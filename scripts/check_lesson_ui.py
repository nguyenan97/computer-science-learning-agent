#!/usr/bin/env python3
"""Check every staged EN/VI lesson's reading interactions on desktop and mobile.

This checks the candidate build, not production deployment or semantic correctness.
Downloads advertised with the production prefix are served from the staged build;
their actual downloaded bytes must match its generated ZIP.
"""
import argparse
import asyncio
from functools import partial
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.async_api import async_playwright
from check_lesson_parity import structure
from check_lesson_site import DEPLOYED_BASE, LESSONS, QuietHandler, ROUTES

CONTRAST = """() => {
  const rgb = text => text.match(/[\\d.]+/g).slice(0, 3).map(Number);
  const luminance = color => rgb(color).map(x => {
    x /= 255; return x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4;
  }).reduce((sum, x, i) => sum + x * [.2126, .7152, .0722][i], 0);
  const ratios = [];
  for (const node of document.querySelectorAll('.markdown-section a, .markdown-section code, .markdown-section .token')) {
    if (!node.getClientRects().length) continue;
    let parent = node, background = 'rgb(255, 255, 255)';
    while (parent) {
      const value = getComputedStyle(parent).backgroundColor;
      if (!value.startsWith('rgba') || !value.endsWith(', 0)')) { background = value; break; }
      parent = parent.parentElement;
    }
    const a = luminance(getComputedStyle(node).color), b = luminance(background);
    ratios.push({ratio: (Math.max(a,b) + .05) / (Math.min(a,b) + .05),
                 kind: node.className || node.tagName});
  }
  return ratios;
}"""


async def check(site, base, chromium):
    totals = dict(pages=0, answers=0, code_blocks=0, tables=0, images=0,
                  keyboard_scrolls=0, downloads=0, language_switches=0, neighbor_clicks=0)
    min_contrast = 100
    errors = []
    async with async_playwright() as p:
        options = {'headless': True, 'args': ['--no-sandbox']}
        if chromium: options['executable_path'] = chromium
        browser = await p.chromium.launch(**options)
        for width, height in ((1440, 1000), (390, 844)):
            context = await browser.new_context(viewport={'width': width, 'height': height}, accept_downloads=True)
            # A PR has no production deployment yet. Verify the advertised ZIP's
            # candidate bytes via its real link, without falling back to live Pages.
            async def staged_download(route):
                relative = route.request.url.removeprefix(DEPLOYED_BASE)
                asset = site / relative
                assert asset.is_file() and asset.suffix == '.zip', route.request.url
                await route.fulfill(path=asset, headers={
                    'Content-Type': 'application/zip',
                    'Content-Disposition': f'attachment; filename="{asset.name}"'})
            await context.route(DEPLOYED_BASE + '**/*.zip', staged_download)
            page = await context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            await page.add_init_script("""
                let config;
                Object.defineProperty(window, '$docsify', {
                  get: () => config, set: value => {
                    value.plugins = [...(value.plugins || []), (hook, vm) =>
                      hook.doneEach(() => window.__readyRoute = vm.route.path.split('?')[0])];
                    config = value;
                  }
                });
            """)
            async def ready(route):
                await page.wait_for_function('(route) => window.__readyRoute === route', arg='/' + route)
            for index, language, route in ROUTES:
                await page.goto(base + '#/' + route, wait_until='networkidle')
                await ready(route)
                assert await page.locator('html').get_attribute('lang') == language, route
                article = page.locator('.markdown-section')
                assert await article.locator('h1').count() == 1
                assert await page.title() == (await article.locator('h1').inner_text()).strip()
                details = article.locator('details')
                count = await details.count()
                assert count > 0 and await article.locator('details[open]').count() == 0, route
                for number in range(count):
                    answer = details.nth(number)
                    summary = answer.locator('summary').first
                    await summary.click()
                    assert await answer.evaluate('(node) => node.open')
                    assert await answer.inner_text() != await summary.inner_text()
                    await summary.click()
                    assert not await answer.evaluate('(node) => node.open')
                    # Native details keyboard operation also works independently.
                    if number == 0:
                        await summary.focus(); await page.keyboard.press('Enter')
                        assert await answer.evaluate('(node) => node.open')
                        outline = await summary.evaluate('(node) => getComputedStyle(node).outlineStyle')
                        assert outline != 'none'
                        await page.keyboard.press('Enter')
                        assert not await answer.evaluate('(node) => node.open')
                totals['answers'] += count
                # Inspect every full source and result even when normally collapsed.
                await details.evaluate_all('(nodes) => nodes.forEach(node => node.open = true)')
                await page.wait_for_timeout(50)  # allow native toggle events/layout
                codes = await article.locator('pre > code').all_text_contents()
                expected = [body.strip() for _, body in structure((site/(route+'.md')).read_text())[2]]
                assert [body.strip() for body in codes] == expected, (route, 'rendered fence mismatch')
                totals['code_blocks'] += len(codes)
                totals['tables'] += await article.locator('table').count()
                assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), route
                # Page width alone misses inline literals clipped by their ancestor.
                # Pre/table code deliberately scrolls; prose code must wrap inside
                # the article's content box, including every wrapped fragment.
                clipped = await article.evaluate("""(article) => {
                  const box = article.getBoundingClientRect(), css = getComputedStyle(article);
                  const left = box.left + parseFloat(css.paddingLeft);
                  const right = box.right - parseFloat(css.paddingRight);
                  return [...article.querySelectorAll('code')].filter(node => {
                    if (node.closest('pre, table')) return false;
                    // pre-wrap may legally hang trailing spaces and decorations
                    // over a line edge. Check visible text tokens, not that padding.
                    const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
                    let text;
                    while ((text = walker.nextNode())) {
                      for (const token of text.data.matchAll(/\\S+/g)) {
                        const range = document.createRange();
                        range.setStart(text, token.index);
                        range.setEnd(text, token.index + token[0].length);
                        if ([...range.getClientRects()].some(rect => rect.width &&
                            (rect.left < left - 1 || rect.right > right + 1))) return true;
                      }
                    }
                    return false;
                  }).map(node => node.textContent);
                }""")
                assert not clipped, (route, 'clipped inline code', clipped)
                scrollables = article.locator('table, pre')
                for number in range(await scrollables.count()):
                    node = scrollables.nth(number)
                    if await node.evaluate('(node) => node.scrollWidth > node.clientWidth + 1'):
                        assert await node.get_attribute('tabindex') == '0', (route, number)
                        assert await node.get_attribute('aria-label')
                        await node.focus()
                        await node.evaluate('(node) => node.scrollLeft = 0')
                        await page.keyboard.press('ArrowRight')
                        await page.wait_for_timeout(80)
                        assert await node.evaluate('(node) => node.scrollLeft > 0'), (route, number)
                        totals['keyboard_scrolls'] += 1
                contrast = await page.evaluate(CONTRAST)
                assert contrast
                minimum = min(contrast, key=lambda item: item['ratio'])
                assert minimum['ratio'] >= 4.5, (route, minimum)
                min_contrast = min(min_contrast, minimum['ratio'])
                for image in await article.locator('img').all():
                    assert await image.get_attribute('alt')
                    assert await image.evaluate('(node) => node.complete && node.naturalWidth > 0')
                    totals['images'] += 1
                for lab in LESSONS[index].get('labs', []):
                    archive = lab.get('archive')
                    if not archive: continue
                    link = article.locator(f'a[href="{DEPLOYED_BASE}{archive}"]').first
                    # The original :target opens a new tab. Download in the current
                    # tab for a deterministic Playwright download listener.
                    await link.evaluate('(node) => node.removeAttribute("target")')
                    async with page.expect_download() as download_info:
                        await link.click()
                    download = await download_info.value
                    assert not await download.failure()
                    downloaded = Path(await download.path())
                    assert downloaded.read_bytes() == (site/archive).read_bytes(), archive
                    totals['downloads'] += 1
                # Exercise actual language and neighbor links after reading interactions.
                switch = 'English' if language == 'vi' else 'Tiếng Việt'
                await article.locator('a').filter(has_text=switch).first.click()
                other = ('en' if language == 'vi' else 'vi')
                other_route = next(r for i, lang, r in ROUTES if i == index and lang == other)
                await ready(other_route)
                assert await page.locator('html').get_attribute('lang') == other
                totals['language_switches'] += 1
                forward = index < len(LESSONS)-1
                label = ('Bài sau:' if forward else 'Bài trước:') if other=='vi' else ('Next:' if forward else 'Previous:')
                await article.locator('a').filter(has_text=label).click()
                neighbor = index+1 if forward else index-1
                await ready(next(r for i, lang, r in ROUTES if i == neighbor and lang == other))
                totals['neighbor_clicks'] += 1
                totals['pages'] += 1
            await context.close()
        assert not errors, errors
        await browser.close()
    print(json.dumps({**totals, 'viewports': [1440, 390], 'minimum_text_contrast': round(min_contrast, 3),
                      'runtime_errors': errors, 'scope': 'staged candidate; downloads mapped to staged ZIP bytes'}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, required=True)
    parser.add_argument('--chromium-path')
    args = parser.parse_args()
    site = args.site.resolve()
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(site.parent)))
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        asyncio.run(check(site, f'http://127.0.0.1:{server.server_port}/{site.name}/', args.chromium_path))
    finally:
        server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__': main()

#!/usr/bin/env python3
"""Exercise published lesson navigation and asset links in Chromium, locally or live."""
import argparse
import asyncio
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import urlsplit
import urllib.error
import urllib.request

from playwright.async_api import async_playwright
from add_lesson_navigation import page_path

DEPLOYED_BASE = 'https://nguyenan97.github.io/computer-science-learning-agent/'
ROOT = Path(__file__).resolve().parents[1]
LESSONS = json.loads((ROOT/'lessons/catalog.json').read_text(encoding='utf-8'))['lessons']
ROUTES = [(index, lang, page_path(entry, lang).as_posix()[:-3])
          for index, entry in enumerate(LESSONS) for lang in ('en', 'vi')]


def fetch(url):
    # urllib uses configured proxy/CA trust. Keep TLS verification enabled even on
    # cloud hosts where Chromium does not share the Python/system CA store.
    try:
        response=urllib.request.urlopen(url,timeout=40)
    except urllib.error.HTTPError as error:
        response=error
    with response:
        return response.status, dict(response.headers), response.read()


async def check(base, chromium, document_delay_ms=0):
    async with async_playwright() as p:
        options={'headless':True,'args':['--no-sandbox']}
        if chromium: options['executable_path']=chromium
        browser=await p.chromium.launch(**options)
        page=await browser.new_page()
        # Hash navigation can finish before Docsify replaces the old document.
        # Its doneEach hook identifies the route whose content is actually ready.
        await page.add_init_script("""
            let docsifyConfig;
            Object.defineProperty(window, '$docsify', {
                configurable: true,
                get: () => docsifyConfig,
                set: (config) => {
                    const ready = (hook, vm) => hook.doneEach(() => {
                        window.__docsifyRenderedRoute = vm.route.path.split('?')[0];
                    });
                    config.plugins = [...(config.plugins || []), ready];
                    docsifyConfig = config;
                }
            });
        """)

        async def verified_https(route):
            status,headers,body=await asyncio.to_thread(fetch,route.request.url)
            headers={k:v for k,v in headers.items() if k.lower() not in ('content-encoding','transfer-encoding','content-length')}
            await route.fulfill(status=status,headers=headers,body=body)
        await page.route('https://**/*',verified_https)
        if document_delay_ms:
            async def delayed_document(route):
                await asyncio.sleep(document_delay_ms / 1000)
                await route.fallback()
            await page.route('**/labs/cost-model/dotnet/README*.md', delayed_document)

        assets=set(); documents=set(); language_switches=0; neighbor_links=0
        runtime_errors=[]
        page.on('pageerror', lambda error: runtime_errors.append(str(error)))
        async def wait_for_document(href):
            route=urlsplit(href).fragment.split('?',1)[0].split('#',1)[0]
            await page.wait_for_function('(route) => window.__docsifyRenderedRoute === route', arg=route)
        async def wait_for_lesson(index, lang):
            await wait_for_document(base+'#/'+page_path(LESSONS[index],lang).as_posix()[:-3])
            prefix=LESSONS[index]['title'][lang].split(' — ',1)[0]
            await page.wait_for_function('(text) => document.querySelector(".markdown-section h1")?.textContent.includes(text)', arg=prefix)
        for index, lang, route in ROUTES:
            await page.goto(base+'#/'+route,wait_until='networkidle')
            await wait_for_lesson(index,lang)
            assert 'Page not found' not in await page.locator('.markdown-section').inner_text()
            related='Nội dung liên quan' if lang=='vi' else 'Related reading'
            await page.locator('.markdown-section h2').filter(has_text=related).wait_for()
            links=await page.locator('.markdown-section a').evaluate_all('(xs)=>xs.map(x=>({href:x.href,text:x.textContent}))')
            for link in links:
                href=link['href']
                if href.startswith(base+'#/'):
                    assert '/..' not in href, href
                    target=urlsplit(href).fragment.split('?',1)[0].split('#',1)[0].lstrip('/')
                    assert not target.endswith(('.py','.cs','.json','.txt','.zip')), href
                    documents.add(href)
                elif href.startswith(base):
                    assets.add(href)
                elif href.startswith(DEPLOYED_BASE) and not urlsplit(href).fragment:
                    # Check the advertised deployment asset against the candidate
                    # build before publication; live mode uses the actual URL.
                    assets.add(base+href.removeprefix(DEPLOYED_BASE))

            # Exercise the actual bottom previous/next link, preserving language.
            if len(LESSONS)>1:
                forward=index<len(LESSONS)-1
                target_index=index+1 if forward else index-1
                label=('Bài sau:' if forward else 'Bài trước:') if lang=='vi' else ('Next:' if forward else 'Previous:')
                neighbor=page.locator('.markdown-section a').filter(has_text=label)
                assert await neighbor.count()==1, (route,label)
                expected=base+'#/'+page_path(LESSONS[target_index],lang).as_posix()[:-3]
                assert await neighbor.evaluate('(a)=>a.href')==expected
                await neighbor.click()
                await wait_for_lesson(target_index,lang)
                neighbor_links+=1
                await page.goto(base+'#/'+route,wait_until='networkidle')
                await wait_for_lesson(index,lang)

            switch='English' if lang=='vi' else 'Tiếng Việt'
            await page.locator('.markdown-section a').filter(has_text=switch).first.click()
            await wait_for_lesson(index,'en' if lang=='vi' else 'vi')
            language_switches+=1

        for href in sorted(documents):
            await page.goto(href,wait_until='networkidle')
            await wait_for_document(href)
            content=await page.locator('.markdown-section').inner_text()
            assert content and 'Page not found' not in content, href
            # Optional lab guides expose individual source downloads. Check those
            # assets as well as the complete ZIP linked directly from the lesson.
            for asset in await page.locator('.markdown-section a').evaluate_all('(xs)=>xs.map(x=>x.href)'):
                if asset.startswith(base) and not urlsplit(asset).fragment:
                    assets.add(asset)
                elif asset.startswith(DEPLOYED_BASE) and not urlsplit(asset).fragment:
                    assets.add(base+asset.removeprefix(DEPLOYED_BASE))
        for href in sorted(assets):
            status,_,body=await asyncio.to_thread(fetch,href)
            assert status==200 and body, (href,status)
            assert not body.lstrip().startswith(b'<!DOCTYPE html>'), href
        assert any(href.endswith('dotnet-lab.zip') for href in assets)
        assert any(href.endswith('Deduplication.cs') for href in assets)
        assert not runtime_errors, runtime_errors
        print(json.dumps({'lesson_pages':len(ROUTES),'language_switches':language_switches,
                          'previous_next_clicks':neighbor_links,'runtime_errors':runtime_errors,
                          'internal_document_links':len(documents),'asset_links':len(assets),
                          'tls_verification':True,'document_delay_ms':document_delay_ms,'base':base}))
        await browser.close()


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--site',type=Path)
    group.add_argument('--base-url')
    parser.add_argument('--chromium-path')
    parser.add_argument('--document-delay-ms',type=int,default=0,
                        help='simulate slow optional lab guides to verify render readiness')
    args=parser.parse_args()
    if args.document_delay_ms < 0: parser.error('document delay must be nonnegative')
    if args.base_url:
        asyncio.run(check(args.base_url.rstrip('/')+'/',args.chromium_path,args.document_delay_ms)); return
    # Serve from a subdirectory, matching a GitHub Project Pages deployment.
    site=args.site.resolve()
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(site.parent)))
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    try:
        asyncio.run(check(f'http://127.0.0.1:{server.server_port}/{site.name}/',args.chromium_path,args.document_delay_ms))
    finally:
        server.shutdown();server.server_close();worker.join()


if __name__=='__main__': main()

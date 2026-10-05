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

DEPLOYED_BASE = 'https://nguyenan97.github.io/computer-science-learning-agent/'
ROUTES = ('lessons/2026-10-05-cost-model/lesson', 'vi/lessons/2026-10-05-cost-model/lesson')


def fetch(url):
    # urllib uses configured proxy/CA trust. Keep TLS verification enabled even on
    # cloud hosts where Chromium does not share the Python/system CA store.
    try:
        response=urllib.request.urlopen(url,timeout=40)
    except urllib.error.HTTPError as error:
        response=error
    with response:
        return response.status, dict(response.headers), response.read()


async def check(base, chromium):
    async with async_playwright() as p:
        options={'headless':True,'args':['--no-sandbox']}
        if chromium: options['executable_path']=chromium
        browser=await p.chromium.launch(**options)
        page=await browser.new_page()

        async def verified_https(route):
            status,headers,body=await asyncio.to_thread(fetch,route.request.url)
            headers={k:v for k,v in headers.items() if k.lower() not in ('content-encoding','transfer-encoding','content-length')}
            await route.fulfill(status=status,headers=headers,body=body)
        await page.route('https://**/*',verified_https)

        assets=set(); documents=set(); language_switches=0
        for route in ROUTES:
            await page.goto(base+'#/'+route,wait_until='networkidle')
            await page.locator('.markdown-section h1').wait_for()
            assert 'Page not found' not in await page.locator('.markdown-section').inner_text()
            assert 'C#' in await page.locator('.markdown-section h1').inner_text()
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

            switch='English' if route.startswith('vi/') else 'Tiếng Việt'
            await page.locator('.markdown-section a').filter(has_text=switch).first.click()
            await page.wait_for_function('(text) => document.querySelector(".markdown-section h1")?.textContent.includes(text)',
                                         arg='Lesson 01' if switch=='English' else 'Bài 01')
            language_switches+=1

        for href in sorted(documents):
            await page.goto(href,wait_until='networkidle')
            content=await page.locator('.markdown-section').inner_text()
            assert content and 'Page not found' not in content, href
        for href in sorted(assets):
            status,_,body=await asyncio.to_thread(fetch,href)
            assert status==200 and body, (href,status)
            assert not body.lstrip().startswith(b'<!DOCTYPE html>'), href
        assert any(href.endswith('dotnet-lab.zip') for href in assets)
        assert any(href.endswith('Deduplication.cs') for href in assets)
        print(json.dumps({'lesson_pages':len(ROUTES),'language_switches':language_switches,
                          'internal_document_links':len(documents),'asset_links':len(assets),
                          'tls_verification':True,'base':base}))
        await browser.close()


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--site',type=Path)
    group.add_argument('--base-url')
    parser.add_argument('--chromium-path')
    args=parser.parse_args()
    if args.base_url:
        asyncio.run(check(args.base_url.rstrip('/')+'/',args.chromium_path)); return
    # Serve from a subdirectory, matching a GitHub Project Pages deployment.
    site=args.site.resolve()
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(site.parent)))
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    try:
        asyncio.run(check(f'http://127.0.0.1:{server.server_port}/{site.name}/',args.chromium_path))
    finally:
        server.shutdown();server.server_close();worker.join()


if __name__=='__main__': main()

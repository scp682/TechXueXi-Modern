"""Current public content feeds, with bounded requests and strict JSON parsing."""
from urllib.parse import urlparse
import json
import os
import subprocess
import requests

ARTICLE_FEEDS = ('1ap1igfgdn2', '1jscb6pu1n2')
VIDEO_FEEDS = ('1742g60067k', '3o3ufqgl8rsn')


def public_feed(feed):
    if feed not in ARTICLE_FEEDS + VIDEO_FEEDS:
        raise ValueError('未知的公开内容源')
    url = 'https://www.xuexi.cn/lgdata/' + feed + '.json'
    if os.name == 'nt':
        # Python 3.8's old TLS/proxy stack is not compatible with this machine.
        # Use Windows' standard HTTP client for PUBLIC feeds only; no cookies.
        script = ("$ProgressPreference='SilentlyContinue'; $ErrorActionPreference='Stop'; "
                  "[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new(); "
                  "(Invoke-WebRequest -UseBasicParsing -Uri '" + url +
                  "' -TimeoutSec 30).Content")
        result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive',
                                 '-Command', script], capture_output=True,
                                encoding='utf-8', timeout=40,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:
            raise RuntimeError('Windows 公开内容请求失败：' + result.stderr.strip()[:300])
        return json.loads(result.stdout.lstrip('\ufeff'))
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def links_from_feed(rows, video=False, limit=500):
    if not isinstance(rows, list):
        raise ValueError('内容列表不是 JSON 数组')
    rows = sorted((r for r in rows if isinstance(r, dict)),
                  key=lambda r: str(r.get('publishTime', '')), reverse=True)
    links, seen = [], set()
    for row in rows:
        if video and row.get('itemType') not in ('kVideo', 'kPureVideo'):
            continue
        if not video and row.get('itemType') in ('kVideo', 'kPureVideo'):
            continue
        url = row.get('url') or row.get('static_page_url') or ''
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https') or not (
                parsed.hostname == 'xuexi.cn' or
                (parsed.hostname or '').endswith('.xuexi.cn')):
            continue
        url = url.replace('http://', 'https://', 1)
        if url not in seen:
            seen.add(url)
            links.append(url)
        if len(links) >= limit:
            break
    return links


def _get_links(feeds, video=False, browser=None):
    errors = []
    for feed in feeds:
        url = 'https://www.xuexi.cn/lgdata/' + feed + '.json'
        try:
            rows = public_feed(feed)
            links = links_from_feed(rows, video=video)
            if links:
                return links
            errors.append(feed + ': 没有有效内容')
        except (requests.RequestException, ValueError, RuntimeError,
                subprocess.SubprocessError, OSError) as exc:
            errors.append(feed + ': ' + str(exc))
    raise RuntimeError('获取当前内容列表失败：' + '; '.join(errors))


def get_article_links(browser=None):
    return _get_links(ARTICLE_FEEDS, browser=browser)


def get_video_links(browser=None):
    return _get_links(VIDEO_FEEDS, video=True, browser=browser)

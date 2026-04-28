import os
import requests
import re


def get_name(url):
    n = re.sub(r'^https?://', '', url)
    n = re.sub(r'[\\/:*?"<>|]', '_', n)
    n = n.rstrip('_')
    if not n.endswith('.html'):
        n += '.html'
    return n


def cache(func):
    def wrapper(url):
        fn = get_name(url)
        if os.path.exists(fn) and os.path.getsize(fn) > 0:
            print(f"Read from cache: {fn}")
            try:
                with open(fn, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                pass

        print(f"Downloading: {url}")
        return func(url, fn)

    return wrapper


@cache
def dl(url, fn):
    try:
        h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=h)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(r.text)
        print(f"Saved: {fn}")
        return r.text
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    while True:
        u = input("\nInput URL (q to quit): ").strip()
        if u.lower() == 'q':
            break
        if not u:
            continue
        if not u.startswith('http'):
            u = 'https://' + u

        res = dl(u)
        if res:
            print(f"Content Len: {len(res)}")
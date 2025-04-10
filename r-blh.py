import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

def show_banner():
    print("\n" + "=" * 70)
    print("""\
 ______           _______  ___      __   __ 
|    _ |         |  _    ||   |    |  | |  |
|   | ||   ____  | |_|   ||   |    |  |_|  |
|   |_||_ |____| |       ||   |    |       |
|    __  |       |  _   | |   |___ |       |
|   |  | |       | |_|   ||       ||   _   |
|___|  |_|       |_______||_______||__| |__|
""")
    print("                  🔎 A Broken Link Checker")
    print("                   ✍️  by Rivek Raj Tamang (Rivudon)")
    print("=" * 70 + "\n")

def fetch_links(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()
        for link in soup.find_all('a', href=True):
            absolute = urljoin(url, link['href'])
            if absolute.startswith('http'):
                links.add(absolute)
        return links
    except Exception as e:
        print(f"[!] Failed to fetch links from {url} - {e}")
        return []

def check_status(links):
    list_404 = []
    list_4xx = []
    list_3xx = []

    for link in links:
        try:
            r = requests.get(link, timeout=10, allow_redirects=False)
            code = r.status_code

            if code == 404:
                list_404.append(link)
            elif code == 403 or (400 <= code < 500):
                list_4xx.append(f"{link} [{code}]")
            elif 300 <= code < 400:
                redirect_url = r.headers.get('Location')
                if redirect_url:
                    try:
                        final = requests.get(redirect_url, timeout=10, allow_redirects=True)
                        final_text = final.text.lower()
                        if "404" in final_text or "not found" in final_text or "this page isn’t available" in final_text:
                            list_404.append(f"{link} ➜ {redirect_url} [Redirect leads to 404]")
                        else:
                            list_3xx.append(f"{link} ➜ {redirect_url} [{code}]")
                    except Exception:
                        list_4xx.append(f"{link} ➜ {redirect_url} [Broken redirect]")
                else:
                    list_3xx.append(f"{link} [{code}]")
        except requests.exceptions.RequestException:
            continue

    return list_404, list_4xx, list_3xx

def main():
    show_banner()

    if len(sys.argv) != 2:
        print("Usage: python3 r-blh.py <https://target.com>")
        sys.exit(1)

    target = sys.argv[1]
    print(f"[*] Collecting links from: {target}")
    links = fetch_links(target)

    print(f"[*] Checking {len(links)} links...")
    not_found, client_errors, redirects = check_status(links)

    print("\n🔎 404 Not Found:")
    for l in not_found:
        print(f" - {l}")

    print("\n🚫 Other 4xx (Forbidden, Bad Request, etc):")
    for l in client_errors:
        print(f" - {l}")

    print("\n↪️ 3xx Redirects:")
    for l in redirects:
        print(f" - {l}")

if __name__ == '__main__':
    main()

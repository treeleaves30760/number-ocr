import requests
import os
import time
import random
from bs4 import BeautifulSoup

# List of different user agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
]

# List of different accept languages
ACCEPT_LANGUAGES = [
    'en-US,en;q=0.9',
    'en-GB,en;q=0.8',
    'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
]

def get_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': random.choice(ACCEPT_LANGUAGES),
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

def get_session():
    session = requests.Session()
    session.headers.update(get_random_headers())
    return session

def get_auth_img_url(session):
    main_url = "https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/"
    response = session.get(main_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the img tag with src containing 'auth_img.php'
    auth_img = soup.find('img', src=lambda x: x and 'auth_img.php' in x)
    
    if auth_img and 'src' in auth_img.attrs:
        return f"https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/{auth_img['src']}"
    else:
        raise Exception("Could not find auth_img URL")

def download_image(session, url, save_path):
    response = session.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded: {save_path}")
    else:
        print(f"Failed to download: {url}")

def main():
    output_dir = "images"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    while True:
        session = get_session()
        try:
            auth_img_base_url = get_auth_img_url(session)
            print(f"Found auth_img base URL: {auth_img_base_url}")
            download_image(session, auth_img_base_url, f"{output_dir}/image_{int(time.time())}.png")
            time.sleep(random.uniform(1, 3))
        
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
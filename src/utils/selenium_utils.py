import os
import re
import hashlib
from dotenv import load_dotenv
# import undetected_chromedriver.v2 as uc
from selenium.webdriver.chrome.options import Options
from selenium import webdriver 
import requests
import json

def get_driver(headless=False):

    # options = webdriver.ChromeOptions()
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument('--no-sandbox')
    options.add_argument('--no-verify')
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-dev-shm-usage")

    # options.add_argument('-no-proxy-server')
    # option=r"D:\download\FirefoxPortable\FirefoxPortable.exe"
    # options.add_argument("-no-remote")
    # options.add_argument("--disable-web-security")
    # options.add_argument("-no-proxy-server")

    try:
        new_proxy = requests.post('https://tmproxy.com/api/proxy/get-current-proxy',json={'api_key':'bc0d7f3df8b707e42db3d0382022298c'})
        if new_proxy.status_code != 200:
            print(f'status code:{new_proxy.status_code}')
        # return driver
        PROXY = json.loads(new_proxy.content.decode())['data']['https']
    except:
        print('connection error')

    if headless:
        options.headless = True

    options.add_argument('--proxy-server=%s' % PROXY) 

    driver = webdriver.Chrome(options=options)
    # driver.proxy = {'https':f'https://{PROXY}',
    #                 'http':f'http://{PROXY}'}


    return driver

def reset_driver_proxy(driver):
    try:
        new_proxy = requests.post('https://tmproxy.com/api/proxy/get-new-proxy',json={'api_key':'bc0d7f3df8b707e42db3d0382022298c'})
    except:
        print('connection error')
        return driver
    if new_proxy.status_code != 200:
        print(f'status code:{new_proxy.status_code}')
        return driver
    
    PROXY = json.loads(new_proxy.content.decode())['data']['https']
    print(PROXY)
    if PROXY == '':
        print('no proxy yet')
        return driver 
    driver.quit()

    options = webdriver.ChromeOptions()
    # options.proxy = {
    #     'httpProxy':PROXY
    # }
    options.add_argument('--proxy-server=%s' % PROXY) 

    options.add_argument("--start-maximized")
    options.add_argument('--no-sandbox')
    options.add_argument('--no-verify')
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-dev-shm-usage")

    # options.add_argument('-no-proxy-server')
    # if headless:
    #     options.headless = True
    driver = webdriver.Chrome(options=options)


    return driver


def filter_duplicated_link(origin_links):
    links = []
    for i in origin_links:
        if not i in links:
            links.append(i)

    return links


def clean(string):
    CLEAN = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    string = re.sub(CLEAN, '', string)
    return re.sub('\s+', ' ', string).strip()


def hashing(string):
    return str(hashlib.sha1(string.encode("utf-8")).hexdigest())
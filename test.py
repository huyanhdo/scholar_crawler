import requests
from src.utils.selenium_utils import get_driver
import time
from tqdm import tqdm
from selenium import webdriver
import json

def reset_driver_proxy(driver):
    try:
        new_proxy = requests.post('https://tmproxy.com/api/proxy/get-new-proxy',json={'api_key':'56e087a47c7748d068052b77174c09ac'})
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
    # options.add_argument('--proxy-server=%s' % PROXY)
    options.proxy = {
        'httpProxy':PROXY
    } 
    options.add_argument("--start-maximized")
    options.add_argument('--no-sandbox')
    options.add_argument('--no-verify')
    # if headless:
    #     options.headless = True
    driver = webdriver.Chrome(options=options)

    return driver

driver = get_driver()
print(dir(driver))
print(driver.caps[''])
# print(id(driver))
# for i in tqdm(range(1000)):
#     driver = reset_driver_proxy(driver=driver)
#     print(id(driver))
#     time.sleep(10)


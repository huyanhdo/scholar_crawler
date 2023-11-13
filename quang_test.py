from selenium import webdriver
from selenium.webdriver.chrome.options import Options


options = Options()
# options = webdriver.ChromeOptions()
# options.binary_location=r"D:\download\FirefoxPortable\App\Firefox64\firefox.exe"
# options.add_argument("-no-remote")
# options.add_argument("--disable-web-security")
# options.add_argument("-no-proxy-server")
 

# driver.proxy = {
#         'http':'http://171.252.22.234:4593',
#         'https':'https://171.252.22.234:4593'}
# print('alo')
# driver.proxy = {
#         'http':'http://27.78.193.34:25755',
#         'https':'https://27.78.193.34:25755'}
# driver.get('https://whatismyipaddress.com/')
# driver = webdriver.Chrome(options=options)

# print('alo')
# driver.get('https://whatismyipaddress.com/')
# driver.quit()
options.add_argument('--proxy-server=%s'%'171.232.91.169:13975')
driver = webdriver.Chrome(options=options)
driver.get('https://whatismyipaddress.com/')
print('alo')

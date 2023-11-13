from utils import request_get_with_scraper

body = request_get_with_scraper('https://scholar.google.com/citations?hl=vi&user=M_GMPswAAAAJ')
# print(body)
with open('html.html','r',encoding='utf8') as f:
    a = f.read()
print(a)
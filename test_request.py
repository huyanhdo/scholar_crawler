import requests

url = "https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=label:robotics+^%^2B+Nguyen"

payload={}
# headers = {
#   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
#   'Accept-Language': 'en-US,en;q=0.5',
#   'Accept-Encoding': 'gzip, deflate, br',
#   'Alt-Used': 'scholar.google.com',
#   'Connection': 'keep-alive',
# #   'Cookie': 'SID=bQhLlVZY-MhJN_KRr7H85h7ZjZAk897Cppj2M7yl0iU2LQ22UWx2kkxmYgM8pTe_mB37CA.; __Secure-1PSID=bQhLlVZY-MhJN_KRr7H85h7ZjZAk897Cppj2M7yl0iU2LQ22G0KTS63aBz9axTv_Um5gpg.; __Secure-3PSID=bQhLlVZY-MhJN_KRr7H85h7ZjZAk897Cppj2M7yl0iU2LQ225p7ZipuNTgJGXh27a1d-tw.; HSID=A2biym7r1eimYC4nC; SSID=A0i32qEs_gzf5VY8b; APISID=ExKDLIWw5oIXzyBJ/AxEsLo4XFxrlM-HGT; SAPISID=qE6IcCBwbkD5_d3_/Adob_3ZI8-a22r9hP; __Secure-1PAPISID=qE6IcCBwbkD5_d3_/Adob_3ZI8-a22r9hP; __Secure-3PAPISID=qE6IcCBwbkD5_d3_/Adob_3ZI8-a22r9hP; SEARCH_SAMESITE=CgQIqZkB; AEC=Ackid1QU1wbAJkInEcAOAjuJXxqNphuYm93fDEoI-gyhqZ4nyhs3fSprvdI; GSP=LM=1697010304:S=a3ZaQ1BGHwX-GZy9; NID=511=vTwZXOwkOFwuA7GIRMHuufrO0ylCafh9So9t9VwSbKygCmqQBtbMsIsRNGv8vFaTt8XIPqF7OneKIUtUqLMJSDdukp_hkwj7V9okRlH4S8RZUsJDh_F-JbIvChWb3pgbs7Ui0cbGMQmuiTB8Cav_h4Ous4461t_XTRJwSI5w-3paa50SG7-pNRcpfBQGe6ZqG4ufuXgHWSMaKMIyVUQiKKnNT8_CS_CbeMHFVMHZKddd0gViXV4XaYWUjQz_bqzA_egtSOaWU5rj8be9azY-XpBLWHGpgfE1Q9QY9R9N1Lh63wImKXsf8KJubl8; 1P_JAR=2023-10-11-10; SIDCC=ACA-OxOOfTPDkEjLGcENGPhgtZxc9NZvRf1fYSrztaW_h7EickIbmQebRAzor4PTI1UOcUmenaU; __Secure-1PSIDCC=ACA-OxPGYPp3kPcQICIcVcd99j8HDnUih2UEAwfEztAzgLnedwTzvBQWevv9k_IiC8KSKrOfQA4; __Secure-3PSIDCC=ACA-OxNWjs0jIYO2E9dqxkbirb72gxnCmofD_SzXIxwDASZNI-KYIqQoneOaqK9L-Z4M8uqLuPU',
#   'Upgrade-Insecure-Requests': '1',
#   'Sec-Fetch-Dest': 'document',
#   'Sec-Fetch-Mode': 'navigate',
#   'Sec-Fetch-Site': 'cross-site',
#   'TE': 'trailers'
# }

proxies = {
    'https':'116.96.236.217:4951'
}

response = requests.get(url)

print(response.text)

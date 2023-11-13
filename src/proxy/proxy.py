import requests
API_KEY = 'f4503e51631b94bf1fd25730145cbc92'
path = 'https://tmproxy.com/api/proxy'
def get_proxy():
    return requests.post(f'{path}/get-currrent-proxy',json={'api_key':API_KEY})

if __name__ == '__main__':
    print(get_proxy().json())   
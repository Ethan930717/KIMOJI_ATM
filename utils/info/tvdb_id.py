import requests

def get_tvdb_token():
    api_key = '38e4fa8a-3a0a-4ce0-8873-32934ec2f213'
    url = "https://api4.thetvdb.com/v4/login"
    headers = {"Content-Type": "application/json"}
    payload = {"apikey": api_key}
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("data", {}).get("token")
    except requests.exceptions.SSLError as ssl_err:
        print(f"SSL Error: {ssl_err}")
    except requests.RequestException as req_err:
        print(f"Request Error: {req_err}")
    return None

def search_tvdb(name):
    token = get_tvdb_token()
    if token:
        url = f"https://api4.thetvdb.com/v4/search"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"query": name, "type": "series"}  # 可以是 'series' 或 'movie'
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                results = response.json().get("data", [])
                if results:
                    full_id = results[0].get("id")
                    id_only = full_id.split("-")[-1]  # 分割字符串
                    return id_only
        except requests.exceptions.SSLError as ssl_err:
            print(f"SSL Error: {ssl_err}")
        except requests.RequestException as req_err:
            print(f"Request Error: {req_err}")
    return 0  # 如果遇到错误，返回0

import requests

class RestDB:

    def __init__(self) -> None:
        pass
    
    def fetch_all_items(self):
        url = "https://virtualsync-63c9.restdb.io/rest/virtualsync"

        headers = {
            'content-type': "application/json",
            'x-apikey': "7998f5bbe9751602547c48197347d697354fe",
            'cache-control': "no-cache"
            }
        try:
            print("making Rest Db call")
            response = requests.request("GET", url, headers=headers)

            if response.status_code==200:
                return eval(response.content)
            else:
                return f"Returned Response Code {response.status_code}"
        except Exception as e:
            return f"Returned Exception {e}"    
        

if __name__ == "__main__":
    db_client = RestDB()
    all_items = db_client.fetch_all_items()
    print(all_items)

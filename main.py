import requests
import time

PATH_TO_API_KEY = "~/keys/coingecko.key"

if __name__ == "__main__":
    with open(PATH_TO_API_KEY, "r") as fin:
        api_key = fin.read()
    url = f"https://api.coingecko.com/api/v3/ping?x_cg_demo_api_key={api_key}"
    while True:
        content = requests.get(url).content
        time.sleep(256)


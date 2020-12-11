import requests
import json

url_github = 'http://api.github.com/users/Evenstarr/repos'

response = requests.get(url_github)

try:
    if response.ok:
        try:
            to_file = response.json()
            with open("1.json", "w+", encoding="utf-8") as f:
                json.dump(to_file, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Smth wrong {e}")
    else:
        print("Response not ok")
except Exception as e:
    print(f"Smth wrong {e}")

import requests
import json

# 123

app_key = "F0B65862-3097-4399-8550-C88FEB30F41B"

file_name = "output.json"

# Там много методов, этот показывает доступные упаковки
url = "https://api.dellin.ru/v1/references/services.json"

params = {
   "appkey": app_key,
   "arrivalPoint": "1000000100000160000000000",
   "derivalPoint": "7800000000000000000000000",
   "length": 1,
   "width": 1,
   "height": 1,
   "weight": 1,
   "quantity": 1
}

response = requests.get(url, params=params)

try:
    if response.ok:
        try:
            to_file = response.json()
            with open("2.json", "w+", encoding="utf-8") as f:
                json.dump(to_file, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Smth wrong {e}")
    else:
        print("Response not ok")
except Exception as e:
    print(f"Smth wrong {e}")
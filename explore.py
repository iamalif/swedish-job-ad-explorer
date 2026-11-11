import requests
import json

url = "https://jobsearch.api.jobtechdev.se/search"

params = {
    "q": "data",
    "limit": 5,
}

response = requests.get(url, params=params)

print("Status:", response.status_code)

print("Top-level keys:", response.json().keys())

data = response.json()

print("type of positions:", type(data["positions"]))
print("type of hits:", type(data["hits"]))

first_ad = data["hits"][0]

print("type of one ad:", type(first_ad))
print("keys in one ad:", first_ad.keys())

print("headline type:", type(first_ad["headline"]))
print("headline value:", first_ad["headline"])
print()
print("employer type:", type(first_ad["employer"]))
print("employer value:", first_ad["employer"])
print()
print("occupation type:", type(first_ad["occupation"]))
print("occupation value:", first_ad["occupation"])

print()
print("employer name:", first_ad["employer"]["name"])
print("occupation label:", first_ad["occupation"]["label"])

print()
print("workplace address type:", type(first_ad["workplace_address"]))
print("workplace address value:", first_ad["workplace_address"])
print("workplace address municipality:", first_ad["workplace_address"]["municipality"])
print("workplace address region:", first_ad["workplace_address"]["region"])


with open("sample.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saved sample.json")
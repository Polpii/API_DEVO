import requests
import json

BASE = "http://127.0.0.1:5000/"

# print("Write your path: ")
# endpoint = input()

endpoint = "map" #+ "/DVIC"
response = requests.get(BASE + endpoint)
json_data = json.loads(response.text)
print(json_data[0]['name'])
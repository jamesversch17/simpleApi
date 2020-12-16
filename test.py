import requests

BASE = "http://127.0.0.1:5000/"

response = requests.put(BASE + "move/1", { "piece" : "bishop", "start_sq" : "e2", "end_sq" : "e4", "capture" : True})

response = requests.get(BASE + "move/1")
print(response.json())
response = requests.patch(BASE + "move/1", {"piece" : "queen"})
print(response.json())
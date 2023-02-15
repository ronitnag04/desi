import requests 

r = requests.get('http://localhost:80/items')
print(r.text)

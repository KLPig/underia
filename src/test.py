import requests

r = requests.get('https://raw.githubusercontent.com/KLPig/underia/master/docs/data.xml')

print(r.status_code)
print(r.text)
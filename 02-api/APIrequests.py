import requests

base_url = "https://swapi.info/api/"
endpoint = "people/"

response = requests.get(base_url + endpoint)

#Response class

print(f"Response {response.status_code}")

#print(f"Response Data {response.headers}")


#Retrieving text object from the class
data = response.json()


print(data[0]["name"])
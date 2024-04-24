import requests

response= requests.get("http://api.open-notify.org/astros.json")
peopleInSpace=response.json()

print("There are currently\t", peopleInSpace['number'], "people in the space")
print("There names are as follow\n")
for people in peopleInSpace['people']:
    print("Astraunat name:\t", people['name'])



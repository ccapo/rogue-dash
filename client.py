import pathlib
import requests
import json

credPath = "data/credentials.json"
urlReg = "http://localhost:8080/api/register"
urlAuth = "http://localhost:8080/api/authenticate"
urlScore = "http://localhost:8080/api/score"

def upload_score(scorecard):
  file = pathlib.Path(credPath)
  credJSON = {}
  if file.exists():
    with open(credPath) as json_file:
        credJSON = json.load(json_file)
  else:
    try:
      r = requests.post(urlReg)
    except:
      return

    if r.status_code != requests.codes.ok:
      print("Request #1 failed with code: {}".format(r.status_code))
      return

    credJSON = r.json()
    with open(credPath, 'w') as outfile:
      json.dump(credJSON, outfile)

  try:
    r2 = requests.post(urlAuth, data=credJSON)
  except:
    return

  if r2.status_code != requests.codes.ok:
    print("Request #2 failed with code: {}".format(r2.status_code))
    return

  tokenJSON = r2.json()
  headers = {'Authorization': 'Bearer '+tokenJSON['accessToken'], 'Content-Type': 'application/json'}

  try:
    r3 = requests.post(urlScore, headers=headers, data=json.dumps(scorecard))
  except:
    return

  if r3.status_code != requests.codes.ok:
    print("Request #3 failed with code: {}".format(r3.status_code))
    return

  print(r3.json())

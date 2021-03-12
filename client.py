import pathlib
import requests
import json

class Client:
  def __init__(self):
    self.credPath = "data/credentials.json"
    self.urlReg = "http://localhost:8080/api/register"
    self.urlAuth = "http://localhost:8080/api/authenticate"
    self.urlScore = "http://localhost:8080/api/score"

  def upload_score(self, scorecard):
    file = pathlib.Path(self.credPath)
    credJSON = {}
    if file.exists():
      with open(self.credPath) as json_file:
          credJSON = json.load(json_file)
    else:
      try:
        r = requests.post(self.urlReg)
      except:
        return

      if r.status_code != requests.codes.ok:
        print("Request #1 failed with code: {}".format(r.status_code))
        return

      credJSON = r.json()
      with open(self.credPath, 'w') as outfile:
        json.dump(credJSON, outfile)

    try:
      r2 = requests.post(self.urlAuth, data=credJSON)
    except:
      return

    if r2.status_code != requests.codes.ok:
      print("Request #2 failed with code: {}".format(r2.status_code))
      return

    tokenJSON = r2.json()
    headers = {'Authorization': 'Bearer '+tokenJSON['accessToken'], 'Content-Type': 'application/json'}

    try:
      r3 = requests.post(self.urlScore, headers=headers, data=json.dumps(scorecard))
    except:
      return

    if r3.status_code != requests.codes.ok:
      print("Request #3 failed with code: {}".format(r3.status_code))
      return

    print(r3.json())

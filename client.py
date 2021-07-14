import pathlib
import requests
import json

class Record:
  def __init__(self):
    self.name = ''
    self.score = 0
    self.highscore = 0

class Client:
  def __init__(self, host = 'https://rogue-dash.site'):
    self.host = host
    self.credPath = "data/credentials.json"
    self.scorePath = "data/score.json"
    self.urlReg = self.host + "/api/register"
    self.urlAuth = self.host + "/api/authenticate"
    self.urlScore = self.host + "/api/score"
    self.record = Record()

  def upload_score(self, scorecard):
    file = pathlib.Path(self.credPath)
    credJSON = {}
    if file.exists():
      with open(self.credPath) as json_file:
        credJSON = json.load(json_file)
    else:
      try:
        req = requests.post(self.urlReg)
      except:
        return

      if req.status_code != requests.codes.ok:
        print("Registration request failed with code: {}".format(req.status_code))
        return

      credJSON = req.json()
      with open(self.credPath, 'w') as outfile:
        json.dump(credJSON, outfile)

    try:
      req = requests.post(self.urlAuth, data=credJSON)
    except:
      return

    if req.status_code != requests.codes.ok:
      print("Authentication request failed with code: {}".format(req.status_code))
      return

    tokenJSON = req.json()
    headers = {'Authorization': 'Bearer '+tokenJSON['accessToken'], 'Content-Type': 'application/json'}

    try:
      req = requests.post(self.urlScore, headers=headers, data=json.dumps(scorecard))
    except:
      return

    if req.status_code != requests.codes.ok:
      print("Score upload failed with code: {}".format(req.status_code))
      return

    scoreJSON = req.json()
    with open(self.scorePath, 'w') as outfile:
      json.dump(scoreJSON, outfile)

  def read_score(self):
    file = pathlib.Path(self.scorePath)
    scoreJSON = {'name': '', 'score': 0, 'highscore': 0}
    if file.exists():
      with open(self.scorePath) as json_file:
        scoreJSON = json.load(json_file)
    self.record.name = scoreJSON['name']
    self.record.score = scoreJSON['score']
    self.record.highscore = scoreJSON['highscore']

    return self.record

from pprint import pprint

import requests


headers = {"X-Auth-Token": "aTdkHnqPHm6wuTCJrYJkwgkreorTstCery5h-dgPw9z",
          "X-User-Id": "tbC22wqAWbW3wosG8",
          "Content-type": "application/json"}
params = {"msgId": "x5QXCh3ypSFrQX58i"}


url = "https://rocketchat.mts-nn.ru/api/v1/chat.getMessage"


result = requests.get(url=url, params=params, headers=headers)
pprint(result.json()["message"]["reactions"])
import requests
import json
import pandas as pd

pv_url = "https://api.solar.sheffield.ac.uk/pvlive/api/v4/gsp/0"

response = requests.get(pv_url)
content = response.json()
print(content["data"][0][2])

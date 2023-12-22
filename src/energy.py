import requests
import json
import pandas as pd
from config import bmrs_api_key
import xml.etree.ElementTree as ET

# Get carbon intensity
# https://carbonintensity.org.uk/
# https://carbon-intensity.github.io/api-definitions/#get-intensity
c_url = "https://api.carbonintensity.org.uk/intensity"
response = requests.get(c_url)
content = response.json()
carbon_intensity = content["data"][0]["intensity"]["actual"]
carbon_intensity_index = content["data"][0]["intensity"]["index"]
# Get Solar Data
# https://www.solar.sheffield.ac.uk/pvlive/
pv_url = "https://api.solar.sheffield.ac.uk/pvlive/api/v4/gsp/0"
response = requests.get(pv_url)
content = response.json()
solar = content["data"][0][2]

# Get onshore wind
url = "https://national-grid-admin.ckan.io/api/3/action/datastore_search"
params = {"resource_id": "db6c038f-98af-4570-ab60-24d71ebd0ae5"}
response = requests.get(url, params)
content = response.json()
embedded_wind = content["result"]["records"][0]["EMBEDDED_WIND_FORECAST"]

current_generation = (
    "https://downloads.elexonportal.co.uk/fuel/download/latest?key=4le1ovvduygagr7"
)
response = requests.get(current_generation)
xml_response = response.content
root = ET.fromstring(xml_response)


updated_at = root[0].attrib["AT"]

fuel_types = []
consumption = []
for child in root[0]:
    fuel_types.append(child.attrib["TYPE"])
    consumption.append(float(child.attrib["VAL"]))

fuels = pd.Series(fuel_types, name="Fuel Type")
values = pd.Series(consumption, name="Consumption")
imports = [
    "INTFR",
    "INTIRL",
    "INTNED",
    "INTEW",
    "INTNEM",
    "INTELEC",
    "INTIFA2",
    "INTNSL",
    "INTVKL",
]
gas = ["OCGT", "CCGT"]
hydro = ["NPSHYD"]
pumped = ["PS"]

df = pd.DataFrame(data=[consumption], columns=fuels)

df["Imports"] = df[imports].sum(axis=1)
df["Gas"] = df[gas].sum(axis=1)
df["Hydro"] = df[hydro].sum(axis=1)
df["Pumped Storage"] = df[pumped].sum(axis=1)
df["Solar"] = solar
df["WIND"] = df["WIND"] + embedded_wind
drop_columns = imports + gas + hydro + pumped
df.drop(columns=drop_columns, inplace=True)

total2 = df.sum(axis=1)[0]


df_proportion = pd.DataFrame(
    data=[[round(100 * df[col].sum() / total2, 2) for col in df.columns]],
    columns=df.columns,
)

df_all = pd.concat([df, df_proportion], axis=0)
df_t = df_all.transpose()
df_t.columns = ["Amount", "Percentage"]

print(f"Live Fuel Mix {updated_at}:")
print(df_t)
print(f"Total generation is {round(total2/1000,2)} GW")
print(f"Carbon intensity is {carbon_intensity} gCO2/kWh ({carbon_intensity_index})")

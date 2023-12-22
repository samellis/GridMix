import requests
import json
import pandas as pd
from config import bmrs_api_key
import xml.etree.ElementTree as ET

# eso_base_url = "https://api.nationalgrideso.com/api/3/action/"

# https://www.energydashboard.co.uk/data

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
total1 = df.sum(axis=1)[0]

df["Imports"] = df[imports].sum(axis=1)
df["Gas"] = df[gas].sum(axis=1)
df["Hydro"] = df[hydro].sum(axis=1)
df["Pumped Storage"] = df[pumped].sum(axis=1)
df["Solar"] = solar
drop_columns = imports + gas + hydro + pumped
df.drop(columns=drop_columns, inplace=True)

total2 = df.sum(axis=1)[0]


df_proportion = pd.DataFrame(
    data=[[round(100 * df[col].sum() / total1, 2) for col in df.columns]],
    columns=df.columns,
)

df_all = pd.concat([df, df_proportion], axis=0)
df_t = df_all.transpose()
df_t.columns = ["Amount", "Percentage"]

print(f"Live Fuel Mix {updated_at}:")
print(df_t)
print(f"Total generation is {round(total2/1000,2)} GW")
print(f"Carbon intensity is {carbon_intensity} gCO2/kWh ({carbon_intensity_index})")

# from grid.iamkate: Onshore wind turbines in England and Wales (and some in Scotland) are connected to the local distribution network rather than the national transmission network, so their reported power generation is an estimate from National Grid ESO, based on weather conditions and observed transmission network demand.
# offshore wind turbines are connected to transmission network so power gen is measured directly

# missing wind: 18766-14083 = 4683 at 15:08

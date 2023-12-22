import requests
import json
import pandas as pd
from config import bmrs_api_key
import xml.etree.ElementTree as ET

# eso_base_url = "https://api.nationalgrideso.com/api/3/action/"

# https://www.energydashboard.co.uk/data

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
print(updated_at)

fuel_types = []
consumption = []
for child in root[0]:
    fuel_types.append(child.attrib["TYPE"])
    consumption.append(float(child.attrib["VAL"]))

fuels = pd.Series(fuel_types, name="Source")
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
hydro = ["PS", "NPSHYD"]

df = pd.DataFrame(data=[consumption], columns=fuels)
total1 = df.sum(axis=1)[0]
print(df)
print(total1)
df["Imports"] = df[imports].sum(axis=1)
df["Gas"] = df[gas].sum(axis=1)
df["Hydro"] = df[hydro].sum(axis=1)
df["Solar"] = solar
drop_columns = imports + gas + hydro
df.drop(columns=drop_columns, inplace=True)

total2 = df.sum(axis=1)[0]
print(total2)

df_proportion = pd.DataFrame(
    data=[[round(100 * df[col].sum() / total1, 2) for col in df.columns]],
    columns=df.columns,
)
print(f"Total generation: {total2}")
print(df)
print(df_proportion)

# from grid.iamkate: Onshore wind turbines in England and Wales (and some in Scotland) are connected to the local distribution network rather than the national transmission network, so their reported power generation is an estimate from National Grid ESO, based on weather conditions and observed transmission network demand.
# offshore wind turbines are connected to transmission network so power gen is measured directly

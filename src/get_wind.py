import requests
import json

# url = "https://api.nationalgrideso.com/dataset/91c0c70e-0ef5-4116-b6fa-7ad084b5e0e8/resource/db6c038f-98af-4570-ab60-24d71ebd0ae5/download/embedded-forecast.csv"

# url = "https://api.nationalgrideso.com/api/3/action/organization_list"
# url = "https://api.nationalgrideso.com/api/3/action/package_show?id=embedded-wind-and-solar-forecasts"
url = "https://national-grid-admin.ckan.io/api/3/action/datastore_search"
params = {"resource_id": "db6c038f-98af-4570-ab60-24d71ebd0ae5"}
response = requests.get(url, params)
content = response.json()
print(content["result"]["records"][0])
print(content["result"]["records"][1])

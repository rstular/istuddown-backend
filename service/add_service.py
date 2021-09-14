import json
import os
import sys

import pymongo
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = sys.argv[1] if len(sys.argv) > 1 else "config.json"

try:
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    print("[+] Configuration file loaded")

except IOError as err:
    print(str(err))
    exit(1)

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")

# Connect to MongoDB server
client = pymongo.MongoClient(
    config["db_server"].format(
        user=MONGO_USER, pwd=MONGO_PASS, host=MONGO_HOST, port=MONGO_PORT, db=MONGO_DB
    )
)

# Connect to MongoDB database
db = client[MONGO_DB]

# Create MongoDB collection of services
services_collection = db[config["collection_services"]]

service_obj = {}
service_obj["name"] = input("Service name: ")
service_obj["display_name"] = input("Service display name: ")
service_obj["display_url"] = input("Service display URL: ")
service_obj["description"] = input("Service description: ")
service_obj["check_url"] = input("Service check URL: ")
service_obj["order"] = int(input("Service ordering number: "))
service_obj["active"] = input("Service active? [Y/n]: ")

if service_obj["active"][0] == "n" or service_obj["active"][0] == "N":
    service_obj["active"] = 0
else:
    service_obj["active"] = 1


print("Service to be added:")
print(json.dumps(service_obj, indent=4))

decision = input("\nIs this correct? [y/N]: ")
if decision[0] != "y" and decision[0] != "Y":
    print("Aborting")
    exit()

ins_res = services_collection.insert_one(service_obj)

print("[+] Inserted record ID {}".format(str(ins_res.inserted_id)))

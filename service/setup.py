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

    with open("services.json") as f:
        services = json.load(f)["services"]
    print("[+] List of services  loaded")
except IOError as err:
    print(str(err))
    exit(1)

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")

# Connect to MongoDB server
client = pymongo.MongoClient(config["db_server"].format(
    user = MONGO_USER,
    pwd = MONGO_PASS,
    host = MONGO_HOST,
    port = MONGO_PORT,
    db = MONGO_DB
))

# Connect to MongoDB database
db = client[MONGO_DB]

# Create MongoDB collection of services
services_collection = db[config["collection_services"]]
services_collection.drop()

ins_res = services_collection.insert_many(services)

print("[+] Setup complete!")

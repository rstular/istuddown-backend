import os
from datetime import datetime

import pymongo
from dotenv import load_dotenv


def time_since_last_healthcheck(config_obj):

    load_dotenv()

    client = pymongo.MongoClient(
        config_obj["db_server"].format(
            user=os.getenv("MONGO_USER"),
            pwd=os.getenv("MONGO_PASS"),
            db=os.getenv("MONGO_DB"),
            host=os.getenv("MONGO_HOST"),
            port=os.getenv("MONGO_PORT"),
        )
    )

    try:
        client.admin.command("ping")
    except pymongo.errors.ServerSelectionTimeoutError as err:
        return -1

    db = client[os.getenv("MONGO_DB")]
    healthchecks_collection = db[config_obj["collection_healthcheck"]]

    latest_healthcheck_timestamp = (
        healthchecks_collection.find({}, {"timestamp": True})
        .sort([("timestamp", -1)])
        .limit(1)
        .next()
    )

    check_time = datetime.utcfromtimestamp(latest_healthcheck_timestamp["timestamp"])
    current_time = datetime.utcnow()

    delta = current_time - check_time
    return delta

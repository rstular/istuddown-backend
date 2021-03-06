import json
import logging
import logging.handlers
import os
import sys
import time
from enum import IntEnum

import pymongo
import requests
from dotenv import load_dotenv


class ServiceStatus(IntEnum):
    ONLINE = 0
    DEGRADED = 1
    OFFLINE = 2
    UNKNOWN = 3


hc_logger = logging.getLogger("HealthCheck")
hc_logger.setLevel(logging.INFO)


syslog_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
syslog_handler = logging.handlers.SysLogHandler(address="/dev/log")
syslog_handler.setFormatter(syslog_formatter)
syslog_handler.setLevel(logging.DEBUG)
hc_logger.addHandler(syslog_handler)

stdout_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(stdout_formatter)
stdout_handler.setLevel(logging.INFO)
hc_logger.addHandler(stdout_handler)


def perform_healthcheck(config: dict) -> bool:

    load_dotenv()

    hc_logger.info("Initializing healthcheck collector")

    client = pymongo.MongoClient(
        config["db_server"].format(
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
        hc_logger.critical(str(err))
        exit(1)

    hc_logger.debug("Established connection to MongoDB server")

    db = client[os.getenv("MONGO_DB")]

    services_collection = db[config["collection_services"]]
    healthchecks_collection = db[config["collection_healthcheck"]]

    healthcheck_entry = {"timestamp": int(time.time()), "services": []}

    request_headers = {
        "User-Agent": config["operator_info"]["ua"],
        "From": config["operator_info"]["from"]
    }

    for item in services_collection.find().sort("order"):
        if not item["active"]:
            continue

        hc_logger.debug("Performing healthcheck for service {}".format(item["name"]))

        srv_healthcheck = {"service_id": item["_id"]}

        pings = []
        statuses = []

        for i in range(3):

            try:
                r = requests.get(
                    item["check_url"],
                    timeout=config["check_timeout"],
                    allow_redirects=False,
                    verify=False,
                    headers=request_headers,
                )
                pings.append(r.elapsed.total_seconds())
                statuses.append(r.status_code)

            except requests.exceptions.ReadTimeout:
                pass
            except requests.exceptions.ConnectionError:
                pass
            except Exception as err:
                hc_logger.error(
                    "Unknown error ({}) when checking service '{}'".format(
                        err.__class__.__name__, item["name"]
                    )
                )
                hc_logger.error(str(err))

            time.sleep(0.2)

        if len(pings) == 0:
            srv_healthcheck["ping"] = -1
            srv_healthcheck["status"] = ServiceStatus.OFFLINE
        else:
            srv_healthcheck["ping"] = round(sum(pings)/len(pings) * 1000, 3)

        if max(statuses) >= 500 and min(statuses) < 500:
            srv_healthcheck["status"] = ServiceStatus.DEGRADED
        elif max(statuses) >= 500:
            srv_healthcheck["status"] = ServiceStatus.OFFLINE
        elif srv_healthcheck["ping"] >= config["degraded_threshold"]:
            srv_healthcheck["status"] = ServiceStatus.DEGRADED
        else:
            srv_healthcheck["status"] = ServiceStatus.ONLINE

        healthcheck_entry["services"].append(srv_healthcheck)

    healthchecks_collection.insert_one(healthcheck_entry)

    hc_logger.info("Healthcheck completed")

    return True


if __name__ == "__main__":
    hc_logger.info("Healthcheck manually started!")

    CONFIG_FILE = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
    except IOError as err:
        hc_logger.critical(str(err))
        exit(1)

    hc_logger.debug("Loaded configuration file")
    perform_healthcheck(config)

import datetime
import logging
import os
import atexit
from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler

import pytz
from elasticsearch import NotFoundError, TransportError, ConnectionTimeout, ConnectionError, Elasticsearch
from src.elasticsearch.datasets import insert_datasets
from src.utils import StartSchedulerError

ES_HOST = os.getenv('ELASTIC_HOST', 'localhost')
ES_PORT = os.getenv('ELASTIC_PORT', '9200')
es_client = Elasticsearch([ES_HOST + ':' + ES_PORT])
update_interval = 2 * 60 * 60


def schedule_updates(connection_attempts=0):
    if connection_attempts > 4:
        raise StartSchedulerError(hosts=es_client.transport.hosts)
    es_connection_ok = False
    try:
        es_client.cluster.health(wait_for_status="yellow")
        es_connection_ok = True
    except ConnectionError:
        sleep(5)
        schedule_updates(connection_attempts=connection_attempts + 1)
    if es_connection_ok:
        scheduler = BackgroundScheduler()
        sleep(5)
        if not Update.is_running():
            Update.start_update()
            scheduler.add_job(func=Update.start_update, trigger="interval", seconds=update_interval)
            scheduler.start()
            atexit.register(lambda: scheduler.shutdown())
        return True
    else:
        return False


class Update:
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ES_INDEX = "update"

    def __init__(self):
        self.status = Update.IN_PROGRESS
        self.start_time = self.get_local_time()
        self.end_time = None
        self.id = None

    @staticmethod
    def start_update(connection_attempts=0, ignore_previous_updates=False):
        if connection_attempts == 4:
            return
        update = Update()
        try:
            if not ignore_previous_updates:
                jobs_completed_for_intervall = es_client.search(index="updates", body=updates_last_x_minutes_query)
                if jobs_completed_for_intervall["hits"]["total"]["value"] > 0:
                    return False
        except NotFoundError:
            logging.info("Initiating elasticsearch index: update")
            pass
        except (ConnectionError, ConnectionTimeout, TransportError, ConnectionRefusedError):
            logging.warning("start_update in scheduler.py: connection error when attempting to contact elasticsearch")
            sleep(5)
            Update.start_update(connection_attempts + 1)
        result = es_client.index(index="updates", body=update.doc())
        doc_id = result["_id"]
        status = insert_datasets(success_status=Update.COMPLETED, failed_status=Update.FAILED)
        Update.complete_update(doc_id, update, status)

    @staticmethod
    def complete_update(doc_id, update_obj, status):
        update_obj.end_time = Update.get_local_time()
        update_obj.status = status
        try:
            es_client.delete(index="updates", id=doc_id)
            es_client.index(index="updates", body=update_obj.doc())
        except (ConnectionError, ConnectionTimeout, TransportError, ConnectionRefusedError):
            logging.warning("Elasticsearch complete_update: could not write to elasticsearch")

    @staticmethod
    def is_running(connection_attempts=0):
        if connection_attempts == 4:
            return False
        try:
            jobs_in_progress = es_client.search(index="updates", body=in_progress_query)
            return jobs_in_progress["hits"]["total"]["value"] > 0
        except NotFoundError:
            return False
        except (ConnectionError, ConnectionTimeout, TransportError):
            logging.error(f"Connection error checking for jobs in progress. Attempts: {connection_attempts}")
            sleep(5)
            return Update.is_running(connection_attempts + 1)

    def doc(self):
        doc = {
            "status": self.status,
            "start_time": self.start_time
        }
        if self.end_time:
            doc["end_time"] = self.end_time
        return doc

    @staticmethod
    def get_local_time():
        local_tz = pytz.timezone('Europe/Oslo')
        return datetime.datetime.now(tz=local_tz)


in_progress_query = {
    "query": {
        "term": {
            "status.keyword": "in progress"
        }
    }
}
updates_last_x_minutes_query = {
    "query": {
        "bool": {
            "must": [
                {
                    "range": {
                        "end_time": {
                            "time_zone": "+01:00",
                            "gte": f"now-{update_interval}s/s",
                            "lte": "now"
                        }
                    }
                }
            ],
            "must_not": {
                "term": {
                    "status": "failed"
                }
            }
        }
    }
}

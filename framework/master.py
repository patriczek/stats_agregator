import config
import urllib2
import json
import os.path
from datetime import datetime, timedelta


class Master:
    master_bt = []
    created = None  # Time when was generate master json
    master_file = "cache/master.json"

    def __init__(self):
        self.url = config.MASTER

    def load(self):
        if config.CACHE and self.old_cache():
            self.load_cache()
        else:
            self.download_all_hash()
            self.clear_cache()

    def download_all_hash(self):
        """
        Download all json from master server.
        """
        url = self.url + "stats/api/get_hash"
        request = urllib2.Request(url,
                                  headers={"Accept": "application/json"})
        # TODO Send data (os, date interval from - to)
        json_string = urllib2.urlopen(request).read()

        self.parse_hash_from_json(json_string=json_string)

        if config.CACHE:
            self.save_cache()

    def parse_hash_from_json(self, json_string):
        self.master_bt = (json.loads(json_string))
        if 'data' in self.master_bt:
            self.master_bt = self.master_bt['data']
        else:
            self.master_bt = self.master_bt

    def save_cache(self):
        if self.master_bt is not None:
            with open(self.master_file, "w") as f:
                f.write(json.dumps(self.master_bt))

    def load_cache(self):
        if os.path.isfile(self.master_file):
            with open(self.master_file, "r") as f:
                for line in f:
                    self.parse_hash_from_json(line)
        else:
            self.download_all_hash()

    def download_ureport(self):
        from slave import Slave
        # TODO Invent better solution for this!
        json_str = Slave.download_data(self.url, self.master_bt)
        self.master_bt = json.loads(json_str)

        return True

    def old_cache(self, days=0, hours=3, minutes=0):
        """
        If master file is older then parametrized time,
        then delete all cached files.
        By default is set on 3 hours
        """
        if os.path.isfile(self.master_file):
            modify_datetime = datetime.fromtimestamp(
                os.path.getmtime(self.master_file))
            current_datetime = datetime.now()

            result = current_datetime - modify_datetime

            if result.total_seconds() > timedelta(minutes=minutes,
                                                  hours=hours,
                                                  days=days).total_seconds():
                self.clear_cache()

        return True

    @staticmethod
    def clear_cache():
        """
        Delete all cached file
        """
        files = os.listdir("cache")
        for f in files:
            os.unlink("cache/" + f)

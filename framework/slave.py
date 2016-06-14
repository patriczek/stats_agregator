import config
import urllib2
import urllib
import json
import os.path
from pprint import pprint
import sys
from aserver import AServer


class Slave(AServer):

    def __init__(self):
        self.url = config.SLAVE

    def download_ureports(self, master_bt):
        for server_name, server_url in self.url.items():
            # Download from all source

            result = self.get_ureport_by_hash(master_hash=master_bt,
                                              source=server_url)

            parse_json = self.parse_hash_from_json(result)  # TODO REMAKE ??

            self.slave_bt[server_name] = parse_json

            if config.CACHE:
                self.save_cache(server_name + ".json", parse_json)

    def load(self, master_hash):
        if config.CACHE:
            # Load from cache and download only missing source
            self.load_cache(master_hash)
        else:
            for server_name, server_url in self.url.items():
                # Download from all source

                result = self.get_ureport_by_hash(master_hash=master_hash, source=server_url)

                parse_json = self.parse_hash_from_json(result)

                self.slave_bt[server_name] = parse_json

    def get_ureport_by_hash(self, master_hash, source=None):
        json_result = None

        if isinstance(self.url, dict):
            if source is not None:
                json_result = self.download_data(url=source,
                                                 data=master_hash)
        return json_result

    @staticmethod
    def download_data(url,  data):
        problem_url = url + "reports/items/"

        json_data_send = json.dumps(data)

        request = urllib2.Request(problem_url, data=json_data_send,
                                  headers={"Content-Type": "application/json",
                                           "Accept": "application/json"})

        try:
            data = urllib2.urlopen(request)
        except urllib2.URLError as e:
            print "{0} - {1}".format(url, e.reason)
            sys.exit()
        except urllib2.HTTPError as e:
            print "Url {0} return code {1}".format(url, e.code)
            sys.exit()

        json_string = data.read()
        return json_string

    @staticmethod
    def parse_hash_from_json(json_string):
        js = json.loads(json_string)
        return js

    def load_cache(self):
        for server_name, server_url in self.url.items():
            if os.path.isfile("cache/" + server_name + ".json"):
                with open("cache/" + server_name + ".json", "r") as f:
                    for line in f:
                        self.slave_bt[server_name] = self.parse_hash_from_json(line)
                return True
            else:
                return False

    def get_problem_by_bthash(self, problem_bt_hash):
        for s_name, s_url in self.url.items():
            # problem_url = s_url + "/problems/bthash/?" + problem_bt_hash + "&bth=f3f5e5020c0f69f71c66fe33e47d232435c451a0"
            problem_url = s_url + "problems/bthash/?" + problem_bt_hash

            #print problem_url + "\n"
            p_request = urllib2.Request(problem_url, headers={"Accept": "application/json"})

            try:
                problem_request = urllib2.urlopen(p_request)
            except urllib2.HTTPError as e:
                print "While tring download '" + problem_url + "' we get code: " + str(e.code)
                continue
            else:
                problem_string = problem_request.read()

            problem = json.loads(problem_string)

            tmp_list = []
            if "multiple" in problem:
                for p in problem['multiple']:
                    tmp_list.append(p)
            else:
                tmp_list.append(problem)

            self.slave_problem[problem_bt_hash] = tmp_list

    def download_problems(self, master_problem):
        for p in master_problem:
            self.get_problem_by_bthash(p['bt_hash_qs'])

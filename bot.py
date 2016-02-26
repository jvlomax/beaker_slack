from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests

import os
import datetime
from importlib import import_module
from slackclient import SlackClient
import time
from plugins.base import Plugin
import sys

from config import url, user, client_repository_id, server_repository_id, token


class Bot:
    def post_client_reviews(self):
        headers = {"User-Agent": "beaker bot", "Content-Type": "application/json"}
        response = requests.get("{}/api/{}/code_reviews.json?state=pending".format(url, client_repository_id),
                                auth=(user, token), headers=headers)
        print(response)
        print(dir(response))
        if response.status_code == 200:
            reviews = response.json().get("code_reviews", {})

            lines = []
            for review in reviews:
                review_url = "{}/{}/code_reviews/{}".format(url, "project-miner", review["id"])
                lines.append("*{}*: {} {}".format(review["requesting_user"].get("name", "unknown"),
                                                    review.get("description", "No description given"),
                                                    review_url))
        if lines:
            self.sc.api_call("chat.postMessage", channel="#client-code-review", text="Good morning. These are the current pending reviews:")
            self.sc.api_call("chat.postMessage", channel="#client-code-review", text="\n".join(lines))
        else:
            self.sc.api_call("chat.postMessage", channel="#client-code-review", text="Good morning. There are no pending reviews")

    def post_server_reviews(self):
        headers = {"User-Agent": "beaker bot", "Content-Type": "application/json"}
        response = requests.get("{}/api/{}/code_reviews.json?state=pending".format(url, server_repository_id),
                                auth=(user, token), headers=headers)
        print(response)
        print(dir(response))
        if response.status_code == 200:
            reviews = response.json().get("code_reviews", {})

            lines = []
            for review in reviews:
                review_url = "{}/{}/code_reviews/{}".format(url, "project_miner_server", review["id"])
                lines.append("*{}*: {} {}".format(review["requesting_user"].get("name", "unknown"),
                                                    review.get("description", "No description given"),
                                                    review_url))
        if lines:
            self.sc.api_call("chat.postMessage", channel="#client-code-review", text="Good morning. These are the current pending reviews:")
            self.sc.api_call("chat.postMessage", channel="#client-code-review", text="\n".join(lines))
        else:
            self.sc.api_call("chat.postMessage", channel="#client-code-review", text="Good morning. There are no pending reviews")

    def __init__(self, token, name="beaker"):
        self.token = token
        self.name = name
        self.plugins = []

        self.tag = "@"
        self.sc = SlackClient(self.token)
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.post_client_reviews, "cron", day_of_week="mon-fri", hour=11)
        self.scheduler.add_job(self.post_server_reviews, "cron", day_of_week="mon-fro", hour=11)
        self.scheduler.start()

    def get_plugins(self):
        print(os.listdir("plugins"))
        modules = [file for file in os.listdir("plugins") if file.endswith(".py") and file != "base.py" and not file.startswith("__")]
        for module in modules:
            import_module("plugins." + module.split(".")[0])
        for subclass in Plugin.__subclasses__():
            print(subclass.__name__)
            self.plugins.append(subclass())

    def refresh_plugins(self):
        pass

    def connect(self):

        if self.sc.rtm_connect():
            while 1:
                for message in self.sc.rtm_read():
                    if message.get("text") is None:
                        continue
                    if message["text"] == "" or message["text"] is None:
                        continue
                    if float(message["ts"]) < time.time():
                        print("old message, ignoring")
                        continue
                    print(message)
                    try:
                        split = message["text"].split(" ")
                    except KeyError:
                        pass
                    else:
                        if split[0][0] == self.tag:

                            command = split[0][1:]
                            for module in self.plugins:
                                if command in module.commands:
                                    data = module.message_recieved(command, " ".join(split[1:]))
                                    if isinstance(data, str):
                                        data = {"text": data}
                                    self.sc.api_call("chat.postMessage", channel=message["channel"], **data)
                                    break
                            else:
                                data = {}
                                if command == "whatdayisit":
                                    data["text"] = datetime.datetime.now().strftime('%A')
                                elif command == "say":
                                    data["text"] = " ".join(split[1:])
                                elif command == "summon":
                                    self.sc.api_call("chat.delete", channel=message["channel"], ts=message["ts"])
                                    data["text"] = "@" + " @".join(split[1:])
                                    data["username"] = "summoner"
                                    data["image"] = "http://seriousmovielover.com/wordpress/wp-content/uploads/2009/10/python2.jpg"
                                    data["as_user"] = False
                                if data != {}:
                                    self.sc.api_call("chat.postMessage", channel=message["channel"], **data)

    def run(self):
        self.get_plugins()
        print(self.plugins)
        self.connect()

if __name__ == "__main__":

    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        print("else")
        token = os.environ.get("SLACK_API_TOKEN")
    if token is not None:
        bot = Bot(token)
        bot.run()

    else:
        print("Please supply a slack API token either as an arg or as env variable")

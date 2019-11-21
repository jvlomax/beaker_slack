from plugins.base import Plugin
from random import randint
import re
import os
import requests
class Staging(Plugin):
    commands = ["staging"]
    TRELLO_TOKEN = os.environ.get("TRELLO_TOKEN")
    TRELLO_API_KEY = os.environ.get("TRELLO_API_KEY")
    TRELLO_BASE_URL = "https://api.trello.com/1"
    STAGING_1_LIST = "5dd29d04fc42266ea69b525a"
    STAGING_2_LIST = "5dd29d07dc9d8d59e2a7f12d"

    def message_recieved(self, command, message=""):
        action = message.split(" ")[0]
        print(self.TRELLO_TOKEN)
        print(self.TRELLO_API_KEY)
        if action == "live":
            try:
                staging1_live = requests.get('{}/lists/{}/cards'.format(self.TRELLO_BASE_URL, self.STAGING_1_LIST), params={'token': self.TRELLO_TOKEN, 'key': self.TRELLO_API_KEY}).json()[0].get('name', '')
            except IndexError:
                staging1_live = ''
            try:
                staging2_live = requests.get('{}/lists/{}/cards'.format(self.TRELLO_BASE_URL, self.STAGING_2_LIST), params={'token': self.TRELLO_TOKEN, 'key': self.TRELLO_API_KEY}).json()[0].get('name', '')
            except IndexError:
                staging2_live = ''

            return "Staging1: {}\nStaging2: {}".format(staging1_live, staging2_live)
        if action == "clear":
            try:
                server = message.split(" ")[1]
            except Exception:
                return "Please indicate which server slot you want to clear. E.g \"@staging clear 1\""
            else:
                list_to_clear = self.STAGING_1_LIST if int(server) == 1 else self.STAGING_2_LIST
                resp = requests.post("{}/lists/{}/archiveAllCards".format(self.TRELLO_BASE_URL, list_to_clear), params={"token": self.TRELLO_TOKEN, "key": self.TRELLO_API_KEY})
                if resp.status_code == 200:
                    return "Server is now clear"
                else:
                    return "There was an error clearing the list"
        if action == "set":
            server_num = message.split(" ")[1]
            branch_info = " ".join(message.split(" ")[2:])
            list_to_use = self.STAGING_1_LIST if int(server_num) == 1 else self.STAGING_2_LIST
            resp = requests.post("{}/cards".format(self.TRELLO_BASE_URL), params={"token": self.TRELLO_TOKEN, "key": self.TRELLO_API_KEY, "idList": list_to_use, "name": branch_info})
            if resp.status_code == 200:
                return "Successfully set status of staging{} to {}".format(server_num, branch_info)
            else:
                return "Error setting status. Please contact my master and have him fix me"
        return "Unknown command. Please see help for more details."
            
    def help(self):
        return ("See what is currently live on staging. commands:\n"
                "live: See what is currently live on staging.\n"
                "clear _n_: clear the status of server _n_.\n"
                "set _n_ _message_: Set the status of server _n_ to whatever you would like")
     



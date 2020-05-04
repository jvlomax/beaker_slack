import os
from plugins.base import Plugin
import requests


class Circe(Plugin):
    commands = ["circe", "kick"]
    TOKEN = os.environ.get("CIRCLE_CI_TOKEN")

    def message_recieved(self, command, message=""):  # pylint:disable=unused-argument
        if not self.TOKEN:
            return "Please supply a circle-ci API token by setting the CIRCLE_CI_TOKEN env variable"
        print(message)
        if message is None or message == "":
            data = requests.get("https://circleci.com/api/v1.1/recent-builds?circle-token={}&shallow=true&limit=1".format(self.TOKEN)).json()
            revision = data[0].get("vcs_revision")
        else:
            revision = message
        res = requests.post("https://circleci.com/api/v1.1/project/gh/Sponsorcraft/Sponsorcraft-Website/build?circle-token={}&revision={}".format(self.TOKEN, revision))
        if res.status_code == 200:
            return "Build succesfully kicked"
        else:
            return "Error starting build"

    def help(self):
        return "Restart a circle build. If no revision is given as an arument, it will restart the last build"

    def __str__(self):
        return "circle ci kicker"

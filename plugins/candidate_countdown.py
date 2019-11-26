import os
from time import time
from datadog import initialize, api
from slackclient import SlackClient

from plugins.base import Plugin


class CandidateCountdown(Plugin):
    commands = ["countdown"]
    DATADOG_API_KEY = os.environ.get("DATADOG_API_KEY", None)
    DATADOG_APPLICATION_KEY = os.environ.get("DATADOG_APPLICATION_KEY", None)
    CRON = "00 12 * * *"
    CRON_CHANNELS = ["#general"]

    def message_recieved(self, command, message=""):    # pylint:disable=unused-argument
        if not self.DATADOG_API_KEY:
            return "Please set the DATADOG_API_KEY env variable"
        if not self.DATADOG_APPLICATION_KEY:
            return "Please set the DATADOG_APPLICATION_KEY env variable"
        initialize(api_key=self.DATADOG_API_KEY, app_key=self.DATADOG_APPLICATION_KEY)
        current_num_candidates = api.Metric.query(
            start=time()-100,
            end=time(),
            query="postgresql.custom.player_count{*}by{eu-postgres-red}"
        )['series'][0]['pointlist'][-1][1]
        remaining_number_of_players = 1000000 - current_num_candidates
        if remaining_number_of_players >= 0:
            return "We are currently {} candidates away from 1 Million".format(int(remaining_number_of_players))
        else:
            return ":tada: Congratulation, you have reach 1 Million candidates :tada:"

    @classmethod
    def cron(cls):
        if not cls.DATADOG_API_KEY:
            print("Please set the DATADOG_API_KEY env variable")
        if not cls.DATADOG_APPLICATION_KEY:
            print("Please set the DATADOG_APPLICATION_KEY env variable")

        initialize(api_key=cls.DATADOG_API_KEY, app_key=cls.DATADOG_APPLICATION_KEY)
        current_num_candidates = api.Metric.query(
            start=time()-100,
            end=time(),
            query="postgresql.custom.player_count{*}by{eu-postgres-red}"
        )['series'][0]['pointlist'][-1][1]
        remaining_number_of_players = 1000000 - current_num_candidates
        client = SlackClient(os.environ.get("SLACK_API_TOKEN"))
        if remaining_number_of_players >= 0:
            for chan in cls.CRON_CHANNELS:
                client.api_call(
                    "chat.postMessage",
                    channel=chan,
                    text="We are currently {} candidates away from 1 Million".format(int(remaining_number_of_players)),
                    username="CountdownBot",
                    as_user=False,
                    icon_url="https://www.dropbox.com/s/tut0r7yomg1f2ok/as-logo.png?dl=1"
                )
        else:
            for chan in cls.CRON_CHANNELS:
                client.api_call(
                    "chat.postMessage",
                    channel=chan,
                    text=":tada: Congratulation, you have reach 1 Million candidates :tada:",
                    username="CountdownBot",
                    as_user=False,
                    icon_url="https://www.dropbox.com/s/tut0r7yomg1f2ok/as-logo.png?dl=1"
                )

    def help(self):
        return "I count candidates"

    def __str__(self):
        return "1 Million Candidate Countdown"


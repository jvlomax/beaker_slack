import requests

from plugins.base import Plugin

token = ""
user = ""
headers = {"User-Agent": "beaker bot", "Content-Type": "application/json"}
url = ""
repository_id = ""


class BeanstalkPlugin(Plugin):
    commands = ["reviews"]

    def message_recieved(self, command, message):
        if command == "reviews":
            response = requests.get("{}/api/{}/code_reviews.json?state=pending".format(url, repository_id),
                                    auth=(user, token), headers=headers)
            print(response)
            print(dir(response))
            if response.status_code == 200:
                reviews = response.json().get("code_reviews", {})
                if len(reviews) < 1:
                    return "No pending reviews"
                lines = []
                for review in reviews:
                    lines.append("*{}*: {}".format(review["requesting_user"].get("name", "unknown"),
                                                 review.get("description", "No description given")))

                return "\n".join(lines)



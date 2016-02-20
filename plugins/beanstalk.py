import requests

from plugins.base import Plugin

from config import url, user, client_repository_id, server_repository_id, token

headers = {"User-Agent": "beaker bot", "Content-Type": "application/json"}

class BeanstalkPlugin(Plugin):
    commands = ["reviews"]

    def message_recieved(self, command, message):
        repo = message.split(" ")[0]
        if repo == "client":
            repository_id = client_repository_id
            client = True
        else:
            repository_id = server_repository_id
            client = False
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
                    review_url = "{}/{}/code_reviews/{}".format(url, "project-miner" if client else "project_mine_server", review["id"])
                    lines.append("*{}*: {} {}".format(review["requesting_user"].get("name", "unknown"),
                                                        review.get("description", "No description given"),
                                                        review_url))

                return "\n".join(lines)



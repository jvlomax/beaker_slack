from plugins.base import Plugin
import requests
import os
import random
TOKEN = os.environ.get("GOOGLE_PLACES_API_TOKEN")
TOKEN = "AIzaSyAhKR8nzhZ_Rwh3yZ15iw5cu1ep13cgspM"


class Lunch(Plugin):
    commands = ["lunch"]
    context = {}

    def message_recieved(self, command, message=""):  # pylint:disable=unused-argument
        if message == "review":
            return self.get_review()
        if not message:
            search = "lunch"
        else:
            search = message
        if TOKEN is None:
            return "Token not set for lunch plugin"
        print(search)
        response = requests.get("https://maps.googleapis.com/maps/api/place/radarsearch/json?location=53.481576, -2.240943&radius=2000&type=cafe|restaurant|meal_takeaway|bar|food&opennow&maxprice=3&keyword={}&key={}".format(search, TOKEN))
        if response.status_code != 200:
            return "Error connecting to api"
        try:
            print(response.json())
            place_id = random.choice(response.json().get("results")).get("place_id")
            if not place_id:
                return "No reuslts found"

            details = requests.get("https://maps.googleapis.com/maps/api/place/details/json?placeid={}&key={}".format(place_id, TOKEN)).json().get("result")

            print("{} results found".format(len(details)))

            name = details["name"]

            link = details.get("url", "")

            address_components = details.get("address_components")[:3]
            address = " ".join(comp["long_name"] for comp in address_components[:2])
            address += "\n{}".format(address_components[2]["long_name"])

            self.context["place_id"] = place_id
            self.context["name"] = name
            self.context["address"] = address
            self.context["url"] = link

            data = {
                "attachments": [
                    {
                        "fallback": "{}\n{}".format(name, address),
                        "color": "#36a64f",
                        "title": name,
                        "title_link": link,
                        "text": address,
                        "fields": [
                            {
                                "title": "Rating",
                                "value": details.get("rating", "Unknown"),
                                "short": True
                            },
                        ]
                    }
                ]
            }

            if details.get("website"):
                data["attachments"][0]["fields"].append({"title": "Website", "value": details.get("website"), "short": True})

            return data
        except Exception as e:
            return "Error parsing data: {}".format(e)

    def get_review(self):
        place_id = self.context.get("place_id")
        if not place_id:
            return "No known context. Please look up a place before looking for reviews"
        details = requests.get(
            "https://maps.googleapis.com/maps/api/place/details/json?placeid={}&key={}".format(place_id,
                                                                                               TOKEN)).json().get("result")

        reviews = details.get("reviews")
        if not reviews:
            return "No reviews found"
        if "current_review" not in self.context:
            self.context["current_review"] = 0
        else:
            self.context["current_review"] = (self.context["current_review"] + 1) % len(reviews)
        return reviews[self.context["current_review"]].get("text", "No review found")

    def help(self):
        return "Returns a random place for lunch in manchester. Reviews can be fetched using the parameter \"review\""

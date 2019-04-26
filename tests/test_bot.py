from bot import Bot


class TestBot:
    def test_instanciate(self):
        bot = Bot(token="test token")
        assert bot

    def test_name(self):
        bot = Bot(name="clarance", token="test token")
        assert bot.name == "clarance"
        bot2 = Bot(name="peter", token="test token")
        assert bot2.name == "peter"


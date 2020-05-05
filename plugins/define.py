from plugins.base import Plugin
import os
import json
import psycopg2


class Define(Plugin):
    commands = ["define"]

    def __init__(self):
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            self.con = psycopg2.connect(database_url, sslmode="require")
            self.cursor = self.con.cursor()
            self.cursor.execute("CREATE TABLE IF NOT EXISTS definitions (id serial PRIMARY KEY, key varchar NOT NULL, definitions text);")
            self.con.commit()

    def message_recieved(self, command, message=""): # pylint:disable=unused-argument
        # Only one token in message, get definition
        if not message:
            items = self.get_all_keys()
            return "The following definitions exist:\n* {}".format("\n* ".join([item.capitalize() for item in items]))
        if len(message.split(" - ")) == 1:
            if message.split(" ")[0] == "clear":
                if self.clear_definitions(" ".join(message.split(" ")[1:])):
                    return "{} cleared".format(" ".join(message.split(" ")[1:]))
                else:
                    return "Could not clear {}".format(" ".join(message.split(" ")[1:]))

            items = self.get_definitions(message.upper())
            print(items)
            if len(items) > 1:
                return "Found {} entries for {}:\n* {}".format(
                    len(items),
                    message,
                    "\n* ".join([item for item in items])
                )
            else:
                return items[0]

        elif len(message.split(" - ")) > 1:
            # create definition
            word = message.split(" - ")[0]
            definition = message.split(" - ")[1]
            self.write_definition(word, definition)
            return message.split(" - ")[0] + " written to dictionary"
        else:
            return "I don't know what you mean"

    def write_definition(self, key, definition):
        with self.con.cursor() as cursor:
            data = [definition]
            print(key)
            cursor.execute("SELECT definitions FROM definitions WHERE key=%s;", (key.upper(), ))
            existing_data = cursor.fetchone()
            if existing_data:
                
                existing_data = json.loads(existing_data[0])
                print(existing_data)
                data += existing_data
                print(data)
                cursor.execute("UPDATE definitions SET definitions=%s WHERE key=%s;", (json.dumps(data), key.upper()))
            else:     
                cursor.execute("INSERT INTO definitions (key, definitions) VALUES (%s, %s);", (key.upper(), json.dumps(data)))
            self.con.commit()
    
    def get_all_keys(self):
        keys = []
        with self.con.cursor() as cursor:
            cursor.execute("SELECT key FROM definitions;")
            rows = cursor.fetchall()
            for row in rows:
                keys.append(row[0])
        return keys
    def get_definitions(self, key):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT definitions FROM definitions WHERE key=%s;", (key.upper(), ))
            res = []
            rows = cursor.fetchall()
            print(rows)
            for row in rows:
                print(row)
                res += json.loads(row[0])
            print(res)

            return res
    def clear_definitions(self, key):
        with self.con.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM definitions WHERE key=%s;", (key.upper(), ))
                self.con.commit()
                return cursor.rowcount
            except Exception:
                return "Item not found"

    def help(self):
        return "* You can look up a definition by just entering the name eg. @define GD\n" \
               "* You can add an entry by entering after the name, seperating with hyphen. eg. @define GD - Giving Day\n" \
               "* You can clear entries by using the clear command, eg. @define clear GD"

    def __str__(self):
        return "Plugin for word definitions"

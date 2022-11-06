import os
from dotenv import load_dotenv
from pushover import Pushover as pusho
class Pulse:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        load_dotenv()
        api_key = os.getenv("PUSHOVER_API_KEY")
        user_key = os.getenv("PUSHOVER_USER_KEY")
        print(api_key)
        self.po = pusho(api_key)
        self.po.user(user_key)

    def send_notification(self, notification: str, list_title: str = '', notification_type: str = 'watchlist') -> None:
        msg = self.po.msg(notification)
        titles = {'watchlist': f"{list_title.upper()} STOCK CHECK", 'ooslist': "OOS STOCK ALERT",
                  'livelist': "LIVE TITLE ALERT"}
        msg.set("title", titles[notification_type])
        msg.set("html", 1)
        self.po.send(msg)

    def initiate_message(self):
        message = []
        self.message_line(message, line_type='message_header')
        message.append(f'<b>{datetime.datetime.now().strftime("%d-%B-%Y %H:%M:%S")}</b>')
        self.message_line(message, line_type='message_header')

        return message

    def message_line(self, message, line_type=None):
        line_types = {"message_header": "==============================",
                      "comic_seperator": "----------------------------------"}
        message.append(line_types[line_type])
        return message
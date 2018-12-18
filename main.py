import json # JSON lib
import requests # HTTP lib
import os # used to access env variables
import time
import urllib.parse # lib that deals with urls
from dbhelper import * # imports all user-defined functions to

TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}/".format(TOKEN)

# groups based on tolerance level:
# 8 groups for RC4 Angel Mortal games: AM1, AM2, AM3, AM4, AM5, AM6, AM7, AM8
# index to the left: ANGEL | index to the right: MORTAL
AM = ["1234", "9583", "5635"]
AM2 = []
AM3 = []
AM4 = []


# using the admin id would allow you to send messages to everyone!
ADMIN_ID = os.environ["ADMIN_PASSWORD"]

user_db = userdb()
am_db = onodb()
users = [] # list of users objects
am_participants = [] # list of player chat_ids

# EMOJI UNICODE
CAKE = u"\U0001F382"
WHALE = u"\U0001F40B"
ROBOT = u"\U0001F916"
SKULL = u"\U0001F480"
SMILEY = u"\U0001F642"
SPOUTING_WHALE = u"\U0001F433"
SPEECH_BUBBLE = u"\U0001F4AC"
THINKING_FACE = u"\U0001F914"

# GREETINGS
ABOUT_THE_BOT = SPOUTING_WHALE + " *About OrcaBot* " + SPOUTING_WHALE + "\n\n" + CAKE + " Birthday: June 2017\n\n" + \
                ROBOT + " Currently maintained by Kang Ming + Zhi Yu :)\n\n" + SKULL +\
                " Past Bot Developers: Bai Chuan, Fiz, Youkuan\n\n"
AM_GREETING = "Hello there, Anonymous! Click or type any of the following:\n" +\
               "/angel: Chat with your Angel\n" +\
               "/mortal: Chat with your Mortal\n" +\
               "/mainmenu: Exits the Chat feature, and return to the Main Menu"
AM_LOGIN_GREETING = "Please enter your 4-digit UserID.\n\n" +\
                     "or click /mainmenu to exit the registration process"
INVALID_PIN = "You have entered the wrong 4-digit number. Please try again, or type /mainmenu to exit."
REDIRECT_GREETING = "Did you mean: /start"
REQUEST_ADMIN_ID = "Please enter your Admin ID to proceed."
SEND_ADMIN_GREETING = "Hello there, Administrator! What do you want to say to everyone?"
SEND_CONNECTION_FAILED = u"Your message has failed to send, because he/she has yet to sign in to the game." +\
                         u" Please be patient and try again soon!" + SMILEY
SUCCESSFUL_ANGEL_CONNECTION = "You have been connected with your Angel." +\
                            " Anything you type here will be sent anonymously to him/her."
SUCCESSFUL_MORTAL_CONNECTION = "You have been connected with your Mortal." +\
                              " Anything you type here will be sent anonymously to him/her."
HELLO_GREETING = "Hello there, {}! Oscar at your service! " + SPOUTING_WHALE
HELP_MESSAGE = "<User guide for bot features>\n\n"
GAME_RULES_MESSAGE = "<Insert games rules>"

# TELEGRAM KEYBOARD OPTIONS
ABOUT_THE_BOT_KEY = u"About the Bot" + " " + SPOUTING_WHALE
ANONYMOUS_CHAT_KEY = u"Angel-Mortal Anonymous Chat" + " " + SPEECH_BUBBLE
HELP_KEY = "Help" + " " + THINKING_FACE
RULES_KEY = "Game Rules"
ANGEL_KEY = u"/angel"
MORTAL_KEY = u"/mortal"
MENU_KEY = u"/mainmenu"
AM_KEYBOARD_OPTIONS = [ANGEL_KEY, MORTAL_KEY, MENU_KEY]
KEYBOARD_OPTIONS = [ANONYMOUS_CHAT_KEY, ABOUT_THE_BOT_KEY, HELP_KEY, RULES_KEY]


# Sends a HTTP GET request using the given url.
# Returns the response in utf8 format
def send_get_request(url):
    response = requests.get(url)
    decoded_response = response.content.decode("utf8")
    return decoded_response


# Converts the HTTP response to a JSON object
# Returns a JSON object that represents the telegram bot api response
def convert_response_to_json(response):
    return json.loads(response)


# Sends a GET request representing a getUpdates() method call to the Telegram BOT API
# and retrieves a JSON object that represents the response, that has an Array of Update objects
# URL used in GET request is appended to make a getUpdates() method call.
# If @param offset is not None, then it is appended to the URL.
def get_updates(offset=None):
    url = BASE_URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    response = send_get_request(url)
    return convert_response_to_json(response)


# Gets the last updated id of the update results
def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


# Gets the text and chat id of the last update
# Returns a tuple containing the text and chat id of the last update
def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return text, chat_id


# Converts a defined range of options for a one-time keyboard, represented by a dictionary, into a JSON string
# Returns a JSON string that represents a dictionary containing the keyboard options
def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


# Converts a defined range of keyboard options represented by a dictionary into a JSON string
# Returns a JSON string that triggers the keyboard removal
def remove_keyboard():
    reply_markup = {"remove_keyboard": True, "selective": True}
    return json.dumps(reply_markup)


# Sends a text in a message to another telegram user, using the telegram sendMessage method
def send_message(text, recipient_chat_id, recipient_name, reply_markup=None):
    try:
        encoded_text = (text.encode("utf8"))
    except:
        pass
    request_text = urllib.parse.quote_plus(encoded_text) # converts url-reserved characters in encoded string
    request_url = BASE_URL + "sendMessage?text={}&chat_id={}".format(request_text, recipient_chat_id)
    if reply_markup:
        request_url += "&reply_markup={}".format(reply_markup)
    send_get_request(request_url)
    print("User: " + recipient_name + "\nReceived message: " + request_text)


# USER PROFILE DECISION MAKING
class User:
    def __init__(self, id):
        self.id = id
        self.angel = 0
        self.mortal = 0

    # Function to open up the main menu with keyboard options.
    def mainmenu(self, text, chat_id, name):
        formatted_hello_greeting = HELLO_GREETING.format(name)
        if text == "/start" or text == "back" or text == "/mainmenu":
            keyboard = build_keyboard(KEYBOARD_OPTIONS)
            send_message(formatted_hello_greeting, chat_id, name, keyboard)

        elif text == ABOUT_THE_BOT_KEY:
            send_message(ABOUT_THE_BOT, chat_id, name)
            keyboard = build_keyboard(KEYBOARD_OPTIONS)
            send_message(formatted_hello_greeting, chat_id, name, keyboard)

        elif text == ANONYMOUS_CHAT_KEY:
            owners = [x[2] for x in am_db.get_four()]
            if chat_id in owners:       # ??? if 4 digit alphanumeric ID is in the list
                send_message(AM_GREETING, chat_id, name, remove_keyboard())
                self.stage = self.anonymous_chat
            else:
                send_message(AM_LOGIN_GREETING, chat_id, name, remove_keyboard())
                self.stage = self.register
        elif text == "/admin":
            send_message(REQUEST_ADMIN_ID, chat_id, name, remove_keyboard())
            self.stage = self.admin_login

        elif text == HELP_KEY:
            send_message(HELP_MESSAGE, chat_id, name, remove_keyboard())

        elif text == RULES_KEY:
            send_message(GAME_RULES_MESSAGE, chat_id, name, remove_keyboard())

        else:
            send_message(REDIRECT_GREETING, chat_id, name, remove_keyboard())

    # A method pointer that is reassigned constantly.
    # Once reassigned to another method with same number of parameters, then the next user input will be directed
    # to the newly reassigned method.
    def stage(self, text, chat_id, name):
        self.mainmenu(text, chat_id, name)

    # Prompts the user for the admin password for login.
    # If valid password, then then admin is allowed to send a message to all users.
    def admin_login(self, text, chat_id, name):
        if text not in ADMIN_ID:
            send_message(INVALID_PIN, chat_id, name, remove_keyboard())
            return
        else:
            send_message(SEND_ADMIN_GREETING, chat_id, name, remove_keyboard())
            self.stage = self.send_all

    # chat_id is required to match the number of parameters in stage()
    # Sends a message to all players.
    def send_all(self, text, chat_id, name):
        list_of_ids = AM + AM2 + AM3 + AM4
        for person_id in list_of_ids:
            owner_data = am_db.get_owner_from_four(person_id)
            recipient_data = owner_data.fetchone()
            # print(recipient_data)
            if recipient_data is not None:
                # print(recipient_data[2])
                am_participants.append(recipient_data[2])
        # print(len(ono_participants))
        for cid in am_participants:  # gets the telegram chat_id each time
            keyboard = build_keyboard(KEYBOARD_OPTIONS)
            send_message("From the Admin:\n" + text, cid, name, keyboard)
        return

    # Registers a user.
    # Verifies the user PIN number first, then registers user in ...
    def register(self, user_pin, chat_id, name):        # text will be the 4 alphanumeric digits
        if user_pin not in AM and user_pin not in AM2 and user_pin not in AM3 and user_pin not in AM4:
            send_message(INVALID_PIN, chat_id, name, remove_keyboard())
            return
        else:
            am_db.register(user_pin, chat_id, name)
            send_message(AM_GREETING, chat_id, name, remove_keyboard())
            self.stage = self.anonymous_chat


    def anonymous_chat(self, text, chat_id, name):
        if text == ANGEL_KEY:
            for x in am_db.get_four_from_owner(chat_id):
                me = x[1]
                break
            if me in AM:
                angel = AM[(AM.index(me) - 1)]
            elif me in AM2:
                angel = AM2[(AM2.index(me) - 1)]
            elif me in AM4:
                angel = AM4[(AM4.index(me) - 1)]
            else:
                angel = AM3[(AM3.index(me) - 1)]
            for x in am_db.get_owner_from_four(angel):
                self.angel = x[2]
                break
            send_message(SUCCESSFUL_ANGEL_CONNECTION, chat_id, name)
            self.stage = self.angelchat
        elif text == MORTAL_KEY:
            for x in am_db.get_four_from_owner(chat_id):
                me = x[1]
                break
            if me in AM:
                mortal = AM[(AM.index(me) + 1)%len(AM)]
            elif me in AM2:
                mortal = AM2[(AM2.index(me) + 1)%len(AM2)]
            elif me in AM4:
                mortal = AM4[(AM4.index(me) + 1)%len(AM4)]
            else:
                mortal = AM3[(AM3.index(me) + 1)%len(AM3)]
            for x in am_db.get_owner_from_four(mortal):
                self.mortal = x[2]
                break
            send_message(SUCCESSFUL_MORTAL_CONNECTION, chat_id, name)
            self.stage = self.mortalchat


    def angelchat(self, text, chat_id, name):
        if self.angel != 0:
            send_message("From your Mortal:\n" + text, self.angel, name)
        else:
            send_message(SEND_CONNECTION_FAILED, chat_id, name)


    def mortalchat(self, text, chat_id, name):
        if self.mortal != 0:
            send_message("From your Angel:\n" + text, self.mortal, name)
        else:
            send_message(SEND_CONNECTION_FAILED, chat_id, name)


# Searches existing user list for a registered user and stages the user
def find_existing_user_then_stage(text, chat_id, name, user_list):
    for registered_user in user_list:  # in the user list
        if chat_id == registered_user.id:  # if there is an existing user
            if text == "/start" or text == "/mainmenu":
                registered_user.stage = registered_user.mainmenu
                registered_user.stage(text, chat_id, name)
            else:
                registered_user.stage(text, chat_id, name)
            break
        else:
            continue


# Initialises a User object, adds it to the global list and the user database
def setup_user_then_stage(text, chat_id, name, user_list):
        new_user = User(chat_id)  # create a new User object
        user_list.append(new_user)  # add new user to the global user list
        user_db.add_user(chat_id, name)  # add user profile to the db
        if text == "/mainmenu":
            new_user.stage = new_user.mainmenu
            new_user.stage(text, chat_id, name)
        else:
            new_user.stage(text, chat_id, name)


def main():
    last_update_id = None # represents offset to be sent in get_updates
    while True:
        updates = get_updates(last_update_id)
        try:
            if len(updates["result"]) > 0:  # accesses the Array object in the JSON response
                for update in updates["result"]:  # iterates through the updates Array
                    if "message" in update and "text" in update["message"]:  # check for text message by user
                            text = update["message"]["text"]  # get message sent by user
                            chat_id = update["message"]["chat"]["id"]  # get user chat id
                            name = update["message"]["from"]["first_name"]  # get user name
                            if chat_id > 0:
                                # todo can use dictionary to improve complexity
                                if chat_id not in [user.id for user in users]:  # new user
                                    setup_user_then_stage(text, chat_id, name, users)
                                else:
                                    find_existing_user_then_stage(text, chat_id, name, users)
                last_update_id = get_last_update_id(updates) + 1
        except KeyError:
            print("I got a KeyError!")
            last_update_id = get_last_update_id(updates) + 1
            pass
        time.sleep(0.5)


if __name__ == '__main__':
    print("Initialised....")
    user_db.setup()
    print("User database set up done.")
    am_db.setup()
    print("AM database set up done.")
    print("Starting main()...")
    main()

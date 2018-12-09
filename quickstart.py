from __future__ import print_function
import datetime
import time
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import telebot
import schedule
import threading

TOKEN ="743001637:AAHLkgNmxnePu1RzeYmHJ5UpmH01FZ9nvJQ"
bot = telebot.TeleBot(TOKEN)

knownUsers= []

commands = {
    "start" : 'Get used to the bot',
    'help' : 'Gives you information about the available commands',
    'schedule' : 'Gives you information about Justus\' schedule today!'
}

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

def get_today():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    tomorrow =  (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat()  + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        timeMax=tomorrow,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events


@bot.message_handler(commands=["start"])
def send_welcome(message):
    cid = message.chat.id
    if cid not in knownUsers:
        knownUsers.append(cid)
        bot.send_message(cid, "**Welcome to Justus' Calendar!** \nHere you will get reminders of your upcoming events for tomorrow! \nAll you have to do is to click start and the reminders will start following in!")
        send_help(message) 
    else:
        bot.send_message(cid, "I already know you, welcome back!")

@bot.message_handler(commands=["help"])
def send_help(message):
    cid = message.chat.id
    help_text = "The following commands are available: \n"
    for key in commands: 
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)

@bot.message_handler(commands= ["schedule"])
def send_schedule(message):
    sch = get_today()
    cid = message.chat.id
    if not sch:
        text = 'No upcoming events found.'
        bot.send_message(cid, text)
    else:
        bot.send_message(cid, "These are your following appointments:")
        for sche in sch:
            if "dateTime" in sche["start"]:
                text = ( "{} at {} ".format(sche["summary"],sche["start"]["dateTime"]))
                bot.send_message(cid, text)
            else:
                text = ("{} at {} ".format(sche["summary"],sche["start"]))
                bot.send_message(cid, text)

def broadcast():
    sch = get_today()
    for cid in knownUsers:
        for sche in sch:
            if "dateTime" in sche["start"]:
                text = ( "{} at {} ".format(sche["summary"],sche["start"]["dateTime"]))
                bot.send_message(cid, text)
            else:
                text = ("{} at {} ".format(sche["summary"],sche["start"]))
                bot.send_message(cid, text)

schedule.every().day.at("8:00").do(broadcast)

def loop1():
    while True:
        try:
            bot.polling()
        except Exception:
            time.sleep(15)
    time.sleep(1)

def loop2():
    while True:
        schedule.run_pending()
        time.sleep(1)

thread1 = threading.Thread(target=loop1)
thread1.start()

thread2 = threading.Thread(target=loop2)
thread2.start()
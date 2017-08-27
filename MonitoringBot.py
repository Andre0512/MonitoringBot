#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib.request import urlopen

import yaml
import subprocess
import shlex
from telegram.ext.dispatcher import run_async, TelegramError
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
import logging
import os
import re
import time

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def custom_str_constructor(loader, node):
    return loader.construct_scalar(node).encode('utf-8')


def get_yml(file):
    result = {}
    with open(os.path.join(os.path.dirname(__file__), file), 'rb') as ymlfile:
        values = yaml.load(ymlfile)
        for k, v in values.items():
            result[k.decode('utf-8')] = dict_byte_to_str(v)
    return result


def dict_byte_to_str(v):
    result = {}
    if hasattr(v, 'items'):
        for key, value in v.items():
            if isinstance(value, bytes):
                value = value.decode('utf-8')
                value = str.replace(value, "\\n", "\n")
            result[key.decode('utf-8')] = value
    else:
        result = v.decode('utf-8')
        result = str.replace(result, "\\n", "\n")
    return result


def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('Help!')


@run_async
def update_processes(key, value):
    bash_file = os.path.join(os.path.dirname(__file__), 'check_process.sh')
    state = subprocess.check_output(shlex.split("bash " + bash_file + " pgrep " + value + " " + key))
    state = state.decode('utf-8')
    if state.split(" ")[0] == "True":
        replace = "✔️"
        extra = " (`" + state.split(" ")[1].rstrip("\n") + "`)"
    else:
        replace = "❌"
        extra = None
    return [replace, extra]


@run_async
def update_fhem(value):
    bash_file = os.path.join(os.path.dirname(__file__), 'check_process.sh')
    state = subprocess.check_output(shlex.split("bash " + bash_file + " fhem " + value))
    replace = "✔️" if re.match(".*is running.*", state.decode('utf-8')) else "❌"
    return replace


@run_async
def update_devices(value, secure=False):
    remote = None if not " " in value else value.split(" ")[1]
    state = ping(value.split(" ")[0], remote=remote, count=5 if secure else 2)
    replace = "✔️" if state else "❌"
    return replace


@run_async
def update_stars(value, key):
    stars, number = get_stars(value, key)
    replace = '_' + "{0:.2f}".format(round(stars, 2)) + '_ ⭐️'
    extra = ' (_' + str(number) + '_)'
    return [replace, extra]


@run_async
def running_updates(val, m_id, bot):
    global msg
    f_dict = cfg[val].copy()
    for key, value in sorted(f_dict.items()):
        extra = None
        if val == 'processes':
            f_dict[key] = update_processes(key, value)
        elif val == 'fhem':
            f_dict[key] = update_fhem(value)
        elif val == 'stars':
            f_dict[key] = update_stars(value, key)
        elif val == 'devices' or val == 'family':
            f_dict[key] = update_devices(value, secure=True if val == 'family' else False)
    for key, value in sorted(f_dict.items()):
        replace = value.result()
        if type(replace) is list:
            replace, extra = replace
        msg[val] = msg[val].replace("❔ *" + key + "*", replace + " *" + key + "*" + (extra if extra else ''))
    bot.edit_message_text(chat_id=m_id.chat.id, message_id=m_id.message_id, text='\n\n'.join(list(msg.values())),
                          parse_mode=ParseMode.MARKDOWN)


def add_category(category):
    key_list = sorted(list(cfg[category]))
    key_list = ["❔ *" + key + "*" for key in key_list]
    msg = "\n".join(key_list)
    return msg


def base_msg(update, bot, msg):
    m_id = update.message.reply_text('\n\n'.join(list(msg.values())), parse_mode=ParseMode.MARKDOWN)
    for value in list(msg):
        running_updates(value, m_id, bot)


def dev(bot, update):
    global msg
    msg = {}
    msg['processes'] = "*Python-Scripts*\n" + add_category('processes')
    msg['fhem'] = "*FHEM*\n" + add_category('fhem')
    msg['devices'] = "*Geräte*\n" + add_category('devices')
    msg['stars'] = "*StoreBot*\n" + add_category('stars')
    base_msg(update, bot, msg)


def wlan(bot, update):
    global msg
    msg = {}
    msg['family'] = "*Familie*\n" + add_category('family')
    msg['devices'] = "*Geräte*\n" + add_category('devices')
    base_msg(update, bot, msg)


def bots(bot, update):
    global msg
    msg = {}
    msg['stars'] = "*StoreBot*\n" + add_category('stars')
    msg['processes'] = "*Python-Scripts*\n" + add_category('processes')
    base_msg(update, bot, msg)


def ping(ip, remote=None, count=2):
    add = ['ssh', remote] if remote else []
    result = subprocess.call(add + ['ping', '-c', str(count), '-W', str(int(count / 2)), ip],
                             stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
    return result == 0


def get_stars(typ, bot):
    url = 'tchannels.me/c' if typ == 'Channel' else 'storebot.me/bot'
    bot = bot.lower()
    response = urlopen('https://' + url + '/' + bot).read().decode('utf-8')
    percent, number = re.findall('@' + bot + '.*\n.*width\:([0-9\.]*)%".*?\(([0-9]*)\)', response)[0]
    stars = float(percent) / 20
    stars = round(stars, 2)
    return stars, number


def restart(bot, update):
    bash_file = os.path.join(os.path.dirname(__file__), 'startup.sh')
    update.message.reply_text('Bot wird neugestartet...')
    subprocess.check_output(shlex.split("bash " + bash_file + " restart"))


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    yaml.add_constructor(u'tag:yaml.org,2002:str', custom_str_constructor)
    global cfg
    cfg = get_yml('./config.yml')

    updater = Updater(cfg['bot']['token'], workers=32)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("dev", dev))
    dp.add_handler(CommandHandler("wlan", wlan))
    dp.add_handler(CommandHandler("restart", restart))
    dp.add_handler(CommandHandler("bots", bots))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, start))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
# !/usr/bin/env python

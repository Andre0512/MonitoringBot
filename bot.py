#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    state = subprocess.check_output(shlex.split("bash check_process.sh pgrep " + value + " " + key))
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
    state = subprocess.check_output(shlex.split("bash check_process.sh fhem " + value))
    replace = "✔️" if re.match(".*is running.*", state.decode('utf-8')) else "❌"
    return replace


@run_async
def update_devices(value):
    remote = None if not " " in value else value.split(" ")[1]
    state = ping(value.split(" ")[0], remote=remote)
    replace = "✔️" if state else "❌"
    return replace


@run_async
def running_updates(object):
    global msg
    f_dict = cfg[object]
    for key, value in sorted(f_dict.items()):
        extra = None
        if object == 'processes':
            replace, extra = update_processes(key, value).result() #ASYNC USELESS
        elif object == 'fhem':
            replace = update_fhem(value).result() #ASYNC USELESS
        elif object == 'devices':
            replace = update_devices(value).result() #ASYNC USELESS
        msg[object] = msg[object].replace("❔ *" + key + "*", replace + " *" + key + "*" + (extra if extra else ''))


def add_category(category):
    key_list = sorted(list(cfg[category]))
    key_list = ["❔ *" + key + "*" for key in key_list]
    msg = "\n".join(key_list)
    return msg


def base_msg(update):
    msg = {} 
    msg['processes'] = "*Python-Scripts*\n" + add_category('processes')
    msg['fhem'] = "*FHEM*\n" + add_category('fhem')
    msg['devices'] = "*Geräte*\n" + add_category('devices')
    m_id = update.message.reply_text('\n\n'.join(list(msg.values())), parse_mode=ParseMode.MARKDOWN)
    return msg, m_id


def echo(bot, update):
    global msg
    msg, m_id = base_msg(update)
    for value in list(msg):
        running_updates(value)
    update_msg(bot, m_id)
    

@run_async
def update_msg(bot, m_id):
    while True:
        text = '\n\n'.join(list(msg.values()))
        try:
            bot.edit_message_text(chat_id=m_id.chat.id, message_id=m_id.message_id, text=text, parse_mode=ParseMode.MARKDOWN)
        except TelegramError:
            pass
        if not '❔' in text:
            break
        time.sleep(1)


def ping(ip, remote=None):
    add = ['ssh', remote] if remote else []
    result = subprocess.call(add + ['ping', '-c', '2', '-W', '1', ip],
        stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
    return result == 0


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():

    yaml.add_constructor(u'tag:yaml.org,2002:str', custom_str_constructor)
    global cfg
    cfg = get_yml('./config.yml')  
    
    updater = Updater(cfg['bot']['token'], workers=32)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import subprocess
import shlex
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
import logging
import os
import re


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


def update_processes(bot, m_id, msg):
    p_dict = cfg['processes']
    for key, value in sorted(p_dict.items()):
        state = subprocess.check_output(shlex.split("bash check_process.sh pgrep " + value + " " + key))
        state = state.decode('utf-8')
        if state.split(" ")[0] == "True":
            msg = msg.replace("❔ *" + key + "*\n", "✔️ *" + key + "* `" + state.split(" ")[1] + "`")
        else:
            msg = msg.replace("❔ *" + key + "*\n", "❌ *" + key + "*\n")
        bot.edit_message_text(chat_id=m_id.chat.id, message_id=m_id.message_id, text=msg, parse_mode=ParseMode.MARKDOWN)
    return msg 


def update_fhem(bot, m_id, msg):
    f_dict = cfg['fhem']
    for key, value in sorted(f_dict.items()):  
        state = subprocess.check_output(shlex.split("bash check_process.sh fhem " + value))
        replace = "✔️" if re.match(".*is running.*", state.decode('utf-8')) else "❌"
        msg = msg.replace("❔ *" + key + "*\n", replace + " *" + key + "*\n")
        bot.edit_message_text(chat_id=m_id.chat.id, message_id=m_id.message_id, text=msg, parse_mode=ParseMode.MARKDOWN)
    return msg 


def update_devices(bot, m_id, msg):
    f_dict = cfg['devices']
    for key, value in sorted(f_dict.items()):
        remote = None if not " " in value else value.split(" ")[1]
        state = ping(value.split(" ")[0], remote=remote)
        replace = "✔️" if state else "❌"
        msg = msg.replace("❔ *" + key + "*\n", replace + " *" + key + "*\n")
        bot.edit_message_text(chat_id=m_id.chat.id, message_id=m_id.message_id, text=msg, parse_mode=ParseMode.MARKDOWN)
    return msg 


def add_category(category, msg):
    key_list = sorted(list(cfg[category]))
    key_list = ["❔ *" + key + "*\n" for key in key_list]
    msg = msg + "".join(key_list)
    return msg


def base_msg(update):
    msg = "*Python-Scripts*\n"
    msg = add_category('processes', msg) + "\n*FHEM*\n"
    msg = add_category('fhem', msg) + "\n*Geräte*\n"
    msg = add_category('devices', msg)
    m_id = update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
    return m_id, msg


def echo(bot, update):
    m_id, msg = base_msg(update)
    msg = update_processes(bot, m_id, msg)
    msg = update_fhem(bot, m_id, msg)
    msg = update_devices(bot, m_id, msg)

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
    
    updater = Updater(cfg['bot']['token'])

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

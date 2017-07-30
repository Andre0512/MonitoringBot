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


def echo(bot, update):
    p_dict = cfg['processes']
    p_list = sorted(list(p_dict.copy()))
    p_list = ["❔ *" + p + "*\n"for p in p_list]
    m_id = update.message.reply_text("".join(p_list), parse_mode=ParseMode.MARKDOWN)
    for key, value in sorted(p_dict.items()):
        state = subprocess.check_output(shlex.split("bash check_process.sh " + key + " " + value))
        state = state.decode('utf-8')
        if state.split(" ")[0] == "True":
            p_list = [p.replace("❔ *" + key + "*\n", "✔️ *" + key + "* `" + state.split(" ")[1] + "`") for p in p_list]
        else:
            p_list = [p.replace("❔ *" + key + "*\n", "❌ *" + key + "*\n") for p in p_list]
        bot.edit_message_text(chat_id=m_id.chat.id, message_id=m_id.message_id, text="".join(p_list), parse_mode=ParseMode.MARKDOWN)

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

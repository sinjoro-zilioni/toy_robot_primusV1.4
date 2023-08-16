#!/usr/bin/env python
import os
import sys
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from telegram.constants import ParseMode
from keys import LOG_CHANNEL, locked_out_reply
from functions.indicator import LOGGER
from functions.key_sys import ag_key_holder


output_text = 'User: {} \n' \
               'Your post has been deleted! .\n' \
               'Forwards from channels are prohibited. \n' \
               'Please contact admins to seek a channel to be approved.'

allowlist_persist  = 'allow_list.txt'

if not os.path.exists(allowlist_persist):
    open(allowlist_persist, 'w').close()

allow_list = [line.rstrip() for line in open(allowlist_persist)]


def persist_update():
    allowlist_file = open(allowlist_persist, 'w')
    allow_list_formatted = map(lambda x: x + '\r', allow_list)
    allowlist_file.writelines(allow_list_formatted)
    allowlist_file.close()

async def allowed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        gear_train = []

        for trigger in range(0, len(allow_list), 250):
            gear_train.append(allow_list[trigger:trigger + 250])

        for gear in gear_train:
            await update.message.reply_text(", @".join(gear))


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ag_key_holder(update.message.from_user.id, update):
        user = update.effective_user.id
        text = "user: {} has added {} to the allowlist."
        allow_list.append(context.args[0])
        persist_update()
        LOGGER.info("user: %s added %s to the allowlist.", user, (context.args[0]))
        await update.message.reply_text('The channel {} is now approved for forwards.'.format(context.args[0]))
        await context.bot.send_message(chat_id=LOG_CHANNEL, text=(text.format(user, str(context.args[0]))), parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(locked_out_reply)

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ag_key_holder(update.message.from_user.id, update):
        user = update.effective_user.id
        text = "user: {} has removed {} from the allowlist."
        allow_list.remove(context.args[0])
        persist_update()
        LOGGER.info("user: %s removed %s from the allowlist.", user, (context.args[0]))
        await update.message.reply_text('The channel {} is no longer approved and is now blocked!'.format(context.args[0]))
        await context.bot.send_message(chat_id=LOG_CHANNEL, text=(text.format(user, str(context.args[0]))), parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(locked_out_reply)


async def forwards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    regulator = [item for item in allow_list if item in update.message.forward_from_chat.username]
    forward = update.message.forward_from_chat
    forward_username = update.message.forward_from_chat.username
    if not any(regulator):
        LOGGER.info("There is a forwarding from the channel: username: %s - key: %s", forward_username, regulator)
        await update.message.reply_text(output_text.format(update.message.from_user.username, str))
        try:
            await update.message.delete()
        except:
            await update.message.reply_text('Unable to eliminate this forwarded message! Has this automaton been granted admin privilege?')
    else:
        LOGGER.info("%s - %s channel is approved.", forward, forward_username)
        pass

add_command = CommandHandler("add", add)
remove_command = CommandHandler("remove", remove)
allowed_command = CommandHandler("allowed", allowed)




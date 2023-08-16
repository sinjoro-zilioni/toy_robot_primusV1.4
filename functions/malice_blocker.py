#!/usr/bin/env python
import os
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from keys import locked_out_reply
from functions.indicator import LOGGER
from functions.key_sys import au_key_holder


output_text = 'User: {} terminated! ☠ \n' \
               '⚖ Termination justified; via automated url blocklist match on: {} \n' \
               '⚔ Vae victis!!'

blocklist_persist  = 'malicious_sites.txt'

if not os.path.exists(blocklist_persist):
    open(blocklist_persist, 'w').close()

block_list = [line.rstrip() for line in open(blocklist_persist)]

def persist_update():
    blocklist_file = open(blocklist_persist, 'w')
    block_list_formatted = map(lambda x: x + '\r', block_list)
    blocklist_file.writelines(block_list_formatted)
    blocklist_file.close()

async def malum_index(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if au_key_holder(update.message.from_user.id, update):

        gear_train = []

        for trigger in range(0, len(block_list), 250):
            gear_train.append(block_list[trigger:trigger + 250])

        for gear in gear_train:
            await update.message.reply_text(str(gear))

    else:
        await update.message.reply_text(locked_out_reply)


async def adaugeo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if au_key_holder(update.message.from_user.id, update):
        block_list.append(context.args[0])
        persist_update()
        await update.message.reply_text('additae {} ad criteria'.format(context.args[0]))
    else:
        await update.message.reply_text(locked_out_reply)

async def expungo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if au_key_holder(update.message.from_user.id, update):
        block_list.remove(context.args[0])
        persist_update()
        await update.message.reply_text('detractus {} ex criteria'.format(context.args[0]))
    else:
        await update.message.reply_text(locked_out_reply)


async def message_scanner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    html_text = update.message.text_html.casefold()
    regulator = [trigger for trigger in block_list if trigger in html_text]
    if any(regulator):
        LOGGER.info("%s trigger from blocklist detected!", regulator)
        await update.message.reply_text(output_text.format(update.message.from_user.username, str(regulator[0].rsplit('.',1)[0])))
        try:
            await update.effective_chat.ban_member(update.message.from_user.id)
            await update.message.delete()
        except:
            await update.message.reply_text('👁‍🗨 Unable to eliminate this user! Has this automaton been granted admin privilege?')
    else:
        pass

malum_index_command = CommandHandler("malum_index", malum_index)
adaugeo_command = CommandHandler("adaugeo", adaugeo)
expungo_command = CommandHandler("expungo", expungo)
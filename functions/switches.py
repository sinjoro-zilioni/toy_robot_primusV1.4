#!/usr/bin/env python
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from keys import locked_out_reply
from functions.key_sys import au_key_holder


async def incipio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'💡 winding up  @{context.bot.username}')
    

async def terminatio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if au_key_holder(update.message.from_user.id, update):
        await update.message.reply_text(f'🔌 Winding down @{context.bot.username}')
        exit()
    else:
        await update.message.reply_text(locked_out_reply)


incipio_command = CommandHandler("incipio", incipio)
terminatio_command = CommandHandler("terminatio", terminatio)

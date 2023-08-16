#!/usr/bin/env python
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from keys import au_key
from functions.indicator import LOGGER
from ag_key import keys

keys = keys
au_lock = "You must have the ☉︎ AU key to conduct this transaction!"

def ag_key_holder(user_id: int, update: Update)-> bool:
    user_id = update.effective_user.id
    msg_id = update.message.from_user.id
    if msg_id in keys:
        LOGGER.info("%s holds the key %s ",user_id, keys)
        return True
    else:
        LOGGER.info("%s does not have the key %s",user_id, keys)
        return False
    
def au_key_holder(user_id: int, update: Update)-> bool:
    user_id = update.effective_user.id
    msg_id = update.message.from_user.id
    if msg_id in au_key:
        LOGGER.info("%s holds the key %s ",user_id, au_key)
        return True
    else:
        LOGGER.info("%s does not have the key %s",user_id, au_key)
        return False
    


async def bestow_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    id = int(context.args[0])
    admin = update.effective_user.username
    if au_key_holder(update.message.from_user.id, update) and len(context.args) == 1:
        try:
            LOGGER.info("User %s has initiated bestow key to %s", admin, id)
            keys.append(id)
            entry = 'keys = ' + str(keys)
            file = open('ag_key.py', 'w')
            file.write(entry)
            file.close()
            await update.message.reply_text(f'@{admin}  successfully bestowed key to user: {id}')
        except:
            await update.message.reply_text(f'@{admin}  unable to bestow key upon user: {id}')
    else:
        await update.message.reply_text(au_lock)


async def confiscate_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    id = int(context.args[0])
    admin = update.effective_user.username
    if au_key_holder(update.message.from_user.id, update) and len(context.args) == 1:
        try:
            LOGGER.info("User %s has initiated confiscate key from user: %s", admin, id)
            keys.remove(id)
            entry = 'keys = ' + str(keys)
            file = open('ag_key.py', 'w')
            file.write(entry)
            file.close()
            await update.message.reply_text(f'@{admin} successfully confiscated key from user: {id}')
        except:
            await update.message.reply_text(f'@{admin} unable to confiscate key from user: {id}')
    else:
        await update.message.reply_text(au_lock)
 

async def key_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if au_key_holder(update.message.from_user.id, update):
        gear_train = []

        for trigger in range(0, len(keys), 50):
            gear_train.append(keys[trigger:trigger + 50])

        for gear in gear_train:
            await update.message.reply_text(str(gear))
    else:
        await update.message.reply_text(au_lock) 


bestow_key_command = CommandHandler("bestow_key", bestow_key)
confiscate_key_command = CommandHandler("confiscate_key", confiscate_key)
key_list_command = CommandHandler("key_list", key_list)


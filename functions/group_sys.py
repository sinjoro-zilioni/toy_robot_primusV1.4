#!/usr/bin/env python
from typing import Optional, Tuple

from telegram import Update, Chat, ChatMember, ChatMemberUpdated, ChatMember
from telegram.ext import ChatMemberHandler, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from keys import LOG_CHANNEL, locked_out_reply
from functions.indicator import LOGGER
from functions.key_sys import au_key_holder


def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tracks the chats the bot is in."""
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result
    cause_name = update.effective_user.full_name

    # Handle chat types differently:
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        if not was_member and is_member:
            LOGGER.info("%s unblocked the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).add(chat.id)
        elif was_member and not is_member:
            LOGGER.info("%s blocked the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).discard(chat.id)
    elif chat.type in [Chat.GROUP]:
        if not was_member and is_member:
            LOGGER.info("%s added the bot to the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).add(chat.id)
            await update.effective_chat.send_message(f'This automaton @{context.bot.username} cannot be added to private groups!!')
            context.bot_data.setdefault("group_ids", set()).discard(chat.id)
            await context.bot.leave_chat(chat.id)
        elif was_member and not is_member:
            LOGGER.info("%s removed the bot from the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).discard(chat.id)
    elif chat.type in [Chat.SUPERGROUP]:
        if not was_member and is_member:
            LOGGER.info("%s added the bot to the group %s, %s, %s", cause_name, chat.title, chat.id, chat.username)
            context.bot_data.setdefault("group_ids", set()).add(chat.id)
            context.bot_data.setdefault("group_username", set()).add(chat.username)
        elif was_member and not is_member:
            LOGGER.info("%s removed the bot from the group %s, %s, %s", cause_name, chat.title, chat.id, chat.username)
            context.bot_data.setdefault("group_ids", set()).discard(chat.id)
            context.bot_data.setdefault("group_username", set()).discard(chat.username)
    elif not was_member and is_member:
        LOGGER.info("%s added the bot to the channel %s", cause_name, chat.title)
        context.bot_data.setdefault("channel_ids", set()).add(chat.id)
        await update.effective_chat.send_message(f'This automaton @{context.bot.username} cannot be added to channels!!')
        context.bot_data.setdefault("channel_ids", set()).discard(chat.id)
        await context.bot.leave_chat(chat.id)
    elif was_member and not is_member:
        LOGGER.info("%s removed the bot from the channel %s", cause_name, chat.title)
        context.bot_data.setdefault("channel_ids", set()).discard(chat.id)


async def chat_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    group_username = ", @".join(str(gid) for gid in context.bot_data.setdefault("group_username", set()))
    chat_list_usernames = (
        f"This automaton is connected to these groups; with the usernames: @{group_username}"
    )  
    await update.effective_message.reply_text(chat_list_usernames)

async def observatio_fororum(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if au_key_holder(update.message.from_user.id, update):
        group_ids = ", ".join(str(gid) for gid in context.bot_data.setdefault("group_ids", set()))
        group_username = ", @".join(str(gid) for gid in context.bot_data.setdefault("group_username", set()))
        chat_list_usernames = (
            f"This automaton is connected to these groups; with the usernames: @{group_username}"
        )
        chat_list_ids = (f" and the corresponding IDs: {group_ids}."
        )
        await context.bot.send_message(chat_id=LOG_CHANNEL, text=chat_list_usernames, parse_mode=ParseMode.HTML)
        await context.bot.send_message(chat_id=LOG_CHANNEL, text=chat_list_ids, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(locked_out_reply)

async def observatio_populum(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if au_key_holder(update.message.from_user.id, update):
        user_ids = ", ".join(str(uid) for uid in context.bot_data.setdefault("user_ids", set()))
        total_count = sum(user_ids)
        text = (
            f"{context.bot.username} is currently in a conversation with {total_count} users. "
        )
        await update.effective_message.reply_text(text)
    else:
        await update.message.reply_text(locked_out_reply)


async def observatio_canalium(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if au_key_holder(update.message.from_user.id, update):
        channel_ids = ", ".join(str(cid) for cid in context.bot_data.setdefault("channel_ids", set()))
        text = (
            f"@{context.bot.username} is currently in the channels with IDs {channel_ids}."
        )
        await update.effective_message.reply_text(text)
    else:
        await update.message.reply_text(locked_out_reply)
    

async def relinquo_forum(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if au_key_holder(update.message.from_user.id, update) and len(context.args) == 1:
        chat_id = context.args[0]
        try:
            chat_id = int(context.args[0])
            await update.message.reply_text(f'successfully left the group with ID: {chat_id}')
            await context.bot.leave_chat(chat_id)
        except:
            await update.message.reply_text(f'Could not leave {chat_id}')
    else:
        await update.message.reply_text(
        f"You must bear the AU key and also specify the chat id as follows: /command -00000001"
    )

async def private_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    user_name = update.effective_user.full_name
    chat = update.effective_chat
    if chat.type != Chat.PRIVATE or chat.id in context.bot_data.get("user_ids", set()):
        return

    LOGGER.info("%s started a private chat with the bot", user_name)
    context.bot_data.setdefault("user_ids", set()).add(chat.id)

    await update.effective_message.reply_text(
        f"{user_name}. 🔒 Only key bearers are authorised to engage in private dialogue with this automaton!"
    )


groups_command = CommandHandler("observatio_fororum", observatio_fororum)
users_command = CommandHandler("observatio_populum", observatio_populum)
channels_command = CommandHandler("observatio_canalium", observatio_canalium)
relinquo_command = CommandHandler("relinquo_forum", relinquo_forum)
chat_track = ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER)
chat_list_command = CommandHandler("chats", chat_list)




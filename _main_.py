#!/usr/bin/env python
import time
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, CommandHandler, MessageHandler, filters
from keys import clavis_i
from functions import allow_list, auxilium, group_sys, indicator, key_sys, malice_blocker, switches

def main() -> None:
    time.sleep(30)
    application = Application.builder().token(clavis_i).build()
    application.add_handler(allow_list.allowed_command)
    application.add_handler(allow_list.add_command)
    application.add_handler(allow_list.remove_command)
    
    application.add_handler(malice_blocker.malum_index_command)
    application.add_handler(malice_blocker.adaugeo_command)
    application.add_handler(malice_blocker.expungo_command)
    application.add_handler(auxilium.auxilium_command)

    application.add_handler(switches.incipio_command)
    application.add_handler(group_sys.relinquo_command)
    application.add_handler(switches.terminatio_command)
    application.add_error_handler(indicator.error_handler)

    application.add_handler(key_sys.bestow_key_command)
    application.add_handler(key_sys.confiscate_key_command)
    application.add_handler(key_sys.key_list_command)

    application.add_handler(group_sys.chat_list_command)
    application.add_handler(group_sys.groups_command)
    application.add_handler(group_sys.users_command)
    application.add_handler(group_sys.channels_command)

    application.add_handler(ChatMemberHandler(group_sys.track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.FORWARDED, allow_list.forwards))
    application.add_handler(MessageHandler(filters.TEXT, malice_blocker.message_scanner, group_sys.private_chat))
    application.run_polling()


if __name__ == '__main__':
    main()
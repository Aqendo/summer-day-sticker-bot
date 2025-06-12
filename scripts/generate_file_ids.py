#!/usr/bin/env python3
# Summer Day Sticker Bot - An inline bot for sending stickers with summer day number
# Copyright (C) 2025 Sergey Sitnikov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import logging
import os
import signal
from typing import List

from dotenv import find_dotenv, load_dotenv
from telegram import Message, Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler

load_dotenv(find_dotenv())

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)

file_ids: List[str] = []

day_index_now = 1

AMOUNT_DAYS = 92


application = (
    ApplicationBuilder()
    .token(
        os.getenv(
            "BOT_TOKEN",
            "please set BOT_TOKEN in environment variables and/or in .env file",
        )
    )
    .build()
)


async def grab_sticker_file_id(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    global day_index_now
    if not isinstance(update.message, Message):
        return
    if not update.message or not update.message.sticker:
        if day_index_now != AMOUNT_DAYS + 1:
            await update.message.reply_text(
                f"You should send sticker for day number {day_index_now}"
            )
        else:
            await update.message.reply_text(
                "You should send a sticker for non-summer time"
            )
        return

    if day_index_now != AMOUNT_DAYS + 1:
        file_ids.append(update.message.sticker.file_id)
        await update.message.reply_text(f"Sticker for day {day_index_now} received!")
        day_index_now += 1
        if day_index_now != AMOUNT_DAYS + 1:
            await update.message.reply_text(
                f"You should send sticker for day number {day_index_now}"
            )
        else:
            await update.message.reply_text(
                "You should send a sticker for non-summer time"
            )
    else:
        file_ids.append(update.message.sticker.file_id)
        await update.message.reply_text("All done! Exiting the script!")
        print(
            "These are the file_ids of all the stickers you have sent to me:", file_ids
        )
        with open("file_ids.json", "w+") as f:
            f.write(json.dumps(file_ids))
        print("They are written into `file_ids.json`")
        os.kill(os.getpid(), signal.SIGINT)


def main() -> None:
    application.add_handler(MessageHandler(None, grab_sticker_file_id))

    print("Write /start to the bot or send a sticker for the 1st day!")

    application.run_polling(allowed_updates=Update.MESSAGE)


if __name__ == "__main__":
    main()

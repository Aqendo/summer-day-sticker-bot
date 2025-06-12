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

import datetime
import json
import logging
import os
from typing import Any, List

import pytz
from dotenv import find_dotenv, load_dotenv
from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultCachedSticker,
    InlineQueryResultsButton,
    Message,
    Update,
    User,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    InlineQueryHandler,
    MessageHandler,
    filters,
)

import database

load_dotenv(find_dotenv())

# Should I move it somewhere else? Don't know.
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.ERROR)

logger = logging.getLogger("summer-day-sticker-bot")

USERNAME = None
TOKEN = None
FILE_IDS_PATH = None
FILE_IDS: List[str] = []


def load_token() -> None:
    global TOKEN
    TOKEN = os.getenv("BOT_TOKEN")
    if TOKEN is None:
        logger.log(
            logging.ERROR,
            "Environment variable `BOT_TOKEN` is not set. You should put token you got from @BotFather there.",
        )
        exit(1)


def is_initialized() -> bool:
    return (
        len(FILE_IDS) != 0
        and USERNAME is not None
        and TOKEN is not None
        and FILE_IDS_PATH is not None
    )


# This is so ridiculously funny how the world got us to 6 Any's just to make `mypy` happy
async def get_username(application: Application[Any, Any, Any, Any, Any, Any]) -> None:
    global USERNAME
    if not application.bot or not application.bot.username:
        assert (
            False
        ), "TODO: Implement proper error handling. Is this case even reachable? Who knows."
    USERNAME = application.bot.username


def load_file_ids() -> None:
    global FILE_IDS, FILE_IDS_PATH
    FILE_IDS_PATH = os.getenv("FILE_IDS_PATH")
    if not FILE_IDS_PATH:
        logger.log(logging.ERROR, "Environment variable `FILE_IDS_PATH` is not set.")
        exit(1)
    if not os.path.exists(FILE_IDS_PATH):
        logger.log(
            logging.ERROR,
            "You should generate file ids via `./scripts/generate_file_ids.py`",
        )
        exit(1)

    with open(FILE_IDS_PATH, "r") as f:
        FILE_IDS = json.loads(f.read())

    if len(FILE_IDS) != 93:
        logger.log(
            logging.ERROR,
            "You should generate file ids via `./scripts/generate_file_ids.py`",
        )
        exit(1)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global USERNAME
    if not isinstance(update.message, Message):
        return
    if not USERNAME:
        raise Exception(
            "Isn't bot initialized? Is this case even reachable? Who knows."
        )
    await update.message.reply_text(
        f"I work only in inline mode! Type <code>@{USERNAME}</code> in any chat.",
        parse_mode="HTML",
    )


async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not isinstance(update.inline_query, InlineQuery) or not is_initialized():
        return
    zone: int = await database.get_timezone(update.inline_query.from_user.id)
    datetime_now: datetime.datetime = datetime.datetime.now(
        pytz.timezone(f"Etc/GMT{-zone:+}")
    )
    day: int = (
        datetime.datetime(
            year=datetime_now.year, month=datetime_now.month, day=datetime_now.day
        )
        - datetime.datetime(year=datetime_now.year, month=5, day=31)
    ).days

    if 1 <= day <= 92:
        sticker_file_id = FILE_IDS[day - 1]
    else:
        sticker_file_id = FILE_IDS[92]

    await update.inline_query.answer(
        results=[
            InlineQueryResultCachedSticker(id="1", sticker_file_id=sticker_file_id)
        ],
        cache_time=0,
        button=InlineQueryResultsButton(
            text=f"Your timezone is: GMT{zone:+}. Click to change!",
            start_parameter="change_timezone",
        ),
    )


def generate_timezone_change_buttons(zone: int) -> List[List[InlineKeyboardButton]]:
    buttons: List[List[InlineKeyboardButton]] = [[] for i in range(27 // 3)]
    for row in range(27 // 3):
        for zone_hour in range(-12 + row * 3, -12 + (row + 1) * 3):
            if zone == zone_hour:
                buttons[row].append(
                    InlineKeyboardButton(
                        text=f"GMT{zone_hour:+} ✅", callback_data=f"{zone_hour}"
                    )
                )
            else:
                buttons[row].append(
                    InlineKeyboardButton(
                        text=f"GMT{zone_hour:+}", callback_data=f"{zone_hour}"
                    )
                )
    return buttons


async def change_timezone_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not isinstance(update.message, Message) or not isinstance(
        update.message.from_user, User
    ):
        return
    zone = await database.get_timezone(update.message.from_user.id)
    buttons = generate_timezone_change_buttons(zone)
    await update.message.reply_text(
        text="Choose your timezone", reply_markup=InlineKeyboardMarkup(buttons)
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (
        not isinstance(update.callback_query, CallbackQuery)
        or not update.callback_query.data
        or not update.callback_query.data.lstrip("-").isdigit()
        or not -12 <= int(update.callback_query.data) <= 14
    ):
        return
    zone: int = int(update.callback_query.data)
    await database.set_timezone(update.callback_query.from_user.id, zone)
    buttons = generate_timezone_change_buttons(zone)
    await update.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(buttons))


async def post_init(application: Application[Any, Any, Any, Any, Any, Any]) -> None:
    await get_username(application)
    await database.initialize_database(application)
    logger.log(logging.NOTSET, "Bot has started!")


def run_bot() -> None:
    load_file_ids()

    load_token()

    if TOKEN is None:
        logger.log(
            logging.ERROR,
            "Environment variable `BOT_TOKEN` is not set. You should put token you got from @BotFather there.",
        )
        exit(1)

    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    application.add_handler(
        CommandHandler(
            "start", change_timezone_start, filters.Text(["/start change_timezone"])
        )
    )
    application.add_handler(MessageHandler(None, message_handler))

    application.add_handler(InlineQueryHandler(inline_handler))

    application.add_handler(CallbackQueryHandler(callback_handler))

    application.run_polling()


if __name__ == "__main__":
    run_bot()

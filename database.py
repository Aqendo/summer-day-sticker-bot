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

import logging
import os
from typing import Any

import aiosqlite
from telegram.ext import Application

DATABASE_PATH = None
logger = logging.getLogger("summer-day-sticker-bot")


async def initialize_database(
    application: Application[Any, Any, Any, Any, Any, Any],
) -> None:
    global DATABASE_PATH
    DATABASE_PATH = os.getenv("DATABASE_PATH")
    if not DATABASE_PATH:
        logger.log(logging.ERROR, "Environment variable `DATABASE_PATH` is not set.")
        exit(1)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS timezones ( id INTEGER PRIMARY KEY, zone TINYINT)"
        )
        await db.commit()
    logger.log(logging.INFO, "Database initialized!")


async def is_intialized() -> bool:
    if not DATABASE_PATH:
        logger.log(
            logging.ERROR,
            "Database is used before initializing! Initialize it first with `initialize_database(application)`",
        )
        return False
    return True


async def get_timezone(user_id: int) -> int:
    if not await is_intialized():
        return 3
    assert DATABASE_PATH is not None
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            sql="INSERT OR IGNORE INTO timezones VALUES (?, ?)", parameters=(user_id, 3)
        )
        await db.commit()
        cursor = await db.execute(
            sql="SELECT zone FROM timezones WHERE id = ?", parameters=(user_id,)
        )
        result = await cursor.fetchone()
        assert result is not None
        assert isinstance(result[0], int)
        return result[0]


async def set_timezone(user_id: int, zone: int) -> None:
    if not await is_intialized():
        return
    assert DATABASE_PATH is not None
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            sql="INSERT OR REPLACE INTO timezones VALUES (?, ?)",
            parameters=(user_id, zone),
        )
        await db.commit()

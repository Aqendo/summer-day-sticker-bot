# Summer Day Sticker Bot

<p align="center">
    <img src="pictures/bot_in_use.webp" alt="Bot in use">
</p>

## What's it?
This bot is designed to send funny stickers with the days of summer according to the current date.

## Prerequisites
- [You should get a bot token from @BotFather](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)
- You should activate `inline mode` in [@BotFather](https://t.me/BotFather)

## Configuration
You should set these environments variables:
- `BOT_TOKEN` - token from [@BotFather](https://t.me/BotFather)
- `DATABASE_PATH` - file name or path where the file of [SQLite](https://sqlite.org) database will be located

Alternatively you can set them in .env file at the root of this bot's folder. There is also `.env.example` provided.

What can be as funny as this bot's purpose? **Telegram limitations.** Therefore your bot _should see every sticker it sents before sending them._

I wrote some little script that will help you get these file_ids. If running locally, start it with
```shell
$ ./scripts/generate_file_ids.py
```
And it will (hopefully) help configuring that part.

**P.S. For Docker configuration see [Running in Docker](#running-in-docker)

## `file_ids.json` structure
This is supposed to be a list of _(currently)_ 93 strings.

- **First 92 of them** - file id's of stickers for 1..92 day of summer
- **Last one** - to show it when it's not the summer

## Running locally
```shell
$ python3 bot.py
```


## Running in Docker
When using Docker, in `.env` you should only ever change `BOT_TOKEN`

Build the image:
```shell
$ docker build -t summer-day-sticker-bot .
```
Generate `file_ids.json` with 
```shell
$ docker run --env-file .env -it summer-day-sticker-bot ./scripts/generate_file_ids.py
```
**OR** 

If you already have it somewhere
```shell
$ ./scripts/copy_fileids.sh /path/to/file_ids.json
```
Then, finally, run the bot!
```shell
$ docker compose up -d
```
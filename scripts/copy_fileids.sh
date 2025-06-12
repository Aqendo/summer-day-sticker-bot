#!/bin/sh
set -xe
# Taken from https://github.com/moby/moby/issues/25245
docker run --rm -v $PWD:/source -v summerbot_data:/dest -w /source summer-day-sticker-bot cp $1 /dest/file_ids.json
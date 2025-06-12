#!/bin/sh
set -xe
mypy . --strict
ruff check .
#!/bin/sh
set -xe
black .
isort . --profile black
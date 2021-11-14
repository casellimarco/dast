#!/bin/bash

set -e

source venv/bin/activate

make lint
make test

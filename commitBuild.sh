#!/bin/bash

set -e

source venv/bin/activate

make lint

python dast/lcs.py
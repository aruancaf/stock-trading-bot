#!/usr/bin/env bash

if [ "$(uname)" == "Darwin" ]; then
    # Do something under Mac OS X platform
    echo "Using MacOS"
    ./venv/bin/python process_runner.py
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Do something under GNU/Linux platform
    echo "Linux"
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ] || [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    # Do something under Windows NT platform
    echo "Windows"
    ./venv_windows/Scripts/python process_runner.py
fi
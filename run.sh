#!/usr/bin/env bash

if [ "$(uname)" == "Darwin" ]; then
    echo "MacOS"
    source ./venv/bin/activate
    ./process_runner.py
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ] || [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    echo "WindowsWSL"
    ./venv_windows/Scripts/activate
    ./venv_windows/Scripts/python process_runner.py
fi
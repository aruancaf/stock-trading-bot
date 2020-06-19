#!/usr/bin/env bash

if [ "$(uname)" == "Darwin" ] || [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Do something under Unix platform
    echo "Unix"
    source ./venv/bin/activate
    ./process_runner.py
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ] || [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    echo "Windows WSL"
    source ./venv_windows/Scripts/activate
    ./venv_windows/Scripts/python process_runner.py
fi
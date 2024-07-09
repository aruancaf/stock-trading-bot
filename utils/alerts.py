import os
from sys import platform


def say_beep(n: int):
    for i in range(0, n):
        if platform == "darwin":
            os.system("say beep")

import os
from .conversation import bot_loop

def run_bot(message_limit=None):
    bot_loop(message_limit)

if __name__ == "__main__":
    run_bot()
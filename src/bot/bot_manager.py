import random
import os
import json
from dotenv import load_dotenv
from .main import run_bot_async, test_token
import asyncio
from discord.errors import LoginFailure

class BotManager:
    def __init__(self):
        self.bots = []
        load_dotenv("config/.env")
        self.bots_file = "data/bots.json"
        self.load_bots()

    def add_bot(self, name, token, persona):
        # Test the token before adding the bot
        if test_token(token):
            bot_id = str(max([int(bot['id']) for bot in self.bots] + [-1]) + 1)
            new_bot = {
                "id": bot_id,
                "name": name,
                "token": token,
                "persona": persona
            }
            self.bots.append(new_bot)
            self.save_bots()
            # Create an empty conversation history file for the new bot
            self.save_conversation_history(bot_id, [])
            return True, "Bot added successfully."
        else:
            return False, "Invalid token. Bot not added."

    def get_bots(self):
        return self.bots

    def run_bot(self, bot_id, token, persona, interval):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_bot_async(bot_id, token, persona, interval))
        except Exception as e:
            print(f"Error running bot with ID {bot_id}: {str(e)}")
        finally:
            loop.close()

    def save_bots(self):
        if self.bots:  # Only save if there are bots to save
            with open(self.bots_file, 'w') as f:
                json.dump(self.bots, f, indent=2)
        else:
            print("Warning: No bots to save. Skipping write operation.")

    def load_bots(self):
        if os.path.exists(self.bots_file):
            try:
                with open(self.bots_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        self.bots = json.loads(content)
                    else:
                        print(f"Warning: {self.bots_file} is empty. Keeping existing bots if any.")
            except json.JSONDecodeError as e:
                print(f"Error decoding {self.bots_file}: {str(e)}. Keeping existing bots if any.")
        else:
            print(f"Warning: {self.bots_file} does not exist. Keeping existing bots if any.")
        
        # Ensure all bots have an ID
        for i, bot in enumerate(self.bots):
            if 'id' not in bot:
                bot['id'] = str(i)
        self.save_bots()  # Save the updated bots with IDs

    def delete_bot(self, bot_id):
        self.bots = [bot for bot in self.bots if bot['id'] != bot_id]
        self.save_bots()
        # Optionally, delete the conversation history file
        history_file = f"data/conversation_history_{bot_id}.json"
        if os.path.exists(history_file):
            os.remove(history_file)

    def save_conversation_history(self, bot_id, history):
        filename = f"data/conversation_history_{bot_id}.json"
        with open(filename, 'w') as f:
            json.dump(history, f)

    def load_conversation_history(self, bot_id):
        filename = f"data/conversation_history_{bot_id}.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return []

    def update_bot_persona(self, bot_id, new_persona):
        for bot in self.bots:
            if bot['id'] == bot_id:
                bot['persona'] = new_persona
                self.save_bots()
                return True
        return False

    def get_bot(self, bot_id):
        for bot in self.bots:
            if bot['id'] == bot_id:
                return bot
        return None

    def set_bot_interval(self, bot_id, interval):
        for bot in self.bots:
            if bot['id'] == bot_id:
                bot['interval'] = interval
                self.save_bots()
                return True
        return False

    def update_bot(self, bot_id, name, token, persona):
        for bot in self.bots:
            if bot['id'] == bot_id:
                bot['name'] = name
                bot['token'] = token
                bot['persona'] = persona
                self.save_bots()
                return True
        return False
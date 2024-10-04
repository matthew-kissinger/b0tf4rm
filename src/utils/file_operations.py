import json
import os
import discord

def load_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return ""

def save_to_file(content, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_discord_logs(bot_id, new_content, file_path):
    logs_file = f"data/memory_{bot_id}.txt"
    current_content = load_from_file(logs_file)
    updated_content = current_content + "\n" + new_content if current_content else new_content
    save_to_file(updated_content, logs_file)

async def get_last_messages(channel, limit=20):
    messages = []
    async for message in channel.history(limit=limit):
        if message.author == channel.guild.me:
            role = "assistant"
            content = message.content
        else:
            role = "user"
            author_name = message.author.display_name if isinstance(message.author, discord.Member) else message.author.name
            content = f"<{author_name}> {message.content}"
        messages.append({"role": role, "content": content})
    
    return messages[::-1]

def save_conversation_history(bot_id, messages):
    filename = f"data/conversation_history_{bot_id}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def load_conversation_history(bot_id):
    filename = f"data/conversation_history_{bot_id}.json"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []
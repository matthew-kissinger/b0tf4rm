import discord
from discord import app_commands
from .conversation import bot_loop
import os
import asyncio

def test_token(token):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)
        loop.run_until_complete(client.login(token))
        return True
    except discord.errors.LoginFailure:
        return False
    finally:
        loop.run_until_complete(client.close())
        loop.close()

async def run_bot_async(bot_id, token, persona, interval):
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.messages = True
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    @client.event
    async def on_ready():
        print(f'{client.user} (ID: {bot_id}) has connected to Discord!')
        try:
            synced = await tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
        
        print(f"Starting bot loop for {client.user} (ID: {bot_id})")
        await bot_loop(client, bot_id, persona, interval)

    print(f"Starting bot with ID: {bot_id}")
    await client.start(token)
    print(f"Bot with ID: {bot_id} has stopped running")

def run_bot(bot_id, token, persona):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_bot_async(bot_id, token, persona))
    except Exception as e:
        print(f"Error running bot with ID {bot_id}: {str(e)}")
    finally:
        loop.close()
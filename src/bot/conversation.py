import os
from src.ai.chat import generate_response, process_response
from src.utils.file_operations import get_last_messages, save_conversation_history, load_conversation_history
import asyncio

async def bot_loop(client, bot_id, persona, interval):
    channel_id = os.getenv("CHANNEL_ID")
    channel = client.get_channel(int(channel_id))
    
    if not channel:
        print(f"Could not find channel with ID {channel_id}")
        return
    
    print(f"Bot {bot_id} is monitoring channel: {channel.name} (ID: {channel.id})")
    
    while True:
        print(f"Starting new loop iteration for bot {bot_id}")
        discord_messages = await get_last_messages(channel, limit=20)
        conversation_history = load_conversation_history(bot_id)
        
        print(f"Loaded {len(discord_messages)} messages from Discord")
        print(f"Loaded {len(conversation_history)} messages from conversation history")
        
        # Convert discord_messages to the format we want to store
        formatted_messages = []
        for msg in discord_messages:
            if msg["role"] == "user":
                formatted_messages.append(msg)
            elif msg["role"] == "assistant":
                # Only include !PING responses in the conversation history
                content = msg["content"]
                if content.startswith("!PING{"):
                    formatted_messages.append({"role": "assistant", "content": content})
        
        # Find new messages
        new_messages = [msg for msg in formatted_messages if msg not in conversation_history]
        print(f"Found {len(new_messages)} new messages")
        
        if new_messages:
            print(f"New messages detected: {len(new_messages)}")
            
            # Update conversation history with new messages
            conversation_history.extend(new_messages)
            conversation_history = conversation_history[-20:]  # Keep only the last 20 messages
            save_conversation_history(bot_id, conversation_history)
            print(f"Updated conversation history. New length: {len(conversation_history)}")
        
        # Always generate a response if the last message is from a user
        if conversation_history and conversation_history[-1]['role'] == 'user':
            response = generate_response(bot_id, conversation_history, persona)
            
            print(f"Generated response: {response}")
            
            discord_message, cleaned_response = process_response(bot_id, response)
            
            print(f"After process_response:")
            print(f"  discord_message: {discord_message}")
            print(f"  cleaned_response: {cleaned_response}")
            
            if cleaned_response:
                if cleaned_response.startswith('!PING{'):
                    await channel.send(discord_message)
                    print(f"Message sent to Discord: {discord_message}")
                    conversation_history.append({"role": "assistant", "content": cleaned_response})
                    save_conversation_history(bot_id, conversation_history)
                    print(f"Added bot response to conversation history: {cleaned_response}")
                elif cleaned_response.startswith('!LOG{'):
                    print("LOG response received. Updating memory but not sending to Discord or adding to conversation history.")
                elif cleaned_response.startswith('!AFK{'):
                    print("AFK response received. Not sending to Discord or adding to conversation history.")
        else:
            print("No new user messages. Waiting for user input.")
        
        # Wait for the specified interval before checking for new messages
        print(f"Bot {bot_id} waiting for {interval} seconds before next iteration")
        await asyncio.sleep(interval)

    print(f"Bot {bot_id} received stop signal and is shutting down.")
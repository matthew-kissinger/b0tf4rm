import requests
import re
from src.utils.file_operations import load_from_file, save_to_file, update_discord_logs, load_conversation_history
import json

LMSTUDIO_CHAT_URL = "http://localhost:1234/v1/chat/completions"
LMSTUDIO_HEADERS = {"Content-Type": "application/json"}

MEMORY_FILE = "data/memory.txt"

with open("prompts/system_prompt.txt", "r") as f:
    SYSTEM_PROMPT = f.read()

CURRENT_MEMORY = load_from_file(MEMORY_FILE)

def generate_response(bot_id, conversation_history, persona):
    try:
        print(f"Generating response for bot {bot_id}")
        if not conversation_history:
            print("No conversation history. Returning AFK.")
            return "!AFK{}"

        # Check if the last message is from a user
        if conversation_history[-1]['role'] == 'user':
            memory_file = f"data/memory_{bot_id}.txt"
            current_memory = load_from_file(memory_file)
            print(f"Current memory: {current_memory}")

            # Include the memory in the system prompt as DISCORD_LOGS
            current_prompt = SYSTEM_PROMPT.replace("[DISCORD_LOGS]", f"[DISCORD_LOGS]\n{current_memory}\n[/DISCORD_LOGS]")
            current_prompt = current_prompt.replace("[BOT_PERSONA]", f"[BOT_PERSONA]\n{persona}\n[/BOT_PERSONA]")
            
            messages = [{"role": "system", "content": current_prompt}]
            messages.extend(conversation_history)

            payload = {
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500,
                "stream": False 
            }
            
            print("Request payload:")
            print(json.dumps(payload, indent=2))
            
            response = requests.post(LMSTUDIO_CHAT_URL, json=payload, headers=LMSTUDIO_HEADERS)
            response.raise_for_status()
            data = response.json()
            content = data['choices'][0]['message']['content'].strip()
            
            print(f"Raw response from AI model: {content}")
            
            if not content:
                print("Warning: Empty response from AI model")
                print(f"Full API response: {data}")
                return "!AFK{}"
            
            return content
        else:
            print("Last message is not from a user. Returning AFK.")
            return "!AFK{}"
    except Exception as e:
        print(f"Error generating response: {e}")
        return f"!AFK{{}}"

def process_response(bot_id, response):
    print(f"Processing response for bot {bot_id}")
    if response:
        print(f"Raw response: {response}")
        
        # Define patterns for each response type
        ping_pattern = r'!PING\{(.*?)\}'
        log_pattern = r'!LOG\{(.*?)\}'
        afk_pattern = r'!AFK\{\}'
        
        # Check for PING response
        ping_match = re.match(ping_pattern, response)
        if ping_match:
            content = ping_match.group(1).strip()
            return content, response  # Return content for Discord and full response for history
        
        # Check for LOG response
        log_match = re.match(log_pattern, response)
        if log_match:
            content = log_match.group(1).strip()
            update_discord_logs(bot_id, content, f"data/memory_{bot_id}.txt")
            print(f"LOG entry added to DISCORD_LOGS: {content}")
            return None, response  # No Discord message, but keep the LOG in history
        
        # Check for AFK response
        if re.match(afk_pattern, response):
            return None, response  # No Discord message, but keep the AFK in history
        
        # If no valid response type is found, treat it as an error
        print("Invalid response format")
        return None, None
    
    print("No response to process")
    return None, None
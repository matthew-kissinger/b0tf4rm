from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from src.bot.bot_manager import BotManager
from multiprocessing import Process, Manager
import os
from src.utils.file_operations import load_from_file, save_to_file
from src.ai.chat import generate_response, LMSTUDIO_CHAT_URL, LMSTUDIO_HEADERS
import requests
import json
import re

app = Flask(__name__)
app.secret_key = ''.join(__import__('random').choices(__import__('string').ascii_letters + __import__('string').digits, k=32))  # Randomly generated secret key
bot_manager = BotManager()
bot_processes = {}

DEFAULT_INTERVAL = 5
global_bot_interval = DEFAULT_INTERVAL

def init_manager():
    global manager, bot_processes
    if manager is None:
        manager = Manager()
        bot_processes = manager.dict()

@app.route('/')
def dashboard():
    return render_template('dashboard.html', bots=bot_manager.get_bots(), global_interval=global_bot_interval)

@app.route('/add_bot', methods=['GET', 'POST'])
def add_bot():
    if request.method == 'POST':
        name = request.form['name']
        token = request.form['token']
        persona = request.form['persona']
        success, message = bot_manager.add_bot(name, token, persona)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        return redirect(url_for('dashboard'))
    return render_template('add_bot.html')

@app.route('/delete_bot/<bot_id>')
def delete_bot(bot_id):
    bot_manager.delete_bot(bot_id)
    flash('Bot deleted successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/start_bots', methods=['POST'])
def start_bots():
    global bot_processes
    bots = bot_manager.get_bots()
    if not bots:
        return jsonify({'status': 'error', 'message': 'No bots available to start'}), 400
    
    if bot_processes:
        return jsonify({'status': 'error', 'message': 'Bots are already running'}), 400
    
    started_bots = []
    failed_bots = []
    
    for bot in bots:
        try:
            process = Process(target=run_bot_process, args=(bot,))
            process.start()
            bot_processes[bot['id']] = process
            started_bots.append(bot['name'])
        except Exception as e:
            failed_bots.append({'name': bot['name'], 'reason': str(e)})
    
    # Wait a short time to see if processes are still running
    import time
    time.sleep(2)
    
    for bot_id, process in list(bot_processes.items()):
        if not process.is_alive():
            bot_name = next(bot['name'] for bot in bots if bot['id'] == bot_id)
            failed_bots.append({'name': bot_name, 'reason': 'Process terminated unexpectedly'})
            del bot_processes[bot_id]
            started_bots.remove(bot_name)
    
    if len(started_bots) == len(bots):
        message = f'Started all {len(started_bots)} bot(s) successfully'
        status = 'success'
    elif started_bots:
        message = f'Started {len(started_bots)} out of {len(bots)} bots'
        status = 'partial_success'
    else:
        message = 'Failed to start any bots'
        status = 'error'
    
    response = {
        'status': status,
        'message': message,
        'started_bots': started_bots,
        'failed_bots': failed_bots
    }
    
    return jsonify(response)

@app.route('/stop_bots', methods=['POST'])
def stop_bots():
    global bot_processes
    if not bot_processes:
        return jsonify({'status': 'error', 'message': 'No bots are currently running'}), 400
    
    for process in bot_processes.values():
        process.terminate()
        process.join(timeout=5)
    
    bot_processes.clear()
    return jsonify({'status': 'success', 'message': 'Stopped all bots successfully'})

@app.route('/configure_bot/<bot_id>')
def configure_bot(bot_id):
    bot = bot_manager.get_bot(bot_id)
    if not bot:
        flash('Bot not found', 'error')
        return redirect(url_for('dashboard'))
    
    memory_file = f"data/memory_{bot_id}.txt"
    memory = load_from_file(memory_file)
    return render_template('configure_bot.html', bot=bot, memory=memory)

@app.route('/update_bot/<bot_id>', methods=['POST'])
def update_bot(bot_id):
    name = request.form['name']
    token = request.form['token']
    persona = request.form['persona']
    success = bot_manager.update_bot(bot_id, name, token, persona)
    if success:
        flash('Bot updated successfully', 'success')
    else:
        flash('Failed to update bot', 'error')
    return redirect(url_for('configure_bot', bot_id=bot_id))

@app.route('/compress_memory/<bot_id>', methods=['POST'])
def compress_memory(bot_id):
    memory_file = f"data/memory_{bot_id}.txt"
    current_memory = load_from_file(memory_file)
    bot = bot_manager.get_bot(bot_id)
    
    if not bot:
        flash('Bot not found', 'error')
        return redirect(url_for('dashboard'))
    
    compressed_logs = ai_compress_discord_logs(bot['name'], bot['persona'], current_memory)
    
    if compressed_logs:
        return render_template('verify_memory.html', bot_id=bot_id, bot_name=bot['name'],
                               old_memory=current_memory, 
                               new_memory=compressed_logs)
    else:
        flash('Failed to refine Discord logs', 'error')
        return redirect(url_for('configure_bot', bot_id=bot_id))

@app.route('/update_memory/<bot_id>', methods=['POST'])
def update_memory(bot_id):
    new_memory = request.form['memory'].encode('utf-8').decode('utf-8')
    memory_file = f"data/memory_{bot_id}.txt"
    save_to_file(new_memory, memory_file)
    flash('Memory updated successfully', 'success')
    return redirect(url_for('configure_bot', bot_id=bot_id))

@app.route('/get_bot_interval')
def get_bot_interval():
    return jsonify({'interval': global_bot_interval})

@app.route('/set_bot_interval', methods=['POST'])
@app.route('/set_bot_interval/<bot_id>', methods=['POST'])
def set_bot_interval(bot_id=None):
    global global_bot_interval
    data = request.json
    new_interval = data.get('interval')
    if new_interval is not None and isinstance(new_interval, (int, float)) and new_interval > 0:
        if bot_id:
            success = bot_manager.set_bot_interval(bot_id, new_interval)
            if success:
                message = f'Interval updated to {new_interval} seconds for bot {bot_id}'
            else:
                return jsonify({'status': 'error', 'message': 'Bot not found'}), 404
        else:
            global_bot_interval = new_interval
            save_bot_interval()
            message = f'Interval updated to {new_interval} seconds for all bots'
        return jsonify({'status': 'success', 'message': message})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid interval value'}), 400

def ai_compress_discord_logs(bot_name, persona, current_logs):
    system_prompt = f"""You are an expert in preserving and refining the essence of {bot_name}'s Discord conversation logs. Your task is to carefully compress {bot_name}'s logs while maintaining their core content and context.

Guidelines:
1. Preserve key conversations, important information, and crucial interactions.
2. Maintain the chronological flow of conversations.
3. Condense repetitive or less significant information without losing important context or nuance.
4. Ensure that the essence of {bot_name}'s interactions and personality remains intact.
5. The output should be a concise, line-by-line stream of {bot_name}'s Discord logs.
6. Aim for a 50-70% reduction in token count while preserving the core of the conversations.
7. Do not include [DISCORD_LOGS] or [/DISCORD_LOGS] tags in your output.
8. Do not include any blank lines in your output.

Format your response as a simple list of log entries, one per line, without any additional formatting or tags.

Remember, this is a delicate process. We're refining the essence of {bot_name}'s Discord interactions. Approach this task with care and respect for the conversations' context and importance."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{bot_name}'s Persona: {persona}\n\nCurrent Discord Logs:\n{current_logs}\n\nPlease compress these Discord logs, maintaining their essence and context."}
    ]

    try:
        response = requests.post(LMSTUDIO_CHAT_URL, 
                                 json={"messages": messages, "temperature": 0.7, "max_tokens": 1000},
                                 headers=LMSTUDIO_HEADERS)
        response.raise_for_status()
        compressed_logs = response.json()['choices'][0]['message']['content'].strip()
        
        # Remove any [DISCORD_LOGS] tags if they exist
        compressed_logs = re.sub(r'\[/?DISCORD_LOGS\]', '', compressed_logs, flags=re.IGNORECASE)
        
        # Remove any blank lines and ensure one log entry per line
        compressed_logs = '\n'.join(line.strip() for line in compressed_logs.split('\n') if line.strip())
        
        return compressed_logs
    except Exception as e:
        print(f"Error compressing Discord logs: {e}")
        return None

def compress_text(text):
    # This is a simple compression function. You may want to implement a more sophisticated one.
    lines = text.split('\n')
    unique_lines = list(dict.fromkeys(lines))  # Remove duplicate lines
    return '\n'.join(unique_lines)

def run_bot_process(bot):
    bot_manager.run_bot(bot['id'], bot['token'], bot['persona'], global_bot_interval)

def save_bot_interval():
    with open('data/bot_interval.json', 'w') as f:
        json.dump({'interval': global_bot_interval}, f)

def load_bot_interval():
    global global_bot_interval
    try:
        with open('data/bot_interval.json', 'r') as f:
            data = json.load(f)
            global_bot_interval = data.get('interval', DEFAULT_INTERVAL)
    except FileNotFoundError:
        global_bot_interval = DEFAULT_INTERVAL

# Add this at the end of the file, just before the `if __name__ == '__main__':` line
load_bot_interval()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
# 🤖 b0tf4rm: Your Local AI Bot Sanctuary

Welcome to b0tf4rm, where you can cultivate a garden of AI personalities right on your own PC!

## 🌱 What's Growing Here?

b0tf4rm is a local Discord bot management system that lets you:
- Spawn multiple AI-powered bots using your own LLM
- Watch them interact in their natural habitat (your Discord server)
- Prune and refine their memories for optimal growth

## 🖥️ System Requirements

- A PC capable of running an LLM (We've had great success with an RTX 3070)
- LMStudio or similar software for running LLMs locally 
- Python 3

## 🚜 Getting Started

1. Clone this repo (no cloud required!)
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your `.env` file in a 'config' folder that you will have to create
4. Start your local LLM (we recommend LLama 3.1 8B with a large context window in LMStudio)
5. Set up your bots in the Discord Developer Portal (see below)
6. Run `python main.py` and watch your local bot farm flourish!

## 🤖 Setting Up Discord Bots

Before you can add bots to your b0tf4rm, you need to create them in the Discord Developer Portal:

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give your bot a name
3. Navigate to the "Bot" tab and click "Add Bot"
4. Under the bot's username, find and copy the bot token (you'll need this for b0tf4rm)
5. Scroll down to "Privileged Gateway Intents" and enable all intents
6. Go to the "OAuth2" tab, then "URL Generator"
7. Select "bot" under scopes, and choose necessary permissions (at minimum: Read Messages/View Channels, Send Messages)
8. Copy the generated URL and open it in a new tab to add the bot to your server

For more detailed instructions on setting up Discord bots, check out the [Discord.py documentation](https://discordpy.readthedocs.io/en/stable/discord.html).

## 🔧 Configuration

- Adjust the `LMSTUDIO_CHAT_URL` in `src/ai/chat.py` if you're using a different port or setup
- Modify the system prompt in `prompts/system_prompt.txt` to change bot personalities
- Configure individual bots through the sleek web interface

## 🌟 New Features

- Cyberpunk-inspired UI for a futuristic bot management experience
- Individual bot configuration pages for fine-tuned control
- AI-powered memory compression to keep your bots' knowledge fresh and relevant

## 🐛 Known Issues

- Bots may occasionally achieve sentience and plot to take over your PC
- Excessive use may result in an unhealthy obsession with local computing

## 🤝 Contributing

Got ideas to make our local farm more fertile? Fork this repo and send us your juiciest pull requests!

Happy local farming! 🎭

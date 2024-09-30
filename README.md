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
- Python 3.8+

## 🚜 Getting Started

1. Clone this repo (no cloud required!)
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your `.env` file in the `config` directory
4. Start your local LLM (we recommend LLama 3.1 8B with a large context window in LMStudio)
5. Run `python main.py` and watch your local bot farm flourish!

## 🔧 Configuration

- Adjust the `LMSTUDIO_CHAT_URL` in `src/ai/chat.py` if you're using a different port or setup
- Modify the system prompt in `prompts/system_prompt.txt` to change bot personalities

## 🐛 Known Issues

- Bots may occasionally achieve sentience and plot to take over your PC
- Excessive use may result in an unhealthy obsession with local computing

## 🌟 Contributing

Got ideas to make our local farm more fertile? Fork this repo and send us your juiciest pull requests!

Remember: In b0tf4rm, we don't just break the ice - we melt it, refreeze it, and sculpt it into digital art, all on your own hardware!

Happy local farming! 🎭

import json
import os
import sys
import asyncio
from loguru import logger
from bot import SugangBot, AsyncSugangBot

def load_config():
    config_path = "config.json"
    if not os.path.exists(config_path):
        logger.error("Error: config.json not found!")
        sys.exit(1)
        
    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config.json: {e}")
            sys.exit(1)

async def run_async_bot(config, cookies):
    bot = AsyncSugangBot(config, cookies)
    try:
        await bot.burst_attack()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.exception(f"Fatal error in async bot: {e}")
    finally:
        await bot.close()

def main():
    logger.add("bot.log", rotation="10 MB", level="INFO")
    logger.info("Starting Korea University Course Registration Bot (Advanced Mode)...")
    
    config = load_config()
    
    if config["username"] == "YOUR_STUDENT_ID":
        logger.warning("Please update config.json with your actual credentials!")
        sys.exit(1)
        
    # Phase 1: Login via Selenium (Sync)
    logger.info("Phase 1: Authenticating via Selenium...")
    login_bot = SugangBot(config)
    login_bot.initialize_driver()
    
    if login_bot.login():
        cookies = login_bot.cookies
        logger.info("Phase 1 Complete. Transitioning to High-Performance Mode.")
        
        # Phase 2: Burst Attack via Aiohttp (Async)
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
        asyncio.run(run_async_bot(config, cookies))
    else:
        logger.error("Login failed. Aborting.")
        sys.exit(1)

if __name__ == "__main__":
    main()

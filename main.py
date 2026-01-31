import json
import os
import sys
from bot import KupidBot
from logger_config import setup_logger

def load_config():
    config_path = "config.json"
    if not os.path.exists(config_path):
        print("Error: config.json not found!")
        sys.exit(1)
        
    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing config.json: {e}")
            sys.exit(1)

def main():
    logger = setup_logger()
    logger.info("Starting Korea University Course Registration Bot...")
    
    config = load_config()
    
    if config["username"] == "YOUR_STUDENT_ID":
        logger.warning("Please update config.json with your actual credentials!")
        sys.exit(1)
        
    bot = KupidBot(config, logger)
    bot.run()

if __name__ == "__main__":
    main()

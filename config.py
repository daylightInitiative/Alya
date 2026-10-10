from dotenv import load_dotenv, find_dotenv
import logging
import json
import os

# special thanks to chatbot
log = logging.getLogger(__name__)

# check for the existance of the env file
if not os.path.exists("secrets.env"):
    env = open("secrets.env", 'w')
    env.close()

load_dotenv(find_dotenv("secrets.env"))

# returns the configuration as a json string
def _load_config() -> str:
    config_path = os.getenv("CONFIG_PATH", "")
    if not config_path:
        log.critical("USAGE: CONFIG_PATH=/path/to/config.json")
        quit(1)

    with open(config_path, "r") as f:
        config_data = json.load(f)
        return config_data


class Config():
    def __init__(self, data=None):
        config_path = os.getenv("CONFIG_PATH", "")
        log.warning("[+] Loaded configuration file: %s", config_path) # important for debugging to know which config

        self.patch(data)
        #self.patch_secrets()

    def patch(self, data):
        if data is not None and type(data) is dict:
            for field in data:
                if not getattr(self, field, None):
                    setattr(self, field, data[field])
    
    # def patch_secrets(self):
    #     # (avoiding putting the password and user in plaintext json files)
    #     user = os.getenv("DB_USER")
    #     if user:
    #         self.db_config["user"] = user

    #     password = os.getenv("DB_PASSWORD")
    #     if password:
    #         self.db_config["password"] = password

app_config = Config(data=_load_config())
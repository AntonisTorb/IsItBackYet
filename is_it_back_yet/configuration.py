import json
from pathlib import Path

class Config():

    def __init__(self, config_path: Path, cam: int = 0) -> None:
        '''Configuration class for the application.'''

        # Default configuration values.
        self.req_timeout_sec: int = 5
        self.loop_timeout_sec: int = 10
        self.max_users: int = 1000
        self.time_until_expiration_hours: int = 1

        try:
            with open(config_path, 'r') as f:
                self.__dict__ = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            print("Configuration file not found or corrupted. Creating with default values...")
            self._dump_config(config_path)


    def _dump_config(self, config_path: Path) -> None:
        '''Creates the `config.json` configuration file if it does not exist or is corrupted.'''

        with open(config_path, 'w') as f:
            config = self.__dict__
            json.dump(config, f, indent=4)

    def __repr__(self) -> str:
        return f'self.__dict'

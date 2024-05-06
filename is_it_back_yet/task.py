import logging
import time
from typing import Union

import discord

from .configuration import Config


class Task:

    def __init__(self, config: Config, url: str) -> None:
        '''Represents a url task for the bot and contains the user list.'''

        self.config: Config = config
        self.url: str = url

        self.users: list[Union[discord.User, discord.Member]] = []
        self.is_back: bool = False
        self.expiration_time_sec: float = time.perf_counter() + self.config.time_until_expiration_hours * 60 * 60
        self.logger: logging.Logger = logging.getLogger(__name__)


    def __repr__(self) -> str:
        return f'{self.__dict__}'
    

    def add_user(self, user: Union[discord.User, discord.Member]) -> str:
        '''Adds a user in the current task and returns the success message.
        If the max users have been reached or the request was duplicate, returns the appropriate failure message.
        '''

        if len(self.users) >= self.config.max_users:
            return "Error: Max number of users reached for this URL. Please try again later."
        elif user in self.users:
            return "Error: Duplicate request. Please don't spam or you could be blocked."
        else:
            self.users.append(user)
            self.expiration_time_sec = time.perf_counter() + self.config.time_until_expiration_hours * 60 * 60
            return f'''### You will be DMed when {self.url} is up!
*This task will expire in {self.config.time_until_expiration_hours} hours unless another user requests it.*'''
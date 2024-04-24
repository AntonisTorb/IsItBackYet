import logging
import time
from typing import Union

import discord


class Task:

    def __init__(self, url: str) -> None:
        self.url: str = url
        self.users: list[Union[discord.User, discord.Member]] = []
        self.max_users: int = 1000
        self.is_back: bool = False
        self.time_until_expiration_hours: int = 1 
        self.expiration_time_sec: float = time.perf_counter() + self.time_until_expiration_hours * 60 * 60
        self.logger = logging.getLogger(__name__)

    def __repr__(self) -> str:
        return f'{self.__dict__}'
    
    def add_user(self, user: Union[discord.User, discord.Member]) -> bool:
        '''Adds a user in the current task and returns `False`. If the max users have been reached, returns True.'''
        if len(self.users) >= self.max_users:
            return True
        elif user in self.users:
            return True
        else:
            self.users.append(user)
            return False
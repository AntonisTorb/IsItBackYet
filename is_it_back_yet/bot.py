from functools import wraps
import logging
import os
import time
import threading

import discord
from discord.ext import tasks
from discord.ext.commands import Bot, Context
from dotenv import load_dotenv
import requests

from .task import Task
from .utils import validate_url


class IsItBackYet:

    def __init__(self) -> None:
        '''Discord bot that keeps track of tasks, checks the task URLs and messages task users appropriatelly.'''

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
        }

        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.dm_messages = True
        self.bot = Bot("!", description="A bot that periodically checks if a url is up.", intents=intents)

        self.tasks: dict[str, Task] = {}
        self.req_timeout_sec: int = 5
        self.loop_timeout_sec: int = 10

        self.logger = logging.getLogger(__name__)

        try:
            load_dotenv()
            self.token: str = os.getenv("TOKEN")
            self.owner_id: int = int(os.getenv("OWNER_ID"))
        except Exception as e:
            self.logger.exception(e)


    def _single_check_url(self, url: str) -> int:
        '''Single `GET` request to the provided `url` that returns the `status code`.
        If the request times out, `0` will be returned.
        '''
        
        try:
            r = requests.get(url=url, headers=self.headers, timeout=self.req_timeout_sec)
        except requests.exceptions.Timeout:
            return 0
        return r.status_code


    def _check_url(self, url: str) -> None:
        '''Check a `url` with a `GET` request and update the related task's `is_back` property.'''

        status_code = self._single_check_url(url)
        if 199 < status_code < 300:
            self.tasks[url].is_back = True
    
    
    async def _message_users(self, task: Task, message: str) -> None:
        '''Message users and remove the URL from the tasks dictionary.'''

        for user in task.users:
            await user.send(message)
        

    def _validate_threads(self, threads: list[threading.Thread]) -> None:
        '''Stopping block to ensure all threads have finished before continuing'''
 
        while True:
            threads_alive: int = len(threads)
            for thread in threads:
                if not thread.is_alive():
                    threads_alive -= 1
            if threads_alive <= 0:
                break


    def run_bot(self) -> None:
        '''Command and task loop setup, as well as running the bot.'''

        def exception_handler_async(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    await func(*args, **kwargs)
                except Exception as e:
                    self.logger.exception(e)
            return wrapper


        @tasks.loop(seconds=self.loop_timeout_sec)
        @exception_handler_async
        async def _main_loop() -> None:
            '''Periodically checks the `urls` and messages users as necessary.'''

            if not self.tasks:
                return
            
            # Check urls in parallel.
            threads: list[threading.Thread] = []
            for url in self.tasks.keys():
                if self.tasks[url].expiration_time_sec <= time.perf_counter():
                    await self._message_users(self.tasks[url], f'Task for {url} has expired.')
                    continue
                t = threading.Thread(target=self._check_url, kwargs={"url":url})
                threads.append(t)
            for thread in threads:
                thread.start()

            self._validate_threads(threads)
            
            for url in self.tasks.keys():
                if not self.tasks[url].is_back:
                    continue
            
                await self._message_users(self.tasks[url], f'{url} is back up!')
            
            self.tasks = {url: value for url, value in self.tasks.items() if not value.is_back}
            
            print(self.tasks)
            
        @self.bot.command()
        @exception_handler_async
        async def check(ctx: Context, url: str):
            '''Command to register a `url` for periodic checking and message users as necessary.'''
            
            try:
                await ctx.message.delete()
            except (discord.Forbidden, discord.NotFound, discord.HTTPException):
                pass
            if ctx.author.bot:
                return

            if not validate_url(url):
                await ctx.author.send("Error: Invalid url provided.")
                return
            
            status_code = self._single_check_url(url)
            if 199 < status_code < 300:
                await ctx.author.send("Url appears to be up, please check your internet connection.")
                return
            
            added_success: bool = True
            if not url in self.tasks.keys():
                task = Task(url)
                task.users.append(ctx.author)
                self.tasks[url] = task
            else:
                added_success = self.tasks[url].add_user(ctx.author)
        
            if not added_success:
                await ctx.author.send("Error: Duplicate request or max number of users reached.")
                return

            await ctx.author.send(f'You will be DMed when {url} is up! This task will expire in {self.tasks[url].time_until_expiration_hours} hours.')


        @self.bot.command()
        @exception_handler_async
        async def close(ctx: Context) -> None:
            '''Command to close the bot connection if sent by the bot `owner`.'''

            if ctx.author.id == self.owner_id:
                await self.bot.close()
            else:
                await ctx.author.send("Unauthorized user, cannot close bot.")


        @self.bot.event
        @exception_handler_async
        async def on_ready() -> None:

            self.logger.info(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
            await _main_loop.start()

        self.bot.run(self.token)
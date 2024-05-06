import datetime
from pathlib import Path
import re


def maintain_log(log_path: Path|str, days: int) -> None:
    '''Function to maintain the log file by removing entries older than `days` days.'''

    if not log_path.exists():
        return
    
    new_log: str = ""
    add_rest: bool = False
    first_timestamp: bool = True

    with open(log_path, "r") as f:
        log_lines: list[str] = f.readlines()

    for index, line in enumerate(log_lines):
        parts: list[str] = line.split("|")
        if not len(parts) == 4:
            continue
        date: str = parts[0][:-4]
        timestamp: float = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp()

        cutoff: int = days * 24 * 60 * 60  # Remove logs older than `days` days.
        
        if datetime.datetime.now().timestamp() - timestamp > cutoff:
            first_timestamp = False
            continue
        if first_timestamp:  # First timestamp is not older than 30 days, no need to continue.
            return
        if not add_rest:
            add_rest = True
        
        if add_rest:
            rest: str = "".join(log_lines[index:])
            new_log = f'{new_log}{rest}'
            break

    with open(log_path, "w") as f:
        f.write(new_log)


def validate_url(url: str) -> bool:
    '''Validates a url based on the `django url validation regex`
    (https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py#L45)
    '''

    validator = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(validator, url) is not None

# hint for backup db, get users with the following by just storing id:
# user: discord.User =  await self.bot.fetch_user(ctx.author.id)

DISCORD_HELP_USERS = '''# Help:
`!check url    `: Add the `url` in a task to check for availability and message you once it's back.
'''

DISCORD_HELP_OWNER = '''# Help:
`!check url                  `: Add the `url` in a task to check for availability and message you once it's back.
`!close                      `: Close application.
`!setexpirationhours hours   `: Set the task expiration time in hours.
`!setlooptimeout sec         `: Set how often the checking loop runs in seconds.
`!setmaxusers amount         `: Set the maximum amount of users for all tasks.
`!setreqtimeout sec          `: Set the GET request timeout in seconds.
'''
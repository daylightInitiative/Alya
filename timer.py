import re
import heapq
import datetime
from discord.ext import commands

# since we are using discord's AutoShardedBot a variable like this won;t cause problems
timers_heap = []

def load_timers():
    pass

def duration_to_string(total_seconds) -> str:
    td = datetime.timedelta(seconds=total_seconds)
    data = {}

    data["weeks"] = td.days // 7
    data["days"] = td.days % 7

    data["hours"], remainder = divmod(td.seconds, 3600)
    data["minutes"], data["seconds"] = divmod(remainder, 60)

    result_str = ""
    for index, (interval, value) in enumerate(data.items()):
        #print(f"index: {index}\tlength:{len(data)}")
        if value != 0:
            result_str += f"{value} {interval}"
        else:
            continue
        if index < len(data) - 1:
            result_str += ", "

    return result_str

# manages the minheap timer scheduling for each user
class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument: str) -> float:
        pattern = re.compile(r'(\d+)\s*(ms|s|m|h|d|w|sec|min|hour|day|week)s?', re.IGNORECASE)
        matches = pattern.findall(argument)
        
        if not matches:
            raise commands.BadArgument("Invalid time format, use '1d5ms' or '5 days' all the way up to weeks.")
            
        # units mapped to their abbreviations
        time_units = {
            'ms': 0.001,
            's': 1, 'sec': 1,
            'm': 60, 'min': 60,
            'h': 3600, 'hour': 3600,
            'd': 86400, 'day': 86400,
            'w': 604800, 'week': 604800
        }
        
        total_seconds = 0
        for value, unit in matches:
            unit_lower = unit.lower()
            if unit_lower in time_units:
                total_seconds += int(value) * time_units[unit_lower]
                
        return total_seconds
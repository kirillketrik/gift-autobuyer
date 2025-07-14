import asyncio
import logging
import random
from typing import Optional, Union

Number = Union[int, float]


def check_number_bounds(number: Number, min_value: Optional[Number], max_value: Optional[Number]) -> bool:
    return (min_value < number if min_value else True) and (max_value > number if max_value else True)


async def sleep_random(a: int, b: int) -> None:
    sleep_time = round(random.randint(a * 1000, b * 1000) / 1000, 3)
    logging.info(f'Pause for {sleep_time}s')
    await asyncio.sleep(sleep_time)

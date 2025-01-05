import os
import random

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    """
    Handles a request to execute iterations of a while loop until a
    randomly generated value meets a specific condition.

    :return: A JSON response containing the result of the loop execution.
    """
    n = 0

    val = get_random_number(500_000, 1_000_000)
    while n < val:
        n += 1
    return {f"Counted till random number: {val} "}

def get_random_number(min_value: int, max_value:int) -> int:
    """
    Generates a random integer between min_value and max_value (inclusive),
    and returns its square.

    :param min_value:
    :param max_value:
    :return: A tuple containing the random integer and its square.
    """
    random_number = random.randint(min_value, max_value)
    return random_number

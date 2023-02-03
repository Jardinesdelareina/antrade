from time import strftime
from random import Random

# Генерация id: текущее время + рандомное число
def generate_id() -> int:
    random_number = Random()
    random_id = '{time_now}{random_int}'.format(
        time_now=strftime('%Y%m%d%H%M%S'),
        random_int=random_number.randint(10, 99)
    )
    return random_id

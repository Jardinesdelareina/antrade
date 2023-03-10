# Расчет количества знаков после запятой у числа типа float
def round_float(num: float) -> int:
    num_str = str(num)
    counter = 0
    for i in num_str[::-1]:
        if i == '.':
            break
        else:
            counter += 1
    return counter

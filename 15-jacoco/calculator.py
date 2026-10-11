def classify(number):
    if number > 0:
        return "positive"
    elif number < 0:
        return "negative"
    else:
        return "zero"


def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None


def is_even(number):
    return number % 2 == 0


def unused_dead_code():
    return "dead"


def wrong_average(a, b):
    # Intentionally wrong: adds instead of averaging.
    return a + b

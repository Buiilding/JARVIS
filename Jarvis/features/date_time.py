import datetime
import inflect

def date():
    """
    Just return date as string
    :return: date if success, False if fail
    """
    try:
        date = datetime.datetime.now().strftime("%b %d %Y")
    except Exception as e:
        print(e)
        date = False
    return date


def time():
    """
    Just return time as string
    :return: time if success, False if fail
    """
    hour = int(datetime.datetime.now().hour)
    minute = int(datetime.datetime.now().minute)
    p = inflect.engine()
    suffix = "AM"
    if hour >= 12:
        suffix = "PM"
        if hour > 12:
            hour_12 = hour - 12
        else:
            hour_12 = 12
    elif hour == 0:
        hour_12 = 12
    else:
        hour_12 = hour

    hour_word = p.number_to_words(hour_12).replace("-", " ")

    if minute == 0:
        minute_part = "o'clock"
    else:
        minute_word = p.number_to_words(minute).replace("-", " ")
        minute_part = minute_word
    if minute == 1:
        time_string = f"{hour_word} and {minute_part} minute {suffix}"
    elif minute == 0:
        time_string = f"{hour_word} o'clock {suffix}"
    else: 
        time_string = f"{hour_word} and {minute_part} minutes {suffix}"

    return time_string
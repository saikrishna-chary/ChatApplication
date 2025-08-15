from datetime import datetime, timedelta


def format_timestamp(timestamp):
    now = datetime.now()
    if timestamp.date() == now.date():
        day = "Today"
    elif timestamp.date() == (now - timedelta(days=1)).date():
        day = "Yesterday"
    else:
        day = timestamp.strftime("%b %d, %Y")

    time = timestamp.strftime("%I:%M %p")
    return f"{day} - {time}"

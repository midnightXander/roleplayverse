from django.utils import timezone

def seconds_difference(datetime):
    now = timezone.now()
    print(now)
    difference = now - datetime
    days = difference.days
    seconds = difference.seconds
    hours = seconds // 3600

    return seconds
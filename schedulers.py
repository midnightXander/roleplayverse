import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

def my_task():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'para.settings'
    try:
        # call_command('management_command')

        print('Task completed')
    except Exception as e:
        print(f'An error occured {e}')



def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(my_task, 'cron', day_of_week = '*', hour = 20, minute = 0)
    scheduler.start()


if __name__ == '__main__':
    start()
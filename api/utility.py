from .models import PushSubscription
from pywebpush import webpush, WebPushException
from django.contrib.auth.models import User

from dotenv import load_dotenv
import os,json


def send_push_notification(subscription :PushSubscription, message):
    # logic to send a push notification using the subscription data
    # try:
    #     subscription = PushSubscription.objects.get(user=user)
    # except:
    #     print(f"Subscription does not exist for user {user}.")
    #     return    

    try: 
        webpush(
            subscription_info= {
                'endpoint': subscription.endpoint,
                'keys': {
                    'p256dh': subscription.p256dh_key,
                    'auth': subscription.auth_key
                }
            },
            data=json.dumps(message),
            vapid_private_key=os.environ.get('VAPID_PRIVATE_KEY'),
            vapid_claims={
                'sub': 'mailto:alexngaikama913@gmail.com' 
                }
        )
    except WebPushException as ex:
        print(f"Failed to send notification: {ex}")
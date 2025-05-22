from .models import PushSubscription
from pywebpush import webpush, WebPushException
from django.contrib.auth.models import User
from core import emails
from dotenv import load_dotenv
import os,json


def send_push_notification(subscription :PushSubscription, message, user:User = None):
    # logic to send a push notification using the subscription data
    # try:
    #     subscription = PushSubscription.objects.get(user=user)
    # except:
    #     print(f"Subscription does not exist for user {user}.")
    #     return    


    if subscription == None:
        print(f"Subscription does not exist for user.")
        try:
            emails.send_email(
            recipient_email = user.email,
            title = {message['title']},
            subject = {message['title']},
            body = f"""
            <h2>Salut {user},</h2>
            <p><strong>{message['body']}</strong></p>
            <a href = '{message['url']}' class = "button">Voir</a>
            """,
            #language = ""
            )
        except:
            print(f"Failed to send email: {ex}")
            return
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
        print(f"Notif sent to {subscription.user}.")
    # except WebPushException as ex:
    #     print(f"Failed to send notification: {ex}")
    except Exception as ex:
        print(f"Failed to send notification: {ex}")
        try:
            if user is not None:
                emails.send_email(
                recipient_email = user.email,
                title = {message['title']},
                subject = {message['title']},
                body = f"""
                <h2>Salut {user},</h2>
                <p><strong>{message['body']}</strong></p>
                <a href = '{message['url']}' class = "button">Voir</a>
                """,
                #language = user.language
                )
        except Exception as ex:
            print(f"Failed to send email: {ex}")
               
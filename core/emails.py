import smtplib
from email.message import EmailMessage
import ssl
from dotenv import load_dotenv
import os
load_dotenv()


rpv_email = os.getenv("GMAIL_ADRESS")
rpv_email_pwd = os.environ.get("GMAIL_PASSWORD")


EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notification Email</title>
    <style>
        /* General styles */
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f7;
            color: #333;
        }
        .email-container {
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .email-header {
            background-color: #F97316;
            color: #ffffff;
            text-align: center;
            padding: 20px;
        }
        .email-header h1 {
            margin: 0;
            font-size: 24px;
        }
        .email-body {
            padding: 20px;
        }
        .email-body h2 {
            font-size: 20px;
            color: #F97316;
        }
        .email-body p {
            line-height: 1.6;
            margin: 10px 0;
        }
        .email-footer {
            text-align: center;
            padding: 20px;
            font-size: 14px;
            color: #777;
            background-color: #f4f4f7;
        }
        .email-footer a {
            color: #F97316;
            text-decoration: none;
        }
        .button {
            display: inline-block;
            background-color: #F97316;
            color: #ffffff;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 16px;
            margin-top: 20px;
        }
        .button:hover {
            background-color: #e05d0f;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="email-header">
            <h1>RolePlay Verse</h1>
        </div>

        <!-- Body -->
        <div class="email-body">
            <h2>Hello, {{ user_name }}</h2>
            <p>We hope this message finds you well! Here’s a quick notification for you:</p>
            <p><strong>{{ notification_message }}</strong></p>
            <p>If you need to take action, click the button below:</p>
            <a href="{{ action_url }}" class="button">Take Action</a>
            <p>If you have any questions, feel free to reply to this email or contact our support team.</p>
        </div>

        <!-- Footer -->
        <div class="email-footer">
            <p>Merci de faire partie de RolePlay Verse!</p>
            <p><a href="https://roleplayverse.live">Visiter la plateforme</a></p>
        </div>
    </div>
</body>
</html>
"""


def send_email(recipient_email:str,title:str, subject:str,body:str,language:str='en'):
    email = EmailMessage()
    email["Subject"] = subject
    email["From"] = rpv_email
    #html_content = EMAIL_TEMPLATE.replace("{{ user_name }}",user_name).replace("{{ notification_message }}",body).replace("{{ action_url }}",action_url)
    html_content = f"""
<!DOCTYPE html>
<html lang="{language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f7;
                color: #333;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .email-header {{
                background-color: #F97316;
                color: #ffffff;
                text-align: center;
                padding: 20px;
            }}
            .email-header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .email-body {{
                padding: 20px;
            }}
            .email-body h2 {{
                font-size: 20px;
                color: #F97316;
            }}
            .email-body p {{
                line-height: 1.6;
                margin: 10px 0;
            }}
            .email-footer {{
                text-align: center;
                padding: 20px;
                font-size: 14px;
                color: #777;
                background-color: #f4f4f7;
            }}
            .email-footer a {{
                color: #F97316;
                text-decoration: none;
            }}
            .button {{
                display: inline-block;
                background-color: #F97316;
                color: #ffffff;
                text-decoration: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 16px;
                margin-top: 20px;
            }}
            .button:hover {{
                background-color: #e05d0f;
            }}
        </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="email-header">
            <h1>RolePlay Verse</h1>
        </div>

        <!-- Body -->
        <div class="email-body">
            {body}
        </div>

        <!-- Footer -->
        <div class="email-footer">
            <p>Merci de faire partie de RolePlay Verse!</p>
            <p><a href="https://roleplayverse.live">Visiter la plateforme</a></p>
        </div>
    </div>
</body>
</html>
    
"""
    email.add_alternative(html_content,subtype="html")
    
    with smtplib.SMTP_SSL("smtp.gmail.com",465,context=ssl.create_default_context()) as smtp_server:
        smtp_server.login(rpv_email,rpv_email_pwd)
        email["To"] = recipient_email

        smtp_server.send_message(email)
        del email["To"]
        del email["From"]
        del email["Subject"]
#!/usr/bin/env python3
from twilio.rest import Client

import os

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

try:
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
        content_variables='{"1":"12/1","2":"3pm"}',
        to='whatsapp:+56950915617'
    )
    
    print(f"Message sent successfully!")
    print(f"Message SID: {message.sid}")
    print(f"Status: {message.status}")
    print(f"To: {message.to}")
    print(f"From: {message.from_}")
    
except Exception as e:
    print(f"Error sending message: {str(e)}")
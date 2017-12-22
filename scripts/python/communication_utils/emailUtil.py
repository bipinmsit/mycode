"""
This call sends a message via MailJet.
"""
from mailjet_rest import Client
import os
import sys
import logging
API_KEY = os.environ['MJ_APIKEY_PUBLIC']
API_SECRET = os.environ['MJ_APIKEY_PRIVATE']


def send_email(subject= "Notification", body=""):
    if not API_KEY or not API_SECRET:
        logging.error("MJ_APIKEY_PUBLIC and MJ_APIKEY_PRIVATE environment variables not set")
        sys.exit(1)
    mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "admin@aspecscire.com",
                    "Name": "Admin Aspec Scire"
                },
                "To": [
                    {
                        "Email": "photogrammetry@aspecscire.com",
                        "Name": "Photogrammetry Team"
                    }
                ],
                "Subject": subject,
                "TextPart": body,
                "HTMLPart": body
            }
        ]
    }
    result = mailjet.send.create(data=data)
    logging.info(result.json())

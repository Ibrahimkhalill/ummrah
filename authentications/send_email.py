import os
import requests
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()
def send_simple_message():
    return requests.post(
        "https://api.mailgun.net/v3/nusukey-omra.com/messages",
        auth=("api", os.getenv('API_KEY', 'API_KEY')),
        data={
            "from": "Mailgun Sandbox <postmaster@nusukey-omra.com>",
            "to": "Md Ibrahim Khalil <contact@nusukey-omra.com>",
            "subject": "Hello Md Ibrahim Khalil",
            "text": "Congratulations Md Ibrahim Khalil, you just sent an email with Mailgun! You are truly awesome!"
        }
    )
if __name__ == "__main__":
    response = send_simple_message()
    print(response.status_code)
    print(response.text)
    if response.status_code == 200:
        print("Email sent successfully!")
    else:
        print("Failed to send email.")
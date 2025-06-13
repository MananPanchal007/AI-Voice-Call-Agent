from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment variables
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
ngrok_url = os.getenv('NGROK_URL')  # Get ngrok URL from environment

if not all([account_sid, auth_token, ngrok_url]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Initialize Twilio client
client = Client(account_sid, auth_token)

def make_call(to_number: str, from_number: str, ngrok_url: str):
    """
    Make a call using Twilio with AI conversation handling
    
    Args:
        to_number (str): The number to call (with country code)
        from_number (str): Your Twilio number (with country code)
        ngrok_url (str): Your ngrok URL
    """
    try:
        # Remove trailing slash from ngrok_url if present
        ngrok_url = ngrok_url.rstrip('/')
        
        # Use our own FastAPI endpoint
        voice_url = f'{ngrok_url}/twiml/voice'
        
        print(f"Using voice URL: {voice_url}")
        
        # Make the call with custom parameters
        call = client.calls.create(
            to=to_number,
            from_=from_number,
            url=voice_url,  # Use our FastAPI endpoint
            status_callback=f'{ngrok_url}/twiml/status',
            status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
            status_callback_method='POST',
            machine_detection='Enable',  # Enable answering machine detection
            record=True,  # Record the call
            recording_status_callback=f'{ngrok_url}/twiml/recording',  # Get recording status
            recording_status_callback_event=['completed'],
            recording_status_callback_method='POST'
        )
        print(f"Call initiated! Call SID: {call.sid}")
        return call.sid
    except TwilioRestException as e:
        print(f"Twilio Error: {str(e)}")
        print(f"Error Code: {e.code}")
        print(f"More Info: {e.uri}")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Get values from environment variables
    TO_NUMBER = os.getenv('TO_NUMBER', "+19998882323")  # The number to call
    FROM_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')  # Your Twilio number
    
    if not FROM_NUMBER:
        raise ValueError("TWILIO_PHONE_NUMBER not set in environment variables")
    
    print(f"Making call from {FROM_NUMBER} to {TO_NUMBER}")
    print(f"Using ngrok URL: {ngrok_url}")
    
    # Make the call
    call_sid = make_call(TO_NUMBER, FROM_NUMBER, ngrok_url)
    
    if call_sid:
        print("Call was successful!")
    else:
        print("Failed to initiate call.")

from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse, JSONResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import openai
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="AI Call Agent")

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

# Create conversations directory if it doesn't exist
os.makedirs('conversations', exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint to verify the server is running"""
    return JSONResponse({
        "status": "running",
        "message": "AI Call Agent is active",
        "endpoints": {
            "voice": "/twiml/voice",
            "process": "/twiml/process",
            "status": "/twiml/status"
        }
    })

def save_conversation(phone_number: str, message: str, response: str):
    """Save conversation to a JSON file"""
    filename = f'conversations/{phone_number}_{datetime.now().strftime("%Y%m%d")}.json'
    
    # Load existing conversation if it exists
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            conversation = json.load(f)
    else:
        conversation = []
    
    # Add new message and response
    conversation.append({
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'response': response
    })
    
    # Save updated conversation
    with open(filename, 'w') as f:
        json.dump(conversation, f, indent=2)

def get_ai_response(message: str, conversation_history: list = None) -> str:
    """Get response from OpenAI"""
    try:
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant. Keep responses concise and natural for phone conversations."}
        ]
        
        # Add conversation history if available
        if conversation_history:
            for entry in conversation_history[-5:]:  # Last 5 exchanges
                messages.append({"role": "user", "content": entry['message']})
                messages.append({"role": "assistant", "content": entry['response']})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting AI response: {str(e)}")
        return "I apologize, but I'm having trouble processing that right now."

@app.post("/twiml/voice")
async def handle_voice(request: Request):
    """Handle incoming voice calls"""
    try:
        response = VoiceResponse()
        
        # Get the caller's phone number
        form_data = await request.form()
        from_number = form_data.get('From', 'unknown')
        print(f"Received call from: {from_number}")
        
        # Custom greeting that identifies the AI assistant
        greeting = """
        Hello! This is your AI Assistant. 
        I'm here to help you with any questions or tasks you have.
        How can I assist you today?
        """
        response.say(greeting, voice='Polly.Amy', language='en-GB')  # Using British English for a more natural sound
        
        # Gather user input
        gather = Gather(
            input='speech',
            action='/twiml/process',
            method='POST',
            speech_timeout='auto',
            speech_model='phone_call',
            language='en-US'
        )
        response.append(gather)
        
        # If no input is received, repeat the greeting
        response.redirect('/twiml/voice')
        
        return Response(content=str(response), media_type='application/xml')
    except Exception as e:
        print(f"Error in handle_voice: {str(e)}")
        response = VoiceResponse()
        response.say("I'm sorry, but I'm having technical difficulties. Please try again later.")
        return Response(content=str(response), media_type='application/xml')

@app.post("/twiml/process")
async def process_speech(request: Request):
    """Process speech input and respond"""
    try:
        response = VoiceResponse()
        form_data = await request.form()
        
        # Get the speech input
        speech_result = form_data.get('SpeechResult', '')
        from_number = form_data.get('From', 'unknown')
        
        print(f"Received speech from {from_number}: {speech_result}")
        
        if speech_result:
            # Get AI response
            ai_response = get_ai_response(speech_result)
            print(f"AI Response: {ai_response}")
            
            # Save conversation
            save_conversation(from_number, speech_result, ai_response)
            
            # Respond to the user
            response.say(ai_response)
            
            # Continue gathering input
            gather = Gather(
                input='speech',
                action='/twiml/process',
                method='POST',
                speech_timeout='auto',
                speech_model='phone_call',
                language='en-US'
            )
            response.append(gather)
        else:
            response.say("I didn't catch that. Could you please repeat?")
            gather = Gather(
                input='speech',
                action='/twiml/process',
                method='POST',
                speech_timeout='auto',
                speech_model='phone_call',
                language='en-US'
            )
            response.append(gather)
        
        return Response(content=str(response), media_type='application/xml')
    except Exception as e:
        print(f"Error in process_speech: {str(e)}")
        response = VoiceResponse()
        response.say("I'm sorry, but I'm having technical difficulties. Please try again later.")
        return Response(content=str(response), media_type='application/xml')

@app.post("/twiml/status")
async def handle_status(request: Request):
    """Handle call status updates"""
    try:
        form_data = await request.form()
        call_sid = form_data.get('CallSid')
        call_status = form_data.get('CallStatus')
        print(f"Call {call_sid} status: {call_status}")
        return PlainTextResponse("OK")
    except Exception as e:
        print(f"Error in handle_status: {str(e)}")
        return PlainTextResponse("Error")

@app.post("/twiml/recording")
async def handle_recording(request: Request):
    """Handle call recording status updates"""
    try:
        form_data = await request.form()
        recording_sid = form_data.get('RecordingSid')
        recording_url = form_data.get('RecordingUrl')
        recording_status = form_data.get('RecordingStatus')
        call_sid = form_data.get('CallSid')
        
        print(f"Recording {recording_sid} for call {call_sid} status: {recording_status}")
        print(f"Recording URL: {recording_url}")
        
        return PlainTextResponse("OK")
    except Exception as e:
        print(f"Error in handle_recording: {str(e)}")
        return PlainTextResponse("Error")

if __name__ == "__main__":
    print("Starting AI Call Agent server...")
    print("Available endpoints:")
    print("- GET  /")
    print("- POST /twiml/voice")
    print("- POST /twiml/process")
    print("- POST /twiml/status")
    print("- POST /twiml/recording")
    uvicorn.run(app, host="0.0.0.0", port=8000) 
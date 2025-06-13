# 🤖 AI Call Agent

An intelligent phone call assistant powered by OpenAI's GPT-3.5 that can handle natural conversations over phone calls using Twilio.

## 🌟 Features

- 📞 Make and receive phone calls using Twilio
- 🗣️ Natural voice conversations with AI
- 🧠 Powered by OpenAI's GPT-3.5
- 💾 Automatic conversation logging
- 🎙️ Call recording capabilities
- 🤖 Customizable AI responses

## 🛠️ Prerequisites

- Python 3.8+
- Twilio Account
- OpenAI API Key
- ngrok (for local development)

## 📋 Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
OPENAI_API_KEY=your_openai_api_key
NGROK_URL=your_ngrok_url
TO_NUMBER=default_number_to_call
```

## 🚀 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-call-agent
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Running the Application

1. Start the FastAPI server:
```bash
python twiml_handler.py
```

2. In a new terminal, start ngrok:
```bash
ngrok http 8000
```

3. Copy the ngrok HTTPS URL (including `.app` suffix) and update your `.env` file:
```env
NGROK_URL=https://your-ngrok-url.ngrok-free.app
```

4. Make a test call:
```bash
python call.py
```

## 📁 Project Structure

```
ai-call-agent/
├── twiml_handler.py    # FastAPI server and TwiML handling
├── call.py            # Call initiation script
├── requirements.txt   # Python dependencies
├── .env              # Environment variables
└── conversations/    # Call conversation logs
```

## 🔧 API Endpoints

- `GET /` - Health check endpoint
- `POST /twiml/voice` - Handle incoming calls
- `POST /twiml/process` - Process speech input
- `POST /twiml/status` - Handle call status updates
- `POST /twiml/recording` - Handle recording status updates

## 📝 Conversation Logging

All conversations are automatically logged in the `conversations/` directory with timestamps and phone numbers.

## 🔒 Security Notes

- Never commit your `.env` file
- Keep your API keys secure
- Use HTTPS for all webhook URLs
- Regularly rotate your API keys

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Troubleshooting

If you encounter the "Url is not a valid URL" error:
1. Ensure your ngrok URL includes the `.app` suffix
2. Verify the URL is properly formatted in your `.env` file
3. Make sure ngrok is running and accessible
4. Check that your FastAPI server is running on port 8000

## 📞 Support

For support, please open an issue in the repository or contact the maintainers.


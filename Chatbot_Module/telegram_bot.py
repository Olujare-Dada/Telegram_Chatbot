from fastapi import FastAPI, Request
import openai
import requests



# Initialize FastAPI app
app = FastAPI()

# Set OpenAI API key (replace with your actual key)
openai.api_key = "your-openai-api-key"

# Set Telegram bot token
TELEGRAM_TOKEN = "your-telegram-bot-token"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Function to generate LLM response
def get_llm_response(prompt: str):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Function to send a message to Telegram
def send_message(chat_id: int, text: str):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# Route to receive Telegram updates (webhook)
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    # Extract chat ID and message text from the request
    chat_id = data["message"]["chat"]["id"]
    user_message = data["message"]["text"]

    # Query the LLM with the user's message
    bot_response = get_llm_response(user_message)

    # Send the LLM-generated response back to the user
    send_message(chat_id, bot_response)

    return {"status": "ok"}



"""
activate_telegram_bot.py

This module sets up a Telegram bot that interacts with users by responding to their messages. It integrates with a chatbot API to provide informative responses based on user queries. The bot listens for messages and commands, facilitating a conversational experience.

Usage:
    This module should be run as the main program. It initializes the Telegram bot and starts listening for incoming messages and commands.

Main Functions:
- start: Handles the /start command, sending a welcome message to users.
- bot_response: Responds to user messages by generating replies from the chatbot.

Webhook Configuration:
    The module includes instructions for setting up a webhook to receive updates from Telegram.

"""


import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from answer_query import get_chatbot_response


# Paste in browser to set up WEBHOOK:
# https://api.telegram.org/bot7189642338:AAGCNZfifibk69do59EgMiZWt5_YQh2dJJ0/setWebhook?url=https://6cf9-70-26-93-16.ngrok-free.app/7189642338:AAGCNZfifibk69do59EgMiZWt5_YQh2dJJ0

# Check if WEBHOOK has been setup:
# https://api.telegram.org/bot7189642338:AAGCNZfifibk69do59EgMiZWt5_YQh2dJJ0/getWebhookInfo


# Load environment variables from .env file
load_dotenv()

# Get the bot token from the environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


# Define a start command handler to greet the user when they use /start
async def start(update: Update, context):
    """
    Handles the /start command by sending a welcome message to the user.

    Args:
        update (Update): Incoming update containing the message.
        context (Context): The context for the command, including data related to the update.
    """
    await update.message.reply_text('Hello! I am your StudyBot for your exam. Send me a message and I will give you the correct response from your material')



# Define a message handler that echoes any message the user sends
async def bot_response(update: Update, context):
    """
    Handles incoming messages and generates a response using the chatbot.

    Args:
        update (Update): Incoming update containing the user's message.
        context (Context): The context for the message, including data related to the update.
    """
    
    user_message = update.message.text
    bot_response = get_chatbot_response(user_message)
    await update.message.reply_text(bot_response)




# Set up the bot
def main():
    
    """
    Sets up the Telegram bot and starts listening for updates.

    Initializes the application, adds command and message handlers, and runs the webhook
    to handle incoming messages.
    """
    
    # Initialize the Application (formerly Updater), which connects to the Telegram API
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add a handler for the /start command
    application.add_handler(CommandHandler('start', start))

    # Add a handler for any text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_response))

    # Start webhook for updates (messages)
    PORT = int(os.environ.get('PORT', '8443'))
    WEBHOOK_URL = f"https://6cf9-70-26-93-16.ngrok-free.app/{TELEGRAM_TOKEN}"


    # Start the webhook
    application.run_webhook(
        listen='0.0.0.0',
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=WEBHOOK_URL
    )

if __name__ == '__main__':
    main()

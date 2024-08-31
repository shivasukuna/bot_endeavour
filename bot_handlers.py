from telegram.ext import CommandHandler, MessageHandler, Filters

# Function to start the bot and request passcode
def start(update, context):
    chat_id = update.message.chat_id
    if chat_id in authorized_users:
        context.bot.send_message(chat_id=chat_id, text="Welcome back!")
    else:
        context.bot.send_message(chat_id=chat_id, text="Please enter the passcode to access the bot.")

# Handle passcode input
def handle_message(update, context):
    chat_id = update.message.chat_id
    text = update.message.text
    
    if chat_id not in authorized_users:
        if text == PASSCODE:
            authorized_users.add(chat_id)
            context.bot.send_message(chat_id=chat_id, text="Access granted!")
        else:
            context.bot.send_message(chat_id=chat_id, text="Incorrect passcode. Try again.")
    else:
        # Handle other messages after authorization
        context.bot.send_message(chat_id=chat_id, text="You're already authorized. How can I help?")

# Command handlers
def add_wallet(update, context):
    chat_id = update.message.chat_id
    if chat_id not in authorized_users:
        context.bot.send_message(chat_id=chat_id, text="You need to be authorized to use this command.")
        return

    if len(context.args) < 2:
        context.bot.send_message(chat_id=chat_id, text="Usage: /add <label> <wallet_address>")
        return

    label, wallet_address = context.args[0], context.args[1]
    if chat_id not in user_data:
        user_data[chat_id] = {}
    
    user_data[chat_id][label] = {"address": wallet_address, "status": "active"}
    context.bot.send_message(chat_id=chat_id, text=f"Added wallet '{label}' with address '{wallet_address}'.")

def remove_wallet(update, context):
    chat_id = update.message.chat_id
    if chat_id not in authorized_users:
        context.bot.send_message(chat_id=chat_id, text="You need to be authorized to use this command.")
        return

    if len(context.args) < 1:
        context.bot.send_message(chat_id=chat_id, text="Usage: /remove <label>")
        return

    label = context.args[0]
    if chat_id in user_data and label in user_data[chat_id]:
        del user_data[chat_id][label]
        context.bot.send_message(chat_id=chat_id, text=f"Removed wallet '{label}'.")
    else:
        context.bot.send_message(chat_id=chat_id, text=f"Label '{label}' not found.")

def pause_wallet(update, context):
    chat_id = update.message.chat_id
    if chat_id not in authorized_users:
        context.bot.send_message(chat_id=chat_id, text="You need to be authorized to use this command.")
        return

    if len(context.args) < 1:
        context.bot.send_message(chat_id=chat_id, text="Usage: /pause <label>")
        return

    label = context.args[0]
    if chat_id in user_data and label in user_data[chat_id]:
        user_data[chat_id][label]["status"] = "paused"
        context.bot.send_message(chat_id=chat_id, text=f"Paused tracking for label '{label}'.")
    else:
        context.bot.send_message(chat_id=chat_id, text=f"Label '{label}' not found.")

def list_wallets(update, context):
    chat_id = update.message.chat_id
    if chat_id not in authorized_users:
        context.bot.send_message(chat_id=chat_id, text="You need to be authorized to use this command.")
        return

    if chat_id in user_data and user_data[chat_id]:
        message = "Tracking wallets:\n"
        for label, wallet_info in user_data[chat_id].items():
            status = wallet_info["status"]
            message += f"Label: {label}, Address: {wallet_info['address']}, Status: {status}\n"
        context.bot.send_message(chat_id=chat_id, text=message)
    else:
        context.bot.send_message(chat_id=chat_id, text="No wallets are being tracked.")

# Initialize the bot with the token and set up command handlers
from telegram.ext import Updater

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Command handlers
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('add', add_wallet))
dispatcher.add_handler(CommandHandler('remove', remove_wallet))
dispatcher.add_handler(CommandHandler('pause', pause_wallet))
dispatcher.add_handler(CommandHandler('list', list_wallets))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Start the bot
updater.start_polling()

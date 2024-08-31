from flask import Flask, request, jsonify
from telegram import Bot
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()
TOKEN = os.getenv('TOKEN')
PASSCODE = os.getenv('PASSCODE')

# Initialize Flask app
app = Flask(__name__)
bot = Bot(token=TOKEN)

# Dictionary to store user data and authorized users
user_data = {}
authorized_users = set()

# Import bot handlers from the bot_handlers module
from bot_handlers import start, handle_message, add_wallet, remove_wallet, pause_wallet, list_wallets

# Function to get the current price and market cap of a token
def get_token_info(token_id):
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        market_cap = data['market_data']['market_cap']['usd']
        price = data['market_data']['current_price']['usd']

        if market_cap >= 1_000_000:
            market_cap_formatted = f"{market_cap / 1_000_000:.2f}M"
        elif market_cap >= 1_000:
            market_cap_formatted = f"{market_cap / 1_000:.2f}K"
        else:
            market_cap_formatted = f"{market_cap:.2f}"

        return market_cap_formatted, price

    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching token info: {e}")
        return None, None

# Route to handle Telegram webhook updates
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    wallet_address = data.get('address', '')
    transaction_type = data.get('type', '')
    token_name = data.get('token', '')
    token_id = data.get('token_id', '')
    amount = float(data.get('amount', '0'))
    coin_address = data.get('coin_address', '')

    # This function should be defined or imported.
    solana_price = get_solana_price()
    
    if not solana_price:
        return jsonify({"status": "error", "message": "Failed to fetch Solana price"}), 500

    usd_value = solana_price * amount
    market_cap, price = get_token_info(token_id)
    
    if not market_cap or not price:
        return jsonify({"status": "error", "message": "Failed to fetch token info"}), 500

    for user_id, wallets in user_data.items():
        for label, wallet_info in wallets.items():
            if wallet_info['address'] == wallet_address and wallet_info['status'] == 'active':
                if transaction_type == "buy":
                    message = (
                        f"📈 Buy detected!\n"
                        f"Wallet '{label}' brought {token_name} for Solana {amount:.2f} worth ${usd_value:.2f}\n"
                        f"MarketC = {market_cap}\n"
                        f"Price = {price}\n\n"
                        f"Ca = `{coin_address}`"
                    )
                elif transaction_type == "sell":
                    message = (
                        f"📉 Sell detected!\n"
                        f"Wallet '{label}' sold {token_name} for Solana {amount:.2f} worth ${usd_value:.2f}\n"
                        f"MarketC = {market_cap}\n"
                        f"Price = {price}\n\n"
                        f"Ca = `{coin_address}`"
                    )
                else:
                    message = (
                        f"🔔 Transaction detected!\n"
                        f"Wallet '{label}' transaction: {transaction_type}\n"
                        f"Token: {token_name} for Solana {amount:.2f} worth ${usd_value:.2f}\n"
                        f"MarketC = {market_cap}\n"
                        f"Price = {price}\n\n"
                        f"Ca = `{coin_address}`"
                    )

                bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')

    return jsonify({"status": "success"}), 200

# Start Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

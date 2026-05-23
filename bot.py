import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# =========================
# CONFIG (SECURE)
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
STAFF_CHAT_ID = -1003941910641

BUY_LINK = "https://v2store.sell.app/"
TELEGRAM_LINK = "https://t.me/cornballsv2"
REFERRAL_LINK = "https://v2store.sell.app/affiliate"

# =========================
# MEMORY
# =========================

redeeming_users = set()
contacting_users = set()
checking_status_users = set()

orders = {}
order_status = {}

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
        "Welcome 👋",
        reply_markup=main_menu()
    )

# =========================
# BUTTONS
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back":
        await query.message.reply_text("🏠 Main Menu", reply_markup=main_menu())
        return

    if query.data == "redeem":
        redeeming_users.add(query.from_user.id)
        await query.message.reply_text("🎟 Send your order ID:", reply_markup=back_button())
        return

    if query.data == "status":
        checking_status_users.add(query.from_user.id)
        await query.message.reply_text("📦 Send order ID:", reply_markup=back_button())
        return

    if query.data == "contact":
        contacting_users.add(query.from_user.id)
        await query.message.reply_text("📨 Send message:", reply_markup=back_button())
        return

    if query.data == "products":
        await query.message.reply_text(
            "📦 Products section",
            reply_markup=back_button()
        )
        return

    if query.data == "info":
        await query.message.reply_text(
            "ℹ️ Info section",
            reply_markup=back_button()
        )
        return

# =========================
# MESSAGES
# =========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text

    # STATUS
    if user.id in checking_status_users:
        if text not in order_status:
            await update.message.reply_text("❌ Order not found.")
        else:
            await update.message.reply_text(f"📦 Status: {order_status[text]}")
        checking_status_users.remove(user.id)
        return

    # CONTACT STAFF
    if user.id in contacting_users:
        await context.bot.send_message(
            chat_id=STAFF_CHAT_ID,
            text=f"📨 Support\nUser: {user.first_name}\nMessage: {text}"
        )
        await update.message.reply_text("Sent to staff.")
        contacting_users.remove(user.id)
        return

    # REDEEM
    if user.id in redeeming_users:
        order_id = text

        orders[order_id] = chat_id
        order_status[order_id] = "Pending"

        await context.bot.send_message(
            chat_id=STAFF_CHAT_ID,
            text=f"📦 New Order\nID: {order_id}"
        )

        await update.message.reply_text("Sent for verification.")
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
        await update.message.reply_text("Usage: /send ID message")
        return

    order_id = parts[1]
    msg = parts[2]

    if order_id not in orders:
        await update.message.reply_text("Not found")
        return

    order_status[order_id] = "Completed"

    await context.bot.send_message(
        chat_id=orders[order_id],
        text=f"✅ Delivered:\n{msg}"
    )

    await update.message.reply_text("Sent.")

# =========================
# RUN BOT
# =========================

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.Chat(STAFF_CHAT_ID) & filters.TEXT, staff_send))

print("Bot running...")
app.run_polling()

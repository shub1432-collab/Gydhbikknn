import os
import re
import requests

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)


# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv(
    "BOT_TOKEN",
    "9149744954:AAFQwIb9oQkIXYSEuXRLh_BtqVxd2hRgc8c"
)

OCR_SPACE_API_KEY = os.getenv(
    "OCR_SPACE_API_KEY",
    "K83665952588957"
)

ADMIN_ID = int(
    os.getenv(
        "ADMIN_ID",
        "8610732477"  # Yahan apni Telegram Admin ID daalain
    )
)

MY_UPI_ID = "paytm.s26tbd7@pty"
MY_UPI_NAME = "Subham"

BUY_BUTTON_TEXT = "👑 Buy Premium Access 🔥"


# =========================================================
# TELEGRAM GROUP CONFIG
# =========================================================

START_GROUP_ID = int(os.getenv("START_GROUP_ID", "-1004492866489"))
START_PINNED_MESSAGE_ID = int(os.getenv("START_PINNED_MESSAGE_ID", "2"))

DEMO_GROUP_ID = int(os.getenv("DEMO_GROUP_ID", "-1004469438880"))
DEMO_PINNED_MESSAGE_ID = int(os.getenv("DEMO_PINNED_MESSAGE_ID", "2"))


# =========================================================
# PREMIUM PLANS & PRIVATE CHANNEL / CONTENT LINKS
# =========================================================

PLAN_DETAILS = {
    "plan_49": {
        "price_str": "₹49",
        "amount": 49,
        "name": "🫦 𝐂𝐇*𝐋𝐃-𝐏*𝐑𝐍🫦💦",
        "channel_invite_link": "https://t.me/+bbHEYkg9NwEzMGU1",
    },
    "plan_69": {
        "price_str": "₹69",
        "amount": 69,
        "name": "🫦 𝐑𝐏𝐄-𝐏*𝐑𝐍🫦💦",
        "channel_invite_link": "https://t.me/+bbHEYkg9NwEzMGU1",
    },
    "plan_79": {
        "price_str": "₹79",
        "amount": 79,
        "name": "🫦 𝐃𝐄𝐒𝐈 𝐁𝐇𝐀𝐁𝐇𝐈🫦💦",
        "channel_invite_link": "https://t.me/+bbHEYkg9NwEzMGU1",
    },
    "plan_99": {
        "price_str": "₹99",
        "amount": 99,
        "name": "🫦 𝐈𝐍𝐒𝐓𝐀𝐆𝐑𝐀𝐌 𝐒𝐓𝐀𝐑🫦💦",
        "channel_invite_link": "https://t.me/+bbHEYkg9NwEzMGU1",
    },
    "plan_149": {
        "price_str": "₹149",
        "amount": 149,
        "name": "🫦 𝐓𝐄𝐄𝐍 𝐈𝐍𝐃𝐈𝐀𝐍🫦💦",
        "channel_invite_link": "https://t.me/+bbHEYkg9NwEzMGU1",
    },
    "plan_199": {
        "price_str": "₹199",
        "amount": 199,
        "name": "🫦 𝐁𝐑𝐎𝐓𝐇𝐄𝐑-𝐒𝐈𝐒𝐓𝐄𝐑🫦💦",
        "channel_invite_link": "https://t.me/+bbHEYkg9NwEzMGU1",
    },
}


# =========================================================
# STATE
# =========================================================

WAITING_FOR_SCREENSHOT = 1


# =========================================================
# AUTO-DELETE QR JOB FUNCTION
# =========================================================

async def delete_qr_message(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    chat_id = job_data["chat_id"]
    message_id = job_data["message_id"]
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print("Error auto-deleting QR message:", e)


# =========================================================
# MAIN MENU
# =========================================================

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🟢 ₹49 — 🫦 𝐂𝐇*𝐋𝐃-𝐏*𝐑𝐍🫦💦", callback_data="plan_49")],
        [InlineKeyboardButton("🔵 ₹69 — 🫦 𝐑𝐏𝐄-𝐏*𝐑𝐍🫦💦", callback_data="plan_69")],
        [InlineKeyboardButton("🟣 ₹79 — 🫦 𝐃𝐄𝐒𝐈 𝐁𝐇𝐀𝐁𝐇𝐈🫦💦", callback_data="plan_79")],
        [InlineKeyboardButton("🟠 ₹99 — 🫦 𝐈𝐍𝐒𝐓𝐀𝐆𝐑𝐀𝐌 𝐒𝐓𝐀𝐑🫦💦", callback_data="plan_99")],
        [InlineKeyboardButton("🔥 ₹149 — 🫦 𝐓𝐄𝐄𝐍 𝐈𝐍𝐃𝐈𝐀𝐍🫦💦", callback_data="plan_149")],
        [InlineKeyboardButton("👑 ₹199 — 🫦 𝐁𝐑𝐎𝐓𝐇𝐄𝐑-𝐒𝐈𝐒𝐓𝐄𝐑🫦💦", callback_data="plan_199")],
        [InlineKeyboardButton("🎁 Demo", callback_data="demo")],
    ]
    return InlineKeyboardMarkup(keyboard)


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chat_id = update.effective_chat.id
    try:
        context.user_data.clear()
        
        await context.bot.copy_message(
            chat_id=user_chat_id,
            from_chat_id=START_GROUP_ID,
            message_id=START_PINNED_MESSAGE_ID
        )
        await context.bot.send_message(
            chat_id=user_chat_id,
            text=(
                "👋 **Welcome!**\n\n"
                "🎉 Welcome to VIP Access Bot!\n\n"
                "✨ Get exclusive access to premium content\n"
                "💰 Affordable plans starting\n"
                "✨ Only Premium Content\n"
                "✨ Daily New Uploads\n"
                "✨ TRY OUR ANY PLAN FOR CHECKING THE QUALITY ✨"
            ),
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"START ERROR for user {user_chat_id}:", e)


# =========================================================
# BUTTON HANDLER
# =========================================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_chat_id = query.from_user.id

    # Handle Admin Approval / Rejection callbacks
    if query.data.startswith("approve_") or query.data.startswith("reject_"):
        if query.from_user.id != ADMIN_ID:
            await query.answer("You are not authorized!", show_alert=True)
            return

        data_parts = query.data.split("_")
        action = data_parts[0]  
        target_user_id = int(data_parts[1])
        plan_key = data_parts[2]

        plan_info = PLAN_DETAILS.get(plan_key, {})
        plan_name = plan_info.get("name", "Premium Plan")
        channel_link = plan_info.get("channel_invite_link", "https://t.me/+YOUR_DEFAULT_LINK")

        if action == "approve":
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=(
                        f"🎉 **Payment Approved!**\n\n"
                        f"👑 **Plan:** {plan_name}\n\n"
                        f"✅ आपका पेमेंट वेरीफाई हो गया है। नीचे दिए गए लिंक से प्राइवेट चैनल ज्वाइन करें:\n\n"
                        f"🔗 {channel_link}"
                    ),
                    parse_mode="Markdown"
                )
                await query.edit_message_caption(
                    caption=query.message.caption + "\n\n**STATUS: ✅ APPROVED BY ADMIN**",
                    parse_mode="Markdown"
                )
            except Exception as err:
                print("Error sending link to user:", err)
                await query.edit_message_caption(
                    caption=query.message.caption + f"\n\n**STATUS: ✅ APPROVED (Failed to message user)**"
                )
        else:
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=(
                        "❌ **Payment Verification Failed / Rejected!**\n\n"
                        "⚠️ आपका पेमेंट स्क्रीनशॉट इनवैलिड या फेक पाया गया है, या राशि मैच नहीं हुई।\n"
                        "कृपया सही स्क्रीनशॉट भेजें या एडमिन से संपर्क करें।"
                    ),
                    parse_mode="Markdown"
                )
                await query.edit_message_caption(
                    caption=query.message.caption + "\n\n**STATUS: ❌ REJECTED BY ADMIN**",
                    parse_mode="Markdown"
                )
            except Exception as err:
                print("Error sending rejection to user:", err)

        return

    if query.data == "demo":
        try:
            await context.bot.copy_message(
                chat_id=user_chat_id,
                from_chat_id=DEMO_GROUP_ID,
                message_id=DEMO_PINNED_MESSAGE_ID
            )
            await context.bot.send_message(
                chat_id=user_chat_id,
                text="🎁 **Demo ऊपर भेज दिया गया है।**\n\n👇 अपना option चुनें:",
                reply_markup=main_menu(),
                parse_mode="Markdown"
            )
        except Exception as e:
            print("DEMO ERROR:", e)
        return

    if query.data.startswith("plan_"):
        if query.data not in PLAN_DETAILS:
            await context.bot.send_message(chat_id=user_chat_id, text="❌ Invalid plan.")
            return ConversationHandler.END

        plan_info = PLAN_DETAILS[query.data]
        context.user_data["selected_plan"] = query.data

        try:
            amount = plan_info["amount"]
            
            # 🔒 LOCKED UPI STRING (Amount & Payee Locked)
            upi_uri = f"upi://pay?pa={MY_UPI_ID}&pn={MY_UPI_NAME}&am={amount}&cu=INR"
            
            # Generate dynamic QR code image URL for locked amount
            qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={requests.utils.quote(upi_uri)}"

            # Send Locked QR code image with exact amount and 2 minutes expiry notice
            sent_msg = await context.bot.send_photo(
                chat_id=user_chat_id,
                photo=qr_api_url,
                caption=(
                    f"🔒 **Locked Payment QR for {plan_info['name']}**\n\n"
                    f"📌 **Amount Locked:** `{plan_info['price_str']}`\n"
                    f"📌 **UPI ID:** `{MY_UPI_ID}`\n"
                    f"📌 **Name:** `{MY_UPI_NAME}`\n\n"
                    f"⏱ **यह QR Code केवल 2 मिनट के लिए मान्य है!**\n"
                    f"1️⃣ इस QR को स्कैन करके पेमेंट करें।\n"
                    f"2️⃣ Payment complete करने के बाद **पूरा payment screenshot** यहाँ भेजें।"
                ),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_main")]
                ])
            )

            # Schedule job to auto-delete this QR message after 120 seconds (2 minutes)
            context.job_queue.run_once(
                delete_qr_message,
                when=120,
                data={"chat_id": user_chat_id, "message_id": sent_msg.message_id}
            )

            return WAITING_FOR_SCREENSHOT
        except Exception as e:
            print("PLAN ERROR:", e)
            await context.bot.send_message(chat_id=user_chat_id, text="❌ QR generate करने में समस्या हुई। कृपया दोबारा कोशिश करें।")
            return ConversationHandler.END

    if query.data == "back_main":
        try:
            await query.edit_message_text(
                text="👇 **अपना option चुनें:**",
                reply_markup=main_menu(),
                parse_mode="Markdown"
            )
        except Exception:
            await context.bot.send_message(
                chat_id=user_chat_id,
                text="👇 **अपना option चुनें:**",
                reply_markup=main_menu(),
                parse_mode="Markdown"
            )
        return ConversationHandler.END


# =========================================================
# SCREENSHOT HANDLER
# =========================================================

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_chat_id = update.effective_chat.id
    selected_plan_key = context.user_data.get("selected_plan")

    if not selected_plan_key:
        await update.message.reply_text("❌ पहले कोई plan select करें। /start दबाएं।")
        return ConversationHandler.END

    plan_info = PLAN_DETAILS.get(selected_plan_key)
    if not plan_info:
        await update.message.reply_text("❌ Plan information नहीं मिली।")
        return ConversationHandler.END

    if not update.message.photo:
        await update.message.reply_text("❌ कृपया payment का screenshot/photo भेजें।")
        return WAITING_FOR_SCREENSHOT

    processing_msg = await update.message.reply_text("⏳ आपका पेमेंट स्क्रीनशॉट एडमिन के पास वेरिफिकेशन के लिए भेज दिया गया है। कृपया प्रतीक्षा करें...")

    try:
        photo_file_id = update.message.photo[-1].file_id

        admin_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}_{selected_plan_key}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}_{selected_plan_key}")
            ]
        ])

        username_str = f"@{user.username}" if user.username else "No Username"
        admin_caption = (
            f"🔔 **NEW PAYMENT SCREENSHOT FOR REVIEW**\n\n"
            f"👤 **User:** {user.full_name}\n"
            f"🆔 **User ID:** `{user.id}`\n"
            f"📱 **Username:** {username_str}\n"
            f"👑 **Plan:** {plan_info['name']}\n"
            f"💰 **Amount:** {plan_info['price_str']}\n"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_caption,
            parse_mode="Markdown"
        )
        
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_file_id,
            reply_markup=admin_keyboard
        )

        await processing_msg.edit_text(
            "📩 **स्क्रीनशॉट सबमिट हो गया है!**\n\n"
            "एडमिन द्वारा चेक करने के बाद आपको चैनल का लिंक भेज दिया जाएगा। कृपया इंतजार करें।"
        )

        context.user_data.clear()
        return ConversationHandler.END

    except Exception as e:
        print("SCREENSHOT FORWARD ERROR:", e)
        await processing_msg.edit_text("❌ स्क्रीनशॉट भेजने में समस्या हुई। कृपया दोबारा कोशिश करें।")
        return WAITING_FOR_SCREENSHOT


async def handle_text_during_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ कृपया payment का **screenshot/photo** भेजें।", parse_mode="Markdown")
    return WAITING_FOR_SCREENSHOT


# =========================================================
# MAIN (High-Performance Configuration)
# =========================================================

def main():
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        print("❌ BOT_TOKEN set नहीं है।")
        return

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)  
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern=r"^plan_")],
        states={
            WAITING_FOR_SCREENSHOT: [
                MessageHandler(filters.PHOTO, handle_screenshot),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_during_payment),
            ]
        },
        fallbacks=[
            CommandHandler("start", start),
            CallbackQueryHandler(button_handler, pattern=r"^(back_main)$")
        ],
        allow_reentry=True,
        per_message=False,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🚀 Bot is running with 2-Minute Auto-Delete QR & Concurrent Engine...")
    
    app.run_polling(
        drop_pending_updates=True,
        poll_interval=0.0,
        read_timeout=30,
        write_timeout=30,
        connect_timeout=30
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging, sqlite3, datetime, os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import instaloader
import requests
import phonenumbers
import whois

# ----------------------- إعدادات -----------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")  # تأكد تحط التوكن هنا أو export BOT_TOKEN="توكنك"
DB_FILE = "bot_osint.db"

# ----------------------- لوج -----------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ----------------------- قاعدة البيانات -----------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            last_seen TEXT,
            queries INTEGER DEFAULT 0
        )"""
    )
    conn.commit()
    conn.close()

def ensure_user(user):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    now = datetime.datetime.now().isoformat()
    try:
        cur.execute(
            "INSERT OR IGNORE INTO users (id, username, last_seen, queries) VALUES (?, ?, ?, 0)",
            (user.id, user.username or "", now),
        )
        cur.execute(
            "UPDATE users SET last_seen=?, username=? WHERE id=?",
            (now, user.username or "", user.id),
        )
        conn.commit()
    finally:
        conn.close()

def log_cmd(user_id, cmd, args=""):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE users SET queries = queries + 1 WHERE id=?", (user_id,)
        )
        conn.commit()
    finally:
        conn.close()

# ----------------------- أوامر البوت -----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update.effective_user)
    message = (
        "🤖 بوت OSINT جاهز!\n\n"
        "الأوامر:\n"
        "/sherlock <username>\n"
        "/insta <username>\n"
        "/deepinsta <username>  🔥 أقوى أداة انستغرام\n"
        "/whois <domain>\n"
        "/phone <number>\n"
        "/osint <query>"
    )
    await update.message.reply_text(message)

# ----------------------- أداة Instaloader -----------------------
async def insta_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update.effective_user)
    log_cmd(update.effective_user.id, "insta", " ".join(context.args))
    if len(context.args) < 1:
        await update.message.reply_text("استخدم: /insta <username>")
        return
    username = context.args[0]
    await update.message.reply_text(f"⏳ جاري جمع بيانات Instagram لـ {username} ...")
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        info = (
            f"👤 اسم: {profile.full_name}\n"
            f"📌 Username: {profile.username}\n"
            f"🔗 Bio: {profile.biography}\n"
            f"👥 المتابعين: {profile.followers}\n"
            f"👤 المتابعين له: {profile.followees}\n"
            f"📸 الصور: {profile.mediacount}\n"
            f"🌐 رابط: https://www.instagram.com/{profile.username}/"
        )
        await update.message.reply_text(info)
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")

# ----------------------- أداة قوية deepinsta -----------------------
async def deepinsta_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update.effective_user)
    log_cmd(update.effective_user.id, "deepinsta", " ".join(context.args))
    if len(context.args) < 1:
        await update.message.reply_text("استخدم: /deepinsta <username>")
        return
    username = context.args[0]
    await update.message.reply_text(f"⏳ جاري تحليل شامل لـ Instagram {username} ...")
    try:
        r = requests.get(f"https://www.instagram.com/{username}/?__a=1")
        if r.status_code != 200:
            raise Exception("لم يتم العثور على الحساب")
        data = r.json()
        user = data.get("graphql", {}).get("user", {})
        info = (
            f"👤 اسم: {user.get('full_name')}\n"
            f"🔗 Username: {user.get('username')}\n"
            f"👥 المتابعين: {user.get('edge_followed_by', {}).get('count')}\n"
            f"👤 المتابعين له: {user.get('edge_follow', {}).get('count')}\n"
            f"📸 الصور: {user.get('edge_owner_to_timeline_media', {}).get('count')}\n"
            f"🌐 رابط: https://www.instagram.com/{username}/"
        )
        await update.message.reply_text(info)
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")

# ----------------------- أوامر OSINT -----------------------
async def osint_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update.effective_user)
    log_cmd(update.effective_user.id, "osint", " ".join(context.args))
    await update.message.reply_text("⏳ جاري تحليل OSINT ... (مؤقتًا مجرد مثال)")
    # هنا يمكن إضافة أي أدوات OSINT حقيقية لاحقًا
    await update.message.reply_text("✅ تحليل OSINT مكتمل (هذا مجرد مثال)")

# ----------------------- أوامر Sherlock -----------------------
async def sherlock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update.effective_user)
    log_cmd(update.effective_user.id, "sherlock", " ".join(context.args))
    if len(context.args) < 1:
        await update.message.reply_text("استخدم: /sherlock <username>")
        return
    username = context.args[0]
    await update.message.reply_text(f"⏳ جاري البحث عن {username} في مواقع التواصل ...")
    os.system(f"python3 ~/sherlock/sherlock.py {username}")

# ----------------------- Whois -----------------------
async def whois_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update.effective_user)
    log_cmd(update.effective_user.id, "whois", " ".join(context.args))
    if len(context.args) < 1:
        await update.message.reply_text("استخدم: /whois <domain>")
        return
    domain = context.args[0]
    try:
        w = whois.whois(domain)
        await update.message.reply_text(f"✅ Whois: {w}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")

# ----------------------- Phone -----------------------
async def phone_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update.effective_user)
    log_cmd(update.effective_user.id, "phone", " ".join(context.args))
    if len(context.args) < 1:
        await update.message.reply_text("استخدم: /phone <number>")
        return
    number = context.args[0]
    try:
        parsed = phonenumbers.parse(number, None)
        info = (
            f"📞 Number: {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}\n"
            f"🌍 Region: {phonenumbers.region_code_for_number(parsed)}"
        )
        await update.message.reply_text(info)
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")

# ----------------------- Main -----------------------
if __name__ == "__main__":
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("insta", insta_cmd))
    app.add_handler(CommandHandler("deepinsta", deepinsta_cmd))
    app.add_handler(CommandHandler("osint", osint_cmd))
    app.add_handler(CommandHandler("sherlock", sherlock_cmd))
    app.add_handler(CommandHandler("whois", whois_cmd))
    app.add_handler(CommandHandler("phone", phone_cmd))

    print("✅ البوت يعمل الآن (polling)...")
    app.run_polling()

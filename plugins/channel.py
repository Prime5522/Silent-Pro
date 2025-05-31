import re
import hashlib
import requests
from info import *
from utils import *
from pyrogram import Client, filters
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


CAPTION_LANGUAGES = ["Bhojpuri", "Hindi", "Bengali", "Tamil", "English", "Bangla", "Telugu", "Malayalam", "Kannada", "Marathi", "Punjabi", "Bengoli", "Gujrati", "Korean", "Gujarati", "Spanish", "French", "German", "Chinese", "Arabic", "Portuguese", "Russian", "Japanese", "Odia", "Assamese", "Urdu"]

notified_movies = set()
user_reactions = {}
reaction_counts = {}

media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    """Media Handler"""
    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return
    media.file_type = file_type
    media.caption = message.caption
    success, silentxbotz = await save_file(bot, media)
    try:  
        if success and silentxbotz == 1 and await get_status(bot.me.id):            
            await send_movie_update(bot, file_name=media.file_name, caption=media.caption)
    except Exception as e:
        print(f"Error In Movie Update - {e}")
        pass


async def send_movie_update(bot, file_name, caption):
    try:
        file_name = await movie_name_format(file_name)
        caption = await movie_name_format(caption)

        # Clean file_name (remove URL, @mention, extra spaces)
        clean_name = re.sub(r'https?://\S+', '', file_name)
        clean_name = re.sub(r'@\w+', '', clean_name)
        clean_name = re.sub(r'\s{2,}', ' ', clean_name).strip()

        title_line = f"🗃️ @PrimeCineHub {clean_name}"

        year_match = re.search(r"\b(19|20)\d{2}\b", caption)
        year = year_match.group(0) if year_match else None

        season_match = re.search(r"(?i)(?:s|season)0*(\d{1,2})", caption) or re.search(r"(?i)(?:s|season)0*(\d{1,2})", file_name)
        if year:
            file_name = file_name[:file_name.find(year) + 4]
        elif season_match:
            season = season_match.group(1)
            file_name = file_name[:file_name.find(season) + 1]

        quality = await get_qualities(caption) or "HDRip"
        language = ", ".join([lang for lang in CAPTION_LANGUAGES if lang.lower() in caption.lower()]) or "Not Idea"

        imdb_data = await get_imdb_details(file_name)
        title = imdb_data.get("title", file_name)
        kind = imdb_data.get("kind", "").strip().upper().replace(" ", "") if imdb_data else None
        imdb_year = imdb_data.get("year", year)
        year = imdb_year or "Unknown"

        poster = await fetch_movie_poster(title, year)
        search_movie = file_name.replace(" ", "-")
        unique_id = generate_unique_id(search_movie)

        # Initialize reaction storage
        reaction_counts[unique_id] = {"❤️": 0, "👍": 0, "👎": 0, "🔥": 0}
        user_reactions[unique_id] = {}

        # Caption template (title_line যুক্ত করা হয়েছে এখানে)
        caption_template = f"""{title_line}

╔════❰ #ɴᴇᴡ_ꜰɪʟᴇ_ᴀᴅᴅᴇᴅ ✅ ❱═❍⊱❁۪۪
║╭━━━❰ 🎬 ꜰᴏʀ ʏᴏᴜʀ ᴇɴᴛᴇʀᴛᴀɪɴᴍᴇɴᴛ 🎭 ❱━⊱
║┃🎬 ᴛɪᴛʟᴇ : {file_name}
║┃🎥 Qᴜᴀʟɪᴛʏ : {quality}
║┃🔊 ʟᴀɴɢᴜᴀɢᴇ : {language}
║┃🗒️ ʀᴇʟᴇᴀsᴇ : {year}
║╰━━━━━━━━━━━━━━━━━━⊱
║
║╭━━━━❰ 📺 ᴠɪᴅᴇᴏ ǫᴜᴀʟɪᴛʏ 📺 ❱━━⊱
║┃
║┣⪼⭕ 𝟰𝟴𝟬𝗽 👉 <a href="https://telegram.me/iPapkornPrimeBot?start=getfile-{search_movie}">https://Primeurl.com-{title}-480p-{quality}.mkv</a>
║┃
║┣⪼⭕ 𝟳𝟮𝟬𝗽 👉 <a href="https://telegram.me/iPapkornPrimeBot?start=getfile-{search_movie}">https://Primeurl.com-{title}-720p-{quality}.mkv</a>
║┃
║┣⪼⭕ 𝟭𝟬𝟴𝟬𝗽 👉 <a href="https://telegram.me/iPapkornPrimeBot?start=getfile-{search_movie}">https://Primeurl.com-{title}-1080p-{quality}.mkv</a>
║┃
║╰━━━━━━━━━━━━━━━━━━⊱
║
║╭━❰ 📚 ʜᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴛᴜᴛᴏʀɪᴀʟ ᴠɪᴅᴇᴏ 🎥 ❱━⊱
║┃        <a href='https://t.me/Prime_Movie_Watch_Dawnload/75'>👉 🔴 ʜᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ 🔴 👈</a>
║╰━━━━━━━━━━━━━━━━⊱
║
║╭━━━━❰ 🤝 ᴏғғɪᴄɪᴀʟ ᴄʜᴀɴɴᴇʟꜱ & ɢʀᴏᴜᴘꜱ 🤝 ❱━⊱
║┃
║┣⪼ ✇ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟꜱ:
║┃🔹 @PrimeCineZone
║┃🔹 @Prime_Botz
║┃
║┣⪼ 🎬 ᴍᴏᴠɪᴇ/ᴡᴇʙ ꜱᴇʀɪᴇꜱ ʀᴇQᴜᴇꜱᴛ ɢʀᴏᴜᴘ:
║┃🔗 https://t.me/PrimeCineZone/143
║┃
║╰━━━━━━━━━━━━━━⊱
║
╚══❰ 💠 ꜱᴛᴀʏ ᴇɴᴛᴇʀᴛᴀɪɴᴇᴅ 💠 ❱═❍⊱❁۪۪
"""

        full_caption = caption_template


        buttons = [[
            InlineKeyboardButton(f"❤️ {reaction_counts[unique_id]['❤️']}", callback_data=f"r{unique_id}{search_movie}heart"),
            InlineKeyboardButton(f"👍 {reaction_counts[unique_id]['👍']}", callback_data=f"r{unique_id}{search_movie}like"),
            InlineKeyboardButton(f"👎 {reaction_counts[unique_id]['👎']}", callback_data=f"r{unique_id}{search_movie}dislike"),
            InlineKeyboardButton(f"🔥 {reaction_counts[unique_id]['🔥']}", callback_data=f"r{unique_id}{search_movie}_fire")
        ], [
            InlineKeyboardButton('Get File', url=f'https://telegram.me/iPapkornPrimeBot?start=getfile-{search_movie}')
        ]]

        image_url = poster or "https://te.legra.ph/file/88d845b4f8a024a71465d.jpg"

        await bot.send_photo(
            chat_id=MOVIE_UPDATE_CHANNEL,
            photo=image_url,
            caption=full_caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:
        print(f"Error in send_movie_update: {e}")
        
        

@Client.on_callback_query(filters.regex(r"^r_"))
async def reaction_handler(client, query):
    try:
        data = query.data.split("_")
        if len(data) != 4:
            return        
        unique_id = data[1]
        search_movie = data[2]
        new_reaction = data[3]
        user_id = query.from_user.id
        emoji_map = {"heart": "❤️", "like": "👍", "dislike": "👎", "fire": "🔥"}
        if new_reaction not in emoji_map:
            return
        new_emoji = emoji_map[new_reaction]       
        if unique_id not in reaction_counts:
            return
        if user_id in user_reactions[unique_id]:
            old_emoji = user_reactions[unique_id][user_id]
            if old_emoji == new_emoji:
                return 
            else:
                reaction_counts[unique_id][old_emoji] -= 1
        user_reactions[unique_id][user_id] = new_emoji
        reaction_counts[unique_id][new_emoji] += 1
        updated_buttons = [[
            InlineKeyboardButton(f"❤️ {reaction_counts[unique_id]['❤️']}", callback_data=f"r_{unique_id}_{search_movie}_heart"),                
            InlineKeyboardButton(f"👍 {reaction_counts[unique_id]['👍']}", callback_data=f"r_{unique_id}_{search_movie}_like"),
            InlineKeyboardButton(f"👎 {reaction_counts[unique_id]['👎']}", callback_data=f"r_{unique_id}_{search_movie}_dislike"),
            InlineKeyboardButton(f"🔥 {reaction_counts[unique_id]['🔥']}", callback_data=f"r_{unique_id}_{search_movie}_fire")
        ],[
            InlineKeyboardButton('Get File', url=f'https://telegram.me/{temp.U_NAME}?start=getfile-{search_movie}')
        ]]
        await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(updated_buttons))
    except Exception as e:
        print("Reaction error:", e)
        
async def get_imdb_details(name):
    try:
        formatted_name = await movie_name_format(name)
        imdb = await get_poster(formatted_name)
        if not imdb:
            return {}
        return {
            "title": imdb.get("title", formatted_name),
            "kind": imdb.get("kind", "Movie"),
            "year": imdb.get("year")
        }
    except Exception as e:
        print(f"IMDB fetch error: {e}")
        return {}

async def fetch_movie_poster(title, year=None):
    try:
        params = {"api_key": TMDB_API, "query": title}
        if year:
            params["year"] = year

        res = requests.get("https://api.themoviedb.org/3/search/movie", params=params, timeout=10)
        data = res.json().get("results", [])
        if not data:
            return "https://te.legra.ph/file/88d845b4f8a024a71465d.jpg"

        movie = data[0]
        movie_id = movie.get("id")
        poster_path = movie.get("poster_path")

        # Step 1: Use official poster if available
        if poster_path:
            return f"https://image.tmdb.org/t/p/original{poster_path}"

        # Step 2: Fallback to backdrop if poster is missing
        if movie_id:
            img_res = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/images?api_key={TMDB_API}", timeout=10)
            backdrops = img_res.json().get("backdrops", [])
            if backdrops:
                return f"https://image.tmdb.org/t/p/original{backdrops[0]['file_path']}"

        # Step 3: Final fallback to default image
        return "https://te.legra.ph/file/88d845b4f8a024a71465d.jpg"

    except Exception as e:
        print(f"Poster fetch error: {e}")
        return "https://te.legra.ph/file/88d845b4f8a024a71465d.jpg"


def generate_unique_id(movie_name):
    return hashlib.md5(movie_name.encode('utf-8')).hexdigest()[:5]

async def get_qualities(text):
    qualities = ["ORG", "org", "hdcam", "HDCAM", "HQ", "hq", "HDRip", "hdrip", 
                 "camrip", "WEB-DL", "CAMRip", "hdtc", "predvd", "DVDscr", "dvdscr", 
                 "dvdrip", "HDTC", "dvdscreen", "HDTS", "hdts"]
    return ", ".join([q for q in qualities if q.lower() in text.lower()])


async def movie_name_format(file_name):
  clean_filename = re.sub(r'http\S+', '', re.sub(r'@\w+|#\w+', '', file_name).replace('_', ' ').replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('{', '').replace('}', '').replace('.', ' ').replace('@', '').replace(':', '').replace(';', '').replace("'", '').replace('-', '').replace('!', '')).strip()
  return clean_filename

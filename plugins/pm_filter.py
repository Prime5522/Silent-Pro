import asyncio
import re
import ast
import math
import random
import pytz
from datetime import datetime, timedelta, date, time
lock = asyncio.Lock()
from database.users_chats_db import db
from database.refer import referdb
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, WebAppInfo
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import *
from fuzzywuzzy import process
from database.users_chats_db import db
from database.ia_filterdb import Media, Media2, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from database.gfilters_mdb import (
    find_gfilter,
    get_gfilters,
    del_allg
)
import logging
from urllib.parse import quote_plus
from Lucia.util.file_properties import get_name, get_hash, get_media_file_size
from database.topdb import silentdb
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

import requests
import string
import tracemalloc

import os
req_channel = int(os.environ.get('REQ_CHANNEL', -1002120012639))

tracemalloc.start()

TIMEZONE = "Asia/Kolkata"
BUTTON = {}
BUTTONS = {}
FRESH = {}
SPELL_CHECK = {}


@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if EMOJI_MODE:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    await silentdb.update_top_messages(message.from_user.id, message.text)
    if message.chat.id != SUPPORT_CHAT_ID:
        manual = await manual_filters(client, message)
        if manual == False:
            settings = await get_settings(message.chat.id)
            if settings['auto_ffilter']:
                await auto_filter(client, message)
    else:
        search = message.text
        temp_files, temp_offset, total_results = await get_search_results(chat_id=message.chat.id, query=search.lower(), offset=0, filter=True)
        if total_results == 0:
            return
        else:
            return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention},\n\nʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ✅\n\n📂 ꜰɪʟᴇꜱ ꜰᴏᴜɴᴅ : {str(total_results)}\n🔍 ꜱᴇᴀʀᴄʜ :</b> <code>{search}</code>\n\n<b>‼️ ᴛʜɪs ɪs ᴀ <u>sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ</u> sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...\n\n📝 ꜱᴇᴀʀᴄʜ ʜᴇʀᴇ : 👇</b>",   
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 ᴊᴏɪɴ ᴀɴᴅ ꜱᴇᴀʀᴄʜ ʜᴇʀᴇ 🔎", url=GRP_LNK)]]))


@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    bot_id = bot.me.id
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if EMOJI_MODE:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    if content.startswith(('/', '#')):
        return  
    try:
        await silentdb.update_top_messages(user_id, content)
        pm_search = await db.pm_search_status(bot_id)
        if pm_search:
            await auto_filter(bot, message)
        else:
            await message.reply_photo(
                photo="https://i.postimg.cc/XXMZ8kvs/file-000000001c6861f88a586629fa554677-conversation-id-681d5240-27b8-800e-a7f8-f4268a53fe3c-message-i.png",  # Replace with your image URL or local path
                caption=f"<b><i>ɪ ᴀᴍ ɴᴏᴛ ᴡᴏʀᴋɪɴɢ ʜᴇʀᴇ ꜰᴏʀ sᴏᴍᴇ ʀᴇᴀsᴏɴs 🚫 ᴊᴏɪɴ ᴍʏ ɢʀᴏᴜᴘ ꜰʀᴏᴍ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴀɴᴅ ꜱᴇᴀʀᴄʜ ᴛʜᴇʀᴇ !👇</i></b>",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("📝 ꜱᴇᴀʀᴄʜ ʜᴇʀᴇ ", url=GRP_LNK)]]
                )
            )
    except Exception as e:
        print(f"An error occurred: {str(e)}")


@Client.on_callback_query(filters.regex(r"^reffff"))
async def refercall(bot, query):
    btn = [[
        InlineKeyboardButton('ɪɴᴠɪᴛᴇ ɪɪɴᴋ', url=f'https://telegram.me/share/url?url=https://t.me/{bot.me.username}?start=reff_{query.from_user.id}&text=Hello%21%20Experience%20a%20bot%20that%20offers%20a%20vast%20library%20of%20unlimited%20movies%20and%20series.%20%F0%9F%98%83'),
        InlineKeyboardButton(f'⏳ {referdb.get_refer_points(query.from_user.id)}', callback_data='ref_point'),
        InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='premium')
    ]]
    reply_markup = InlineKeyboardMarkup(btn)
    await bot.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto("https://graph.org/file/1a2e64aee3d4d10edd930.jpg")
        )
    await query.message.edit_text(
        text=f'Hay Your refer link:\n\nhttps://t.me/{bot.me.username}?start=reff_{query.from_user.id}\n\nShare this link with your friends, Each time they join,  you will get 10 refferal points and after 100 points you will get 1 month premium subscription.',
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
        )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    try:
        ident, req, key, offset = query.data.split("_")
        curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        if int(req) not in [query.from_user.id, 0]:
            return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        try:
            offset = int(offset)
        except:
            offset = 0
        if BUTTONS.get(key)!=None:
            search = BUTTONS.get(key)
        else:
            search = FRESH.get(key)
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
            return
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
        try:
            n_offset = int(n_offset)
        except:
            n_offset = 0
        if not files:
            return
        temp.GETALL[key] = files
        temp.SHORT[query.from_user.id] = query.message.chat.id
        settings = await get_settings(query.message.chat.id)
        if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{silent_size(file.file_size)}| {extract_tag(file.file_name)} {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", callback_data=f'file#{file.file_id}'
                    ),
                ]
                for file in files
            ]
            btn.insert(0, 
                [ 
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0"),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0"),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0")
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}")
           
            ])
        else:
            btn = []
            btn.insert(0, 
                [
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0"),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0"),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0")
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}") 
           
            ])
        try:
            if settings['max_btn']:
                if 0 < offset <= 10:
                    off_set = 0
                elif offset == 0:
                    off_set = None
                else:
                    off_set = offset - 10
                if n_offset == 0:
                    btn.append(
                        [InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
                    )
                elif off_set is None:
                    btn.append([InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
                else:
                    btn.append(
                        [
                            InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                            InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                            InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                        ],
                    )
            else:
                if 0 < offset <= int(MAX_B_TN):
                    off_set = 0
                elif offset == 0:
                    off_set = None
                else:
                    off_set = offset - int(MAX_B_TN)
                if n_offset == 0:
                    btn.append(
                        [InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
                    )
                elif off_set is None:
                    btn.append([InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
                else:
                    btn.append(
                        [
                            InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                            InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                            InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                        ],
                    )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        if not settings["button"]:
            cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
            time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
            remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
            cap = await get_cap(settings, remaining_seconds, files, query, total, search, offset)
            try:
                await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
            except MessageNotModified:
                pass
        else:
            try:
                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except MessageNotModified:
                pass
        await query.answer()
    except Exception as e:
        print(f"Error In Next Funtion - {e}")

@Client.on_callback_query(filters.regex(r"^qualities#"))
async def qualities_cb_handler(client: Client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                return await query.answer(
                    f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                    show_alert=True,
                )
        except:
            pass
        _, key, offset = query.data.split("#")
        search = FRESH.get(key)
        offset = int(offset)
        search = search.replace(' ', '_')
        btn = []
        for i in range(0, len(QUALITIES)-1, 2):
            btn.append([
                InlineKeyboardButton(
                    text=QUALITIES[i].title(),
                    callback_data=f"fq#{QUALITIES[i].lower()}#{key}#{offset}"
                ),
                InlineKeyboardButton(
                    text=QUALITIES[i+1].title(),
                    callback_data=f"fq#{QUALITIES[i+1].lower()}#{key}#{offset}"
                ),
            ])
        btn.insert(
            0,
            [
                InlineKeyboardButton(
                    text="⇊ ꜱᴇʟᴇᴄᴛ ǫᴜᴀʟɪᴛʏ ⇊", callback_data="ident"
                )
            ],
        )
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇs ↭", callback_data=f"fq#homepage#{key}#{offset}")])
        await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))
    except Exception as e:
        print(f"Error In Quality Callback Handler - {e}")

@Client.on_callback_query(filters.regex(r"^fq#"))
async def filter_qualities_cb_handler(client: Client, query: CallbackQuery):
    try:
        _, qual, key, offset = query.data.split("#")
        offset = int(offset)
        curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        search = FRESH.get(key)
        search = search.replace("_", " ")
        baal = qual in search
        if baal:
            search = search.replace(qual, "")
        else:
            search = search
        req = query.from_user.id
        chat_id = query.message.chat.id
        message = query.message
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                return await query.answer(
                    f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                    show_alert=True,
                )
        except:
            pass
        if qual != "homepage":
            search = f"{search} {qual}" 
        BUTTONS[key] = search   
        files, n_offset, total_results = await get_search_results(chat_id, search, offset=offset, filter=True)
        if not files:
            await query.answer("🚫 ɴᴏ ꜰɪʟᴇꜱ ᴡᴇʀᴇ ꜰᴏᴜɴᴅ 🚫", show_alert=1)
            return
        temp.GETALL[key] = files
        settings = await get_settings(message.chat.id)
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{silent_size(file.file_size)}| {extract_tag(file.file_name)} {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", callback_data=f'file#{file.file_id}'
                    ),
                ]
                for file in files
            ]
            btn.insert(0, 
                [ 
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0"),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0"),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0")
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}")
           
            ])

        else:
            btn = []
            btn.insert(0, 
                [
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0"),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0"),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0")
                ]
            )
            btn.insert(1, [           
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}")
           
            ])
        if n_offset != "":
            try:
                if settings['max_btn']:
                    btn.append(
                        [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}")]
                    )
    
                else:
                    btn.append(
                        [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}")]
                    )
            except KeyError:
                await save_group_settings(query.message.chat.id, 'max_btn', True)
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}")]
                )
        else:
            n_offset = 0
            btn.append(
                [InlineKeyboardButton(text="↭ ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ↭",callback_data="pages")]
            )               
        if not settings["button"]:
            cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
            time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
            remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
            cap = await get_cap(settings, remaining_seconds, files, query, total_results, search, offset)
            try:
                await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
            except MessageNotModified:
                pass
        else:
            try:
                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except MessageNotModified:
                pass
        await query.answer()
    except Exception as e:
        print(f"Error In Quality - {e}")

@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                return await query.answer(
                    f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                    show_alert=True,
                )
        except:
            pass
        _, key, offset = query.data.split("#")
        search = FRESH.get(key)
        search = search.replace(' ', '_')
        offset = int(offset)
        btn = []
        for i in range(0, len(LANGUAGES)-1, 2):
            btn.append([
                InlineKeyboardButton(
                    text=LANGUAGES[i].title(),
                    callback_data=f"fl#{LANGUAGES[i].lower()}#{key}#{offset}"
                ),
                InlineKeyboardButton(
                    text=LANGUAGES[i+1].title(),
                    callback_data=f"fl#{LANGUAGES[i+1].lower()}#{key}#{offset}"
                ),
            ])
        btn.insert(
            0,
            [
                InlineKeyboardButton(
                    text="⇊ ꜱᴇʟᴇᴄᴛ ʟᴀɴɢᴜᴀɢᴇ ⇊", callback_data="ident"
                )
            ],
        )
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇs ↭", callback_data=f"fl#homepage#{key}#{offset}")])
        await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))
    except Exception as e:
        print(f"Error In Language Cb Handaler - {e}")
    

@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    try:
        _, lang, key, offset = query.data.split("#")
        offset = int(offset)
        curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        search = FRESH.get(key)
        search = search.replace("_", " ")
        baal = lang in search
        if baal:
            search = search.replace(lang, "")
        else:
            search = search
        req = query.from_user.id
        chat_id = query.message.chat.id
        message = query.message
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                return await query.answer(
                    f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                    show_alert=True,
                )
        except:
            pass
        if lang != "homepage":
            search = f"{search} {lang}"
        BUTTONS[key] = search
        files, n_offset, total_results = await get_search_results(chat_id, search, offset=offset, filter=True)
        if not files:
            await query.answer("🚫 ɴᴏ ꜰɪʟᴇꜱ ᴡᴇʀᴇ ꜰᴏᴜɴᴅ 🚫", show_alert=1)
            return
        temp.GETALL[key] = files
        settings = await get_settings(message.chat.id)
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{silent_size(file.file_size)}| {extract_tag(file.file_name)} {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", callback_data=f'file#{file.file_id}'
                    ),
                ]
                for file in files
            ]
            btn.insert(0, 
                [
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0"),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0"),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0")
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}")
            
            ])
        else:
            btn = []
            btn.insert(0, 
                [
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0"),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0"),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0")
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}")            
            ])
        if n_offset != "":
            try:
                if settings['max_btn']:
                    btn.append(
                        [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}")]
                    )
    
                else:
                    btn.append(
                        [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}")]
                    )
            except KeyError:
                await save_group_settings(query.message.chat.id, 'max_btn', True)
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}")]
                )
        else:
            n_offset = 0
            btn.append(
                [InlineKeyboardButton(text="↭ ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ↭",callback_data="pages")]
            )    

        if not settings["button"]:
            cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
            time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
            remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
            cap = await get_cap(settings, remaining_seconds, files, query, total_results, search, offset)
            try:
                await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
            except MessageNotModified:
                pass
        else:
            try:
                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except MessageNotModified:
                pass
        await query.answer()
    except Exception as e:
        print(f"Error In Language - {e}")
        
@Client.on_callback_query(filters.regex(r"^seasons#"))
async def season_cb_handler(client: Client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                return await query.answer(
                    f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                    show_alert=True,
                )
        except:
            pass
        _, key, offset = query.data.split("#")
        search = FRESH.get(key)
        search = search.replace(' ', '_')
        offset = int(offset)
        btn = []
        for i in range(0, len(SEASONS)-1, 2):
            btn.append([
                InlineKeyboardButton(
                    text=SEASONS[i].title(),
                    callback_data=f"fs#{SEASONS[i].lower()}#{key}#{offset}"
                ),
                InlineKeyboardButton(
                    text=SEASONS[i+1].title(),
                    callback_data=f"fs#{SEASONS[i+1].lower()}#{key}#{offset}"
                ),
            ])
        btn.insert(
            0,
            [
                InlineKeyboardButton(
                    text="⇊ ꜱᴇʟᴇᴄᴛ ʟᴀɴɢᴜᴀɢᴇ ⇊", callback_data="ident"
                )
            ],
        )
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇs ↭", callback_data=f"fl#homepage#{key}#{offset}")])
        await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))
    except Exception as e:
        print(f"Error In Season Cb Handaler - {e}")


@Client.on_callback_query(filters.regex(r"^fs#"))
async def filter_season_cb_handler(client: Client, query: CallbackQuery):
    try:
        _, seas, key, offset = query.data.split("#")
        offset = int(offset)
        curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        search = FRESH.get(key)
        search = search.replace("_", " ")
        baal = seas in search
        if baal:
            search = search.replace(seas, "")
        else:
            search = search
        req = query.from_user.id
        chat_id = query.message.chat.id
        message = query.message
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                return await query.answer(
                    f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                    show_alert=True,
                )
        except:
            pass
        if seas != "homepage":
            search = f"{search} {seas}"
        BUTTONS[key] = search
        files, n_offset, total_results = await get_search_results(chat_id, search, offset=offset, filter=True)
        if not files:
            await query.answer("🚫 ɴᴏ ꜰɪʟᴇꜱ ᴡᴇʀᴇ ꜰᴏᴜɴᴅ 🚫", show_alert=1)
            return
        temp.GETALL[key] = files
        settings = await get_settings(message.chat.id)
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{silent_size(file.file_size)}| {extract_tag(file.file_name)} {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", callback_data=f'file#{file.file_id}'
                    ),
                ]
                for file in files
            ]
            btn.insert(0, 
                [
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0"),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0"),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0")
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}")

            ])
        else:
            btn = []
            btn.insert(0, 
                [
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0"),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0"),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0")
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}")            
            ])
        if n_offset != "":
            try:
                if settings['max_btn']:
                    btn.append(
                        [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}")]
                    )

                else:
                    btn.append(
                        [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}")]
                    )
            except KeyError:
                await save_group_settings(query.message.chat.id, 'max_btn', True)
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}")]
                )
        else:
            n_offset = 0
            btn.append(
                [InlineKeyboardButton(text="↭ ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ↭",callback_data="pages")]
            )    

        if not settings["button"]:
            cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
            time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
            remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
            cap = await get_cap(settings, remaining_seconds, files, query, total_results, search, offset)
            try:
                await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
            except MessageNotModified:
                pass
        else:
            try:
                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except MessageNotModified:
                pass
        await query.answer()
    except Exception as e:
        print(f"Error In Season - {e}")

@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, id, user = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)    
    movies = await get_poster(id, id=True)
    movie = movies.get('title')
    movie = re.sub(r"[:-]", " ", movie)
    movie = re.sub(r"\s+", " ", movie).strip()
    await query.answer(script.TOP_ALRT_MSG)
    gl = await global_filters(bot, query.message, text=movie)    
    if gl == False:
        k = await manual_filters(bot, query.message, text=movie)        
        if k == False:
            files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)           
            if files:
                k = (movie, files, offset, total_results)
                await auto_filter(bot, query, k)
            else:
                reqstr1 = query.from_user.id if query.from_user else 0
                reqstr = await bot.get_users(reqstr1)                
                if NO_RESULTS_MSG:
                    await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, movie)))               
                contact_admin_button = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔰Cʟɪᴄᴋ ʜᴇʀᴇ & ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴀᴅᴍɪɴ🔰", url=OWNER_BOTZ)]]
                )               
                k = await query.message.edit(script.MVE_NT_FND, reply_markup=contact_admin_button)
                await asyncio.sleep(30)
                await k.delete()
                
@Client.on_callback_query(filters.regex(r"action_(\w+)_(\d+)\|(.+)"))
async def handle_actions(client, callback_query):
    action, user_id, search = re.match(r"action_(\w+)_(\d+)\|(.+)", callback_query.data).groups()
    user_id = int(user_id)

    try:
        user = await client.get_users(user_id)
        search_encoded = search.replace(" ", "+")
        user_mention = f"<b>👤 Hey {user.first_name}!</b>"
        search_line = f"🔍 You searched for: <code>{search}</code>\n\n"

        if action == "uploaded":
            message_text = (
    "✅ <b>ʏᴏᴜʀ ʀᴇϙᴜᴇꜱᴛᴇᴅ ᴄᴏɴᴛᴇɴᴛ ʜᴀꜱ ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ.</b>\n\n"
    "📢 <i>ᴄʜᴇᴄᴋ ᴏᴜʀ ᴍᴏᴠɪᴇ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ʀᴇϙᴜᴇꜱᴛ ɢʀᴏᴜᴘ ᴛᴏ ɢᴇᴛ ɪᴛ. ɪꜰ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ʏᴇᴛ, ᴛᴀᴘ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴊᴏɪɴ ᴀʟʟ ᴄʜᴀɴɴᴇʟꜱ ᴀɴᴅ ɢʀᴏᴜᴘꜱ ᴀᴛ ᴏɴᴄᴇ.</i>\n\n"
    "✅ <b>আপনার রিকুয়েস্টকৃত কন্টেন্টটি সফলভাবে আপলোড করা হয়েছে।</b>\n\n"
    "📢 <i>আমাদের মুভি চ্যানেল এবং রিকুয়েস্ট গ্রুপ থেকে আপনার কন্টেন্টটি সংগ্রহ করতে পারেন। "
    "যদি এখনও জয়েন না হয়ে থাকেন, তাহলে নিচের বাটনে ক্লিক করে একবারেই সকল চ্যানেল এবং গ্রুপে জয়েন হতে পারবেন।</i>"
                )
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Jᴏɪɴ ᴏᴜʀ ᴀʟʟ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ɢʀᴏᴜᴘs ɪɴ ᴏɴᴇ ᴄʟɪᴄᴋ", url=f"https://t.me/addlist/ceobDOjc7202ZmVl")]]
            )
            await client.send_photo(
                chat_id=user_id,
                photo="https://i.postimg.cc/fySmH2GT/IMG-20250512-060032-257.jpg",
                caption=f"{user_mention}\n{search_line}{message_text}",
                reply_markup=keyboard
            )
        elif action == "spellcheck":
            message_text = (
    "❌ <b>ɪᴛ ꜱᴇᴇᴍꜱ ʏᴏᴜʀ ʀᴇϙᴜᴇꜱᴛ ʜᴀꜱ ᴀ ꜱᴘᴇʟʟɪɴɢ ᴍɪꜱᴛᴀᴋᴇ.</b>\n\n"
    "📢 <i>ᴛᴏ ɢᴇᴛ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴍᴏᴠɪᴇ ᴏʀ ꜱᴇʀɪᴇꜱ, ʏᴏᴜ ᴍᴜꜱᴛ ᴜꜱᴇ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ɴᴀᴍᴇ. "
    "ᴏᴛʜᴇʀᴡɪꜱᴇ, ᴛʜᴇ ꜰɪʟᴇ ᴡᴏɴ'ᴛ ʙᴇ ꜰᴏᴜɴᴅ. "
    "ɪꜰ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ꜱᴜʀᴇ ᴀʙᴏᴜᴛ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ɴᴀᴍᴇ, ᴘʀᴇꜱꜱ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ɪᴛ ꜰʀᴏᴍ ɢᴏᴏɢʟᴇ.</i>\n\n"
    "❌ <b>আপনি যে রিকুয়েস্টটি করেছেন সেটিতে বানান ভুল রয়েছে মনে হচ্ছে।</b>\n\n"
    "📢 <i>সঠিক মুভি বা ওয়েব সিরিজ পেতে সঠিক নাম ব্যবহার করুন। "
    "না হলে ফাইল খুঁজে পাওয়া যাবে না। "
    "যদি সঠিক নামটি না জানেন, তাহলে নিচের বাটনে ক্লিক করে সরাসরি Google থেকে সঠিক নামটি দেখে নিন।</i>"
            )
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("✏️ Cʜᴇᴄᴋ Sᴘᴇʟʟɪɴɢ ᴏɴ Gᴏᴏɢʟᴇ 🔍", url=f"https://www.google.com/search?q={search_encoded}")]]
            )
            await client.send_photo(
                chat_id=user_id,
                photo="https://i.postimg.cc/8CLst5d5/IMG-20250508-153346-518.jpg",
                caption=f"{user_mention}\n{search_line}{message_text}",
                reply_markup=keyboard
            )

        elif action == "notreleased":
            message_text = (
    "⏳ <b>ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛ ʏᴏᴜ ʀᴇϙᴜᴇꜱᴛᴇᴅ ʜᴀꜱ ɴᴏᴛ ʙᴇᴇɴ ʀᴇʟᴇᴀꜱᴇᴅ ʏᴇᴛ.</b>\n\n"
    "📢 <i>ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛ ᴡɪʟʟ ʙᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴀꜰᴛᴇʀ ɪᴛꜱ ʀᴇʟᴇᴀꜱᴇ ᴅᴀᴛᴇ. "
    "ɪꜰ ʏᴏᴜ ᴀʀᴇ ᴜɴꜱᴜʀᴇ ᴀʙᴏᴜᴛ ᴛʜᴇ ʀᴇʟᴇᴀꜱᴇ ᴅᴀᴛᴇ, ᴘʀᴇꜱꜱ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴄʜᴇᴄᴋ ɪᴛ ᴏɴ ɢᴏᴏɢʟᴇ.</i>\n\n"
    "⏳ <b>আপনি যে রিকুয়েস্টটি করেছেন, সেই কন্টেন্টটি এখনো রিলিজ হয়নি।</b>\n\n"
    "📢 <i>এই কন্টেন্টটি রিলিজ হওয়ার পরেই পাওয়া যাবে। "
    "যদি আপনি সঠিক রিলিজ ডেটটি না জানেন, তাহলে নিচের বাটনে ক্লিক করে সরাসরি Google থেকে রিলিজ ডেটটি দেখে নিতে পারেন।</i>"
            )
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🗓️ Cʜᴇᴄᴋ ʀᴇʟᴇᴀsᴇ ᴅᴀᴛᴇ 🔍", url=f"https://www.google.com/search?q={search_encoded}+release+date")]]
            )
            await client.send_photo(
                chat_id=user_id,
                photo="https://i.postimg.cc/Gppz0W2v/IMG-20250508-153539-360.jpg",
                caption=f"{user_mention}\n{search_line}{message_text}",
                reply_markup=keyboard
            )

        elif action == "processing":
            message_text = (
    "🛠️ <b>ʏᴏᴜʀ ʀᴇϙᴜᴇꜱᴛ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ʙᴇɪɴɢ ᴘʀᴏᴄᴇꜱꜱᴇᴅ.</b>\n\n"
    "📢 <i>ᴛʜᴀᴛ ᴍᴇᴀɴꜱ ɪᴛ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ʙᴇɪɴɢ ᴜᴘʟᴏᴀᴅᴇᴅ. "
    "ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ꜰᴏʀ ᴀ ꜱʜᴏʀᴛ ᴡʜɪʟᴇ. "
    "ᴏɴᴄᴇ ɪᴛ'ꜱ ᴅᴏɴᴇ, ʏᴏᴜ ᴡɪʟʟ ʀᴇᴄᴇɪᴠᴇ ᴀ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ.</i>\n\n"
    "🛠️ <b>আপনি যে কনটেন্টটির রিকুয়েস্ট করেছেন, সেটি এখন প্রসেসিং এ আছে।</b>\n\n"
    "📢 <i>মানে, এটি বর্তমানে আপলোড হচ্ছে। "
    "তাই আপনাকে কিছু সময় অপেক্ষা করতে হবে। "
    "আপলোড হয়ে গেলে আপনাকে নোটিফাই করা হবে।</i>"
            )
            final_msg = f"{user_mention}\n{search_line}{message_text}"
            await client.send_message(user_id, final_msg)

        elif action == "typeinenglish":
            message_text = (
    "✍️ <b>ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛ ʏᴏᴜ ʀᴇϙᴜᴇꜱᴛᴇᴅ ɪꜱ ᴀᴠᴀɪʟᴀʙʟᴇ, ʙᴜᴛ ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴛʏᴘᴇ ᴛʜᴇ ɴᴀᴍᴇ ɪɴ ᴇɴɢʟɪꜱʜ.</b>\n\n"
    "📢 <i>ᴊᴜꜱᴛ ᴡʀɪᴛᴇ ᴛʜᴇ ᴍᴏᴠɪᴇ ᴏʀ ꜱᴇʀɪᴇꜱ ɴᴀᴍᴇ ɪɴ ᴇɴɢʟɪꜱʜ, ᴏᴛʜᴇʀᴡɪꜱᴇ, ᴛʜᴇ ꜰɪʟᴇ ᴡᴏɴ'ᴛ ʙᴇ ꜰᴏᴜɴᴅ. "
    "ɪꜰ ʏᴏᴜ ᴀʀᴇ ᴜɴꜱᴜʀᴇ ᴀʙᴏᴜᴛ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ꜱᴘᴇʟʟɪɴɢ, ᴛᴀᴘ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ɪᴛ ꜰʀᴏᴍ ɢᴏᴏɢʟᴇ.</i>\n\n"
    "✍️ <b>আপনি যে কন্টেন্টটি রিকুয়েস্ট করেছেন, সেটি আছে। কিন্তু আপনাকে সেটার নাম ইংরেজিতে লিখতে হবে।</b>\n\n"
    "📢 <i>শুধুমাত্র কন্টেন্টটির নাম ইংরেজিতে লিখুন। "
    "যদি সঠিক বানান না জানেন, তাহলে নিচের বাটনে ক্লিক করে সরাসরি Google থেকে দেখে নিতে পারেন।</i>"
            )
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔍 Cʜᴇᴄᴋ ᴛʜᴇ Eɴɢʟɪsʜ ɴᴀᴍᴇ ᴏɴ Gᴏᴏɢʟᴇ ✏️", url=f"https://www.google.com/search?q={search_encoded}")]]
            )
            await client.send_photo(
                chat_id=user_id,
                photo="https://i.postimg.cc/sgS1gnG7/check-37583-1280.png",
                caption=f"{user_mention}\n{search_line}{message_text}",
                reply_markup=keyboard
            )

        elif action == "notavailable":
            message_text = (
    "❌ <b>ʀᴇϙᴜᴇꜱᴛᴇᴅ ᴄᴏɴᴛᴇɴᴛ ɪꜱ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ᴀᴛ ᴛʜᴇ ᴍᴏᴍᴇɴᴛ.</b>\n\n"
    "📢 <i>ɪᴛ ᴍɪɢʜᴛ ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ᴏʀ ɴᴇᴠᴇʀ ᴜᴘʟᴏᴀᴅᴇᴅ. "
    "ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɴᴏᴛʜᴇʀ ᴄᴏɴᴛᴇɴᴛ ᴏʀ ᴡᴀɪᴛ ᴀ ꜰᴇᴡ ᴍᴏᴍᴇɴᴛꜱ ᴀɴᴅ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ. "
    "ɪꜰ ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛ ʙᴇᴄᴏᴍᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ, ʏᴏᴜ ᴡɪʟʟ ʙᴇ ɴᴏᴛɪꜰɪᴇᴅ.</i>\n\n"
    "❌ <b>দুঃখিত, আপনি যে কন্টেন্টটির জন্য রিকোয়েস্ট করেছেন, সেটি বর্তমানে আমাদের কাছে এভেলেবল নেই।</b>\n\n"
    "📢 <i>সেটা হয়তো রিমুভ করা হয়েছে বা এখনো আপলোড করা হয়নি। "
    "তাই দয়া করে অন্য কোনো কন্টেন্টের জন্য চেষ্টা করুন অথবা কিছু সময় পর আবার চেষ্টা করুন। "
    "যদি কন্টেন্টটি তখন এভেলেবল হয়, তাহলে আপনাকে জানিয়ে দেওয়া হবে।</i>"
            )
            final_msg = f"{user_mention}\n{search_line}{message_text}"
            await client.send_message(user_id, final_msg)

        elif action == "contact":  
            message_text = (
    "📞 <b>ɴᴇᴇᴅ ʜᴇʟᴘ?</b>\n\n"
    "📢 <i>ɪꜰ ʏᴏᴜ'ʀᴇ ꜰᴀᴄɪɴɢ ᴀɴʏ ɪssᴜᴇ ᴏʀ ɴᴇᴇᴅ ᴀssɪsᴛᴀɴᴄᴇ, "
    "ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ᴀᴅᴍɪɴ.</i>\n\n"
    "📞 <b>ᴅᴏ ʏᴏᴜ ᴛʜɪɴᴋ ᴛʜᴇʀᴇ ɪs ᴀɴ ɪssᴜᴇ?</b>\n"
    "❗ <i>ɪꜰ ʏᴏᴜ ᴀʀᴇ ᴇxᴘᴇʀɪᴇɴᴄɪɴɢ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ ᴏʀ ɪꜰ ʏᴏᴜ ᴛʰɪɴᴋ "
    "ɪᴛ'ꜱ ɴᴇᴇᴅɪɴɢ ᴀᴅᴍɪɴ'ꜱ ᴀssɪsᴛᴀɴᴄᴇ, ʏᴏᴜ ᴄᴀɴ ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ᴀᴅᴍɪɴ "
    "ᴄᴏᴍꜱ ᴛᴏ ʏᴏᴜ ᴀɴᴅ ʀᴇᴇᴠᴇᴀʟ ʏᴏᴜʀ ɪssᴜᴇ ᴀɴᴅ ᴛʜᴇʏ ᴡɪʟʟ ʜᴇʟᴘ "
    "ʏᴏᴜ ᴡɪᴛʜ ɪᴛ.</i>\n\n"
    "📢 <i>ʏᴏᴜ ᴄᴀɴ ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ᴀᴅᴍɪɴ ᴇᴀꜱɪʟʏ ʙʏ ᴄʟɪᴄᴋɪɴɢ ᴏɴ ᴛʜᴇ "
    "ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴀɴᴅ ɢᴇᴛ ʏᴏᴜʀ ɪssᴜᴇ ʀᴇsᴏʟᴠᴇᴅ ᴛᴏᴏ.</i>\n\n"
    "📞 <b>আপনার মনে হচ্ছে কোনো সমস্যা হয়েছে, তাই না? যদি কোন সমস্যা হয়, "
    "তাহলে আমাদের এডমিনের সাথে যোগাযোগ করতে পারেন।</b>\n\n"
    "📢 <i>আপনার সমস্যাটি এডমিন সমাধান করে দিবেন, আশা করছি। "
    "নিচের বাটনে ক্লিক করে আপনি সরাসরি এডমিনের সাথে যোগাযোগ করতে পারবেন।</i>"
            )
            keyboard = InlineKeyboardMarkup(  
                [[InlineKeyboardButton("💬 Cᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ 📞", url=f"https://t.me/Prime_Admin_Support_ProBot")]]  
            )  
            await client.send_photo(  
                chat_id=user_id,  
                photo="https://i.postimg.cc/fyC37H5Y/In-Shot-20250509-130447862.jpg",  
                caption=f"{user_mention}\n{search_line}{message_text}",  
                reply_markup=keyboard  
            )  

        elif action == "premium":  
            message_text = (
    "💎 <b>ɪᴛʜɪs ᴄᴏɴᴛᴇɴᴛ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ꜰᴏʀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ᴏɴʟʏ.</b> 🎬\n"
    "🎥 ᴡᴇ ʜᴀᴠᴇ ᴛʜᴇ ғɪʟᴇ ʏᴏᴜ'ʀᴇ ʟᴏᴏᴋɪɴɢ ꜰᴏʀ, ʙᴜᴛ ʏᴏᴜ'ʟʟ ɴᴇᴇᴅ ᴛᴏ ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ ᴀᴄᴄᴇss ɪᴛ. 🔑\n\n"
    "💡 ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ ᴀɴᴅ sᴜʙsᴄʀɪʙᴇ. 🚀\n\n"
    "💎 <b>এই কনটেন্টটি শুধুমাত্র প্রিমিয়াম ইউজারদের জন্য উপলব্ধ।</b> 🎥\n"
    "🔓 আমাদের কাছে আপনি যে ফাইলটি খুঁজছেন, সেটি রয়েছে, তবে এটি অ্যাক্সেস করতে প্রিমিয়াম সাবস্ক্রিপশন করতে হবে।\n\n"
    "🔔 আরও জানার জন্য এবং সাবস্ক্রাইব করতে নিচের বাটনে ক্লিক করুন। 👇"
            )
            keyboard = InlineKeyboardMarkup(  
                [[InlineKeyboardButton("💎 Gᴇᴛ Pʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss 🚀", callback_data="premium2")]]  
            )  
            await client.send_photo(  
                chat_id=user_id,  
                photo="https://i.postimg.cc/j2v5nZ4m/file-000000007d0461f88bc7fa3cfa687bd4-conversation-id-681d5240-27b8-800e-a7f8-f4268a53fe3c-message-i.png",  
                caption=f"{user_mention}\n{search_line}{message_text}",  
                reply_markup=keyboard  
            )  

        else:
            message_text = "⚠️ Invalid action."
            final_msg = f"{user_mention}\n{search_line}{message_text}"
            await client.send_message(user_id, final_msg)

        await callback_query.answer("✅ Message sent to the user.", show_alert=True)

    except Exception:
        await callback_query.answer("❗ The user has not started the bot yet!", show_alert=True)
            

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    lazyData = query.data
    try:
        link = await client.create_chat_invite_link(int(REQST_CHANNEL))
    except:
        pass
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "gfiltersdeleteallconfirm":
        await del_allg(query.message, 'gfilters')
        await query.answer("ᴅᴏɴᴇ !")
        return
    elif query.data == "gfiltersdeleteallcancel": 
        await query.message.reply_to_message.delete()
        await query.message.delete()
        await query.answer("ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ !")
        return
      
    elif "gfilteralert" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_gfilter('gfilters', keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)

    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
        
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        user = query.message.reply_to_message.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(script.ALRT_TXT, show_alert=True)
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file_id}")          
                            
    elif query.data.startswith("sendfiles"):
        clicked = query.from_user.id
        ident, key = query.data.split("#") 
        settings = await get_settings(query.message.chat.id)
        try:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=allfiles_{query.message.chat.id}_{key}")
            return
        except UserIsBlocked:
            await query.answer('Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles3_{key}")
        except Exception as e:
            logger.exception(e)
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles4_{key}")
            
    elif query.data.startswith("del"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"
        await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")

    elif query.data == "pages":
        await query.answer()    
    
    elif query.data.startswith("killfilesdq"):
        ident, keyword = query.data.split("#")
        await query.message.edit_text(f"<b>Fetching Files for your query {keyword} on DB... Please wait...</b>")
        files, total = await get_bad_files(keyword)
        await query.message.edit_text("<b>ꜰɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ ᴘʀᴏᴄᴇꜱꜱ ᴡɪʟʟ ꜱᴛᴀʀᴛ ɪɴ 5 ꜱᴇᴄᴏɴᴅꜱ !</b>")
        await asyncio.sleep(5)
        deleted = 0
        async with lock:
            try:
                for file in files:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media.collection.delete_one({
                        '_id': file_ids,
                    })
                    if not result.deleted_count and MULTIPLE_DB:
                        result = await Media2.collection.delete_one({
                            '_id': file_ids,
                        })
                    if result.deleted_count:
                        logger.info(f'ꜰɪʟᴇ ꜰᴏᴜɴᴅ ꜰᴏʀ ʏᴏᴜʀ ǫᴜᴇʀʏ {keyword}! ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ꜰʀᴏᴍ ᴅᴀᴛᴀʙᴀꜱᴇ.')
                    deleted += 1
                    if deleted % 20 == 0:
                        await query.message.edit_text(f"<b>ᴘʀᴏᴄᴇꜱꜱ ꜱᴛᴀʀᴛᴇᴅ ꜰᴏʀ ᴅᴇʟᴇᴛɪɴɢ ꜰɪʟᴇꜱ ꜰʀᴏᴍ ᴅʙ. ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ꜰɪʟᴇꜱ ꜰʀᴏᴍ ᴅʙ ꜰᴏʀ ʏᴏᴜʀ ǫᴜᴇʀʏ {keyword} !\n\nᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...</b>")
            except Exception as e:
                print(f"Error In killfiledq -{e}")
                await query.message.edit_text(f'Error: {e}')
            else:
                await query.message.edit_text(f"<b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ꜰᴏʀ ꜰɪʟᴇ ᴅᴇʟᴇᴛᴀᴛɪᴏɴ !\n\nꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ꜰɪʟᴇꜱ ꜰʀᴏᴍ ᴅʙ ꜰᴏʀ ʏᴏᴜʀ ǫᴜᴇʀʏ {keyword}.</b>")
    
    elif query.data.startswith("opnsetgrp"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ʀɪɢʜᴛꜱ ᴛᴏ ᴅᴏ ᴛʜɪꜱ !", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('ʀᴇꜱᴜʟᴛ ᴘᴀɢᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ʙᴜᴛᴛᴏɴ' if settings["button"] else 'ᴛᴇxᴛ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜰɪʟᴇ ꜱᴇɴᴅ ᴍᴏᴅᴇ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ꜱᴛᴀʀᴛ' if settings["botpm"] else 'ᴀᴜᴛᴏ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜰɪʟᴇ ꜱᴇᴄᴜʀᴇ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["file_secure"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ɪᴍᴅʙ ᴘᴏꜱᴛᴇʀ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["imdb"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜱᴘᴇʟʟ ᴄʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["spell_check"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴡᴇʟᴄᴏᴍᴇ ᴍꜱɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["welcome"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["auto_delete"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["auto_ffilter"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴍᴀx ʙᴜᴛᴛᴏɴꜱ',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('⇋ ᴄʟᴏꜱᴇ ꜱᴇᴛᴛɪɴɢꜱ ᴍᴇɴᴜ ⇋', 
                                         callback_data='close_data'
                                         )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=f"<b>ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ {title} ᴀꜱ ʏᴏᴜ ᴡɪꜱʜ ⚙</b>",
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML
            )
            await query.message.edit_reply_markup(reply_markup)
        
    elif query.data.startswith("opnsetpm"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        btn2 = [[
                 InlineKeyboardButton("ᴄʜᴇᴄᴋ ᴍʏ ᴅᴍ 🗳️", url=f"telegram.me/{temp.U_NAME}")
               ]]
        reply_markup = InlineKeyboardMarkup(btn2)
        await query.message.edit_text(f"<b>ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ ғᴏʀ {title} ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ʏᴏᴜ ʙʏ ᴅᴍ.</b>")
        await query.message.edit_reply_markup(reply_markup)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('ʀᴇꜱᴜʟᴛ ᴘᴀɢᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ʙᴜᴛᴛᴏɴ' if settings["button"] else 'ᴛᴇxᴛ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜰɪʟᴇ ꜱᴇɴᴅ ᴍᴏᴅᴇ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ꜱᴛᴀʀᴛ' if settings["botpm"] else 'ᴀᴜᴛᴏ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜰɪʟᴇ ꜱᴇᴄᴜʀᴇ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["file_secure"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ɪᴍᴅʙ ᴘᴏꜱᴛᴇʀ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["imdb"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜱᴘᴇʟʟ ᴄʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["spell_check"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴡᴇʟᴄᴏᴍᴇ ᴍꜱɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["welcome"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["auto_delete"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["auto_ffilter"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴍᴀx ʙᴜᴛᴛᴏɴꜱ',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('⇋ ᴄʟᴏꜱᴇ ꜱᴇᴛᴛɪɴɢꜱ ᴍᴇɴᴜ ⇋', 
                                         callback_data='close_data'
                                         )
                ]
        ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await client.send_message(
                chat_id=userid,
                text=f"<b>ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ {title} ᴀꜱ ʏᴏᴜ ᴡɪꜱʜ ⚙</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=query.message.id
            )

    elif query.data.startswith("show_option"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("• ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ •", callback_data=f"unavailable#{from_user}"),
                InlineKeyboardButton("• ᴜᴘʟᴏᴀᴅᴇᴅ •", callback_data=f"uploaded#{from_user}")
             ],[
                InlineKeyboardButton("• ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ •", callback_data=f"already_available#{from_user}")
             ],[
                InlineKeyboardButton("• ɴᴏᴛ ʀᴇʟᴇᴀꜱᴇᴅ •", callback_data=f"Not_Released#{from_user}"),
                InlineKeyboardButton("• ᴡᴏʀɴɢ ꜱᴘᴇʟʟɪɴɢ •", callback_data=f"Wrong_Spelling#{from_user}")
             ],[
                InlineKeyboardButton("• ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ •", callback_data=f"Not_Available#{from_user}")
             ]]
        btn2 = [[
                 InlineKeyboardButton("ᴠɪᴇᴡ ꜱᴛᴀᴛᴜꜱ", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Hᴇʀᴇ ᴀʀᴇ ᴛʜᴇ ᴏᴘᴛɪᴏɴs !")
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)
        
    elif query.data.startswith("unavailable"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("• ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ •", callback_data=f"unalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ', url=link.invite_link),
                 InlineKeyboardButton("ᴠɪᴇᴡ ꜱᴛᴀᴛᴜꜱ", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Uɴᴀᴠᴀɪʟᴀʙʟᴇ !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<u>{content}</u>\n\n<b>Hᴇʏ {user.mention}, Sᴏʀʀʏ Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<u>{content}</u>\n\n<b>Hᴇʏ {user.mention}, Sᴏʀʀʏ Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)
            
    elif query.data.startswith("Not_Released"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("• ɴᴏᴛ ʀᴇʟᴇᴀꜱᴇᴅ •", callback_data=f"unalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ', url=link.invite_link),
                 InlineKeyboardButton("ᴠɪᴇᴡ ꜱᴛᴀᴛᴜꜱ", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Uɴᴀᴠᴀɪʟᴀʙʟᴇ !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<u>{content}</u>\n\n<b>Hᴇʏ {user.mention}, The movie you requested has not been released yet. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<u>{content}</u>\n\n<b>Hᴇʏ {user.mention}, The movie you requested has not been released yet. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("Wrong_Spelling"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("• ᴡᴏʀɴɢ ꜱᴘᴇʟʟɪɴɢ •", callback_data=f"unalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ', url=link.invite_link),
                 InlineKeyboardButton("ᴠɪᴇᴡ ꜱᴛᴀᴛᴜꜱ", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Type Correct Spelling !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<u>{content}</u>\n\n<b>Hᴇʏ {user.mention}, The spelling of the movie you requested is incorrect. Please type the correct spelling of the movie name and try again.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<u>{content}</u>\n\n<b>Hᴇʏ {user.mention}, The spelling of the movie you requested is incorrect. Please type the correct spelling of the movie name and try again.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("Not_Available"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("• ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ •", callback_data=f"unalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ', url=link.invite_link),
                 InlineKeyboardButton("ᴠɪᴇᴡ ꜱᴛᴀᴛᴜꜱ", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Not Available In The Hindi  !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<u>{content}</u>\n\n<b>Hᴇʏ {user.mention}, Your request is not available in the Hindi language. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<u>{content}</u>\n\n<b>Hᴇʏ {user.mention}, Your request is not available in the Hindi language. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("uploaded"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("• ᴜᴘʟᴏᴀᴅᴇᴅ •", callback_data=f"upalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ', url=link.invite_link),
                 InlineKeyboardButton("ᴠɪᴇᴡ ꜱᴛᴀᴛᴜꜱ", url=f"{query.message.link}")
               ],[
                 InlineKeyboardButton("🔍 ꜱᴇᴀʀᴄʜ ʜᴇʀᴇ 🔎", url=GRP_LNK)
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Uᴘʟᴏᴀᴅᴇᴅ !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<u>{content}</u>\n\n<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<u>{content}</u>\n\n<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("already_available"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("• ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ •", callback_data=f"alalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ', url=link.invite_link),
                 InlineKeyboardButton("ᴠɪᴇᴡ ꜱᴛᴀᴛᴜꜱ", url=f"{query.message.link}")
               ],[
                 InlineKeyboardButton("🔍 ꜱᴇᴀʀᴄʜ ʜᴇʀᴇ 🔎", url=GRP_LNK)
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<u>{content}</u>\n\n<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴏᴜʀ ʙᴏᴛ's ᴅᴀᴛᴀʙᴀsᴇ. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<u>{content}</u>\n\n<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴏᴜʀ ʙᴏᴛ's ᴅᴀᴛᴀʙᴀsᴇ. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)
            
    
    elif query.data.startswith("alalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ !", show_alert=True)
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("upalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Uᴘʟᴏᴀᴅᴇᴅ !", show_alert=True)
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)
        
    elif query.data.startswith("unalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Uɴᴀᴠᴀɪʟᴀʙʟᴇ !", show_alert=True)
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    
    elif lazyData.startswith("streamfile"):
        _, file_id = lazyData.split(":")
        try:
            user_id = query.from_user.id
            username =  query.from_user.mention 
            silent_msg = await client.send_cached_media(
                chat_id=BIN_CHANNEL,
                file_id=file_id,
            )
            fileName = {quote_plus(get_name(silent_msg))}
            silent_stream = f"{URL}watch/{str(silent_msg.id)}/{quote_plus(get_name(silent_msg))}?hash={get_hash(silent_msg)}"
            silent_download = f"{URL}{str(silent_msg.id)}/{quote_plus(get_name(silent_msg))}?hash={get_hash(silent_msg)}"
            await silent_msg.reply_text(
                text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ @iPapkornprimebot ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}",
                quote=True,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Fast Download 🚀", url=silent_download),  # we download Link
                                                    InlineKeyboardButton('🖥️ Watch online 🖥️', url=silent_stream)]])  # web stream Link
            )
            SilentXBotz = await query.message.reply_text(
                text="•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ☠︎⚔",
                quote=True,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Fast Download 🚀", url=silent_download),  # we download Link
                                                    InlineKeyboardButton('🖥️ Watch online 🖥️', url=silent_stream)]])  # web stream Link
            )              
            await asyncio.sleep(DELETE_TIME) 
            await SilentXBotz.delete()
            return            
        except Exception as e:
            print(e)
            await query.answer(f"⚠️ SOMETHING WENT WRONG \n\n{e}", show_alert=True)
            return
           
    
    elif query.data == "pagesn1":
        await query.answer(text=script.PAGE_TXT, show_alert=True)

    elif query.data == "reqinfo":
        await query.answer(text=script.REQINFO, show_alert=True)

    elif query.data == "select":
        await query.answer(text=script.SELECT, show_alert=True)

    elif query.data == "sinfo":
        await query.answer(text=script.SINFO, show_alert=True)

    elif query.data == "start":
        buttons = [[
                    InlineKeyboardButton('+ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ +', url=f'http://telegram.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('• ᴇᴀʀɴ ᴍᴏɴᴇʏ •', callback_data="earn"),
                    InlineKeyboardButton('• ᴜᴘɢʀᴀᴅᴇ ᴘʟᴀɴ •', callback_data="premium"),
                ],[
                    InlineKeyboardButton('• ʜᴇʟᴘ •', callback_data='features'),
                    InlineKeyboardButton('• ᴀʙᴏᴜᴛ ʙᴏᴛᴢ •', callback_data='botz_about')
                ],[
                    InlineKeyboardButton('✧ ᴄʀᴇᴀᴛᴏʀ ✧', url=OWNER_LNK)
                ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    
    elif query.data == "botz_about":
        try:
            btn = [[
                InlineKeyboardButton("• ʀᴇQᴜᴇsᴛ ɢʀᴏᴜᴘ •", url=GRP_LNK),
                InlineKeyboardButton("• Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ •", url=OWNER_SUPP)
            ],[
                InlineKeyboardButton("• ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ •", url=UPDATE_CHANNEL_LNK)
            ],[
                InlineKeyboardButton("• Mᴏᴠɪᴇs Cʜᴀɴɴᴇʟ •", url=CHNL_LNK),
                InlineKeyboardButton("• ᴀʙᴏᴜᴛ •", callback_data="bot")
            ],[
                InlineKeyboardButton("⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋", callback_data="start")
            ]]
            reply_markup = InlineKeyboardMarkup(btn)

            await client.edit_message_media(
                chat_id=query.message.chat.id,
                message_id=query.message.id,
                media=InputMediaPhoto(
                    media="https://i.ibb.co/DDKfvJCX/photo-2025-04-14-08-24-42-7493081901167542280.jpg",
                    caption="ʜᴇʀᴇ ɪꜱ ᴀʙᴏᴜᴛ ᴛʜᴇ ʙᴏᴛ ᴀɴᴅ ɪᴛꜱ ꜰᴇᴀᴛᴜʀᴇꜱ...",
                    parse_mode=enums.ParseMode.HTML
                ),
                reply_markup=reply_markup
            )
        except Exception as e:
            print(e)
            
    elif query.data == "give_trial":
        try:
            user_id = query.from_user.id
            has_free_trial = await db.check_trial_status(user_id)
            if has_free_trial:
                await query.answer("🚸 ʏᴏᴜ'ᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴄʟᴀɪᴍᴇᴅ ʏᴏᴜʀ ꜰʀᴇᴇ ᴛʀɪᴀʟ ᴏɴᴄᴇ !\n\n📌 ᴄʜᴇᴄᴋᴏᴜᴛ ᴏᴜʀ ᴘʟᴀɴꜱ ʙʏ : /plan", show_alert=True)
                return
            else:            
                await db.give_free_trial(user_id)
                await query.message.reply_text(
                    text="<b>🥳 ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ\n\n🎉 ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ꜰʀᴇᴇ ᴛʀᴀɪʟ ꜰᴏʀ <u>5 ᴍɪɴᴜᴛᴇs</u> ꜰʀᴏᴍ ɴᴏᴡ !</b>",
                    quote=False,
                    disable_web_page_preview=True,                  
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💸 ᴄʜᴇᴄᴋᴏᴜᴛ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ 💸", callback_data='seeplans')]]))
                return    
        except Exception as e:
            print(e)

    elif query.data == "premium":
        try:
            btn = [[
                InlineKeyboardButton('• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •', callback_data='buy'),
            ],[
                InlineKeyboardButton('• ʀᴇꜰᴇʀ ꜰʀɪᴇɴᴅꜱ', callback_data='reffff'),
                InlineKeyboardButton('ꜰʀᴇᴇ ᴛʀɪᴀʟ •', callback_data='give_trial')
            ],[            
                InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='start')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)                        
            await client.edit_message_media(                
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))                       
            )
            await query.message.edit_text(
                text=script.BPREMIUM_TXT,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            print(e)
    elif query.data == "premium2":
        try:
            btn = [[
                InlineKeyboardButton('• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •', callback_data='buy'),
            ],[
                InlineKeyboardButton('• ʀᴇꜰᴇʀ ꜰʀɪᴇɴᴅꜱ', callback_data='reffff'),
                InlineKeyboardButton('ꜰʀᴇᴇ ᴛʀɪᴀʟ •', callback_data='give_trial')
            ],[            
                InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='start'),
            ],[
                InlineKeyboardButton('🚫 ᴄʟᴏꜱᴇ 🚫', callback_data='close_data')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)                        
            
            await query.message.reply_photo(
                photo=random.choice(PICS),
                caption=script.BPREMIUM_TXT,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            print(e)

    elif query.data == "buy":
        try:
            btn = [[ 
                InlineKeyboardButton('• ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ •', url=OWNER_BOTZ),
            ],[
                InlineKeyboardButton('🚫 ᴄʟᴏꜱᴇ 🚫', callback_data='close_data')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.reply_photo(
                photo=(SUBSCRIPTION),
                caption=script.PREMIUM_TEXT.format(query.from_user.mention),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            ) 
        except Exception as e:
            print(e)

    elif query.data == "features":
        try:
            buttons = [[
                InlineKeyboardButton('• ꜰɪʟᴛᴇʀꜱ •', callback_data='filters'),
                InlineKeyboardButton('• ꜰɪʟᴇ ꜱᴛᴏʀᴇ •', callback_data='store_file')
            ],[
                InlineKeyboardButton('• ꜱᴇᴛᴛɪɴɢꜱ •', callback_data='setting_btn')        
            ],[
                InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='start')
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
            await query.message.edit_text(
                text=script.FEATURES_TXT,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            print(e)

    
    elif query.data == "earn":
        try:
            btn = [
                [InlineKeyboardButton('💬 ᴘʀɪᴍᴇ ʙᴏᴛᴢ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ 💬', url='https://t.me/Prime_Botz_Support')],
                [InlineKeyboardButton('🚫 ᴄʟᴏꜱᴇ 🚫', callback_data='close_data')]
            ]
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.reply(
                text=script.EARN_INFO.format(temp.B_LINK),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            print(e)

    elif query.data == "filters":
        try:
            buttons = [[
                InlineKeyboardButton('• ᴍᴀɴᴜᴀʟ ꜰɪʟᴛᴇʀꜱ •', callback_data='manuelfilter'),
                InlineKeyboardButton('• ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ •', callback_data='autofilter')
            ],[
                InlineKeyboardButton('• ɢʟᴏʙᴀʟ ꜰɪʟᴛᴇʀꜱ •', callback_data='global_filters'),
                InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='features')
            ]]        
            reply_markup = InlineKeyboardMarkup(buttons)
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
            await query.message.edit_text(
                text=script.ALL_FILTERS.format(query.from_user.mention),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            print(e)

    elif query.data == "global_filters":
        buttons = [[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='filters')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.GFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
    )

    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='filters'),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='filters')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "store_file":
        buttons = [[
            InlineKeyboardButton('⇍ ʙᴀᴄᴋ ⇏', callback_data='features')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.FILE_STORE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        ) 

    elif query.data == "setting_btn":
        buttons = [[
            InlineKeyboardButton('⇍ ʙᴀᴄᴋ ⇏', callback_data='features')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SETTING_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
                    
    elif query.data == "bot":
        buttons = [[
            InlineKeyboardButton('‼️ ᴅɪꜱᴄʟᴀɪᴍᴇʀ ‼️', callback_data='disclaimer'),
            InlineKeyboardButton ('• ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ 📜', url=OWNER_BOTZ),
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.U_NAME, temp.B_NAME, OWNER_LNK),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ 📜', url=OWNER_BOTZ),
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='bot')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "ref_point":
        await query.answer(f'You Have: {referdb.get_refer_points(query.from_user.id)} Refferal points.', show_alert=True)
    
    
    elif query.data == "disclaimer":
            btn = [[
                    InlineKeyboardButton("⇋ ʙᴀᴄᴋ ⇋", callback_data="bot")
                  ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_text(
                text=(script.DISCLAIMER_TXT),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML 
            )
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            await query.answer(script.ALRT_TXT, show_alert=True)
            return
        if status == "True":
            await save_group_settings(int(grp_id), set_type, False)
            await query.answer("ᴏꜰꜰ ✗")
        else:
            await save_group_settings(int(grp_id), set_type, True)
            await query.answer("ᴏɴ ✓")
        settings = await get_settings(int(grp_id))
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('ʀᴇꜱᴜʟᴛ ᴘᴀɢᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ʙᴜᴛᴛᴏɴ' if settings["button"] else 'ᴛᴇxᴛ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜰɪʟᴇ ꜱᴇɴᴅ ᴍᴏᴅᴇ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ꜱᴛᴀʀᴛ' if settings["botpm"] else 'ᴀᴜᴛᴏ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜰɪʟᴇ ꜱᴇᴄᴜʀᴇ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["file_secure"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ɪᴍᴅʙ ᴘᴏꜱᴛᴇʀ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["imdb"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜱᴘᴇʟʟ ᴄʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["spell_check"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴡᴇʟᴄᴏᴍᴇ ᴍꜱɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["welcome"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["auto_delete"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["auto_ffilter"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴍᴀx ʙᴜᴛᴛᴏɴꜱ',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('⇋ ᴄʟᴏꜱᴇ ꜱᴇᴛᴛɪɴɢꜱ ᴍᴇɴᴜ ⇋', 
                                         callback_data='close_data'
                                         )
                ]
        ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer(MSG_ALRT)

    
async def auto_filter(client, msg, spoll=False):
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()

    if not spoll:
        message = msg
        if message.text.startswith("/"):
            return

        if re.findall(r"((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return

        if len(message.text) < 100:
            search = message.text.lower()
            m = await message.reply_text(
                f'🤖 <i>{search} <b>sᴇᴀʀᴄʜɪɴɢ...</b></i>',
                reply_to_message_id=message.id
            )

            # প্রাসঙ্গিক শব্দ বাদ দিয়ে ক্লিন সার্চ তৈরি করা
            find = search.split(" ")
            search = ""
            removes = ["in", "upload", "series", "full", "horror", "thriller", "mystery", "print", "file"]
            for x in find:
                if x in removes:
                    continue
                search += x + " "
            search = search.replace("-", " ").replace(":", "")

            # সার্চ করা
            files, offset, total_results = await get_search_results(message.chat.id, search, offset=0, filter=True)
            settings = await get_settings(message.chat.id)

            # কিছু না পেলে, অ্যাডভান্স চেকিং আগে
            if not files:
                if settings["spell_check"]:
                    ai_sts = await m.edit('🤖 ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ, ᴀɪ ɪꜱ ᴄʜᴇᴄᴋɪɴɢ ʏᴏᴜʀ ꜱᴘᴇʟʟɪɴɢ...')
                    is_misspelled = await ai_spell_check(chat_id=message.chat.id, wrong_name=search)

                    if is_misspelled:
                        await ai_sts.edit(
                            f'<b>✅ Aɪ Sᴜɢɢᴇsᴛᴇᴅ ᴍᴇ<code> {is_misspelled}</code>\nSᴏ Iᴍ Sᴇᴀʀᴄʜɪɴɢ ғᴏʀ <code>{is_misspelled}</code></b>'
                        )
                        await asyncio.sleep(2)
                        message.text = is_misspelled
                        await ai_sts.delete()
                        return await auto_filter(client, message)

                    await ai_sts.delete()

                    # অ্যাডভান্স চেকিং
                    found = await advantage_spell_chok(client, message)
                    if found:
                        return

                # অ্যাডভান্স চেকিং না পেলে, চ্যানেলে পোস্ট করা হবে
                await client.send_message(  
    req_channel,
    f"✨ **🚫 ɴᴏ ꜰɪʟᴇ ʀᴇǫᴜᴇsᴛᴇᴅ 🚫** ✨\n\n"
    f"🎬 **ꜰɪʟᴇ ɴᴀᴍᴇ:** `{search}`\n"
    f"🆔 **ᴜsᴇʀ ɪᴅ:** [ᴠɪᴇᴡ ᴩʀᴏꜰɪʟᴇ](tg://openmessage?user_id={message.from_user.id})\n"
    f"👤 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** `{message.from_user.first_name}`\n"
    f"⏰ **ʀᴇǫᴜᴇsᴛᴇᴅ ᴏɴ:** `{datetime.now().strftime('%d %B %Y, %I:%M %p')}`\n"
    f"💌 **sᴛᴀᴛᴜs:** ᴩᴇɴᴅɪɴɢ 🔄\n", 
    reply_markup = InlineKeyboardMarkup([
    # ✅ বড় বোতাম - Uploaded Done
    [InlineKeyboardButton("✅ ᴜᴩʟᴏᴀᴅᴇᴅ ᴅᴏɴᴇ ✅", callback_data=f"action_uploaded_{message.from_user.id}|{search.strip()}")],

    # ❌ পাশাপাশি দুইটা ছোট বোতাম - Spelling Check & Not Released
    [
        InlineKeyboardButton("❌ ᴄʜᴇᴄᴋ sᴩᴇʟʟɪɴɢ", callback_data=f"action_spellcheck_{message.from_user.id}|{search.strip()}"),
        InlineKeyboardButton("⏳ ɴᴏᴛ ʀᴇʟᴇᴀsᴇᴅ ʏᴇᴛ", callback_data=f"action_notreleased_{message.from_user.id}|{search.strip()}")
    ],

    # 🔎 বড় বোতাম - Google Search
    [InlineKeyboardButton("🔎 sᴇᴀʀᴄʜ ᴀɴᴅ ᴄʜᴇᴄᴋ ᴏɴ ɢᴏᴏɢʟᴇ 🔍", url=f"https://www.google.com/search?q={search.replace(' ', '+')}")],
    # ⚙️ পাশাপাশি দুইটা বড় বোতাম - Processing & Type in English
    [
        InlineKeyboardButton("🛠️ ᴜɴᴅᴇʀ ᴩʀᴏᴄᴇssɪɴɢ", callback_data=f"action_processing_{message.from_user.id}|{search.strip()}"),
        InlineKeyboardButton("🔤 ᴛʏᴩᴇ ɪɴ ᴇɴɢʟɪsʜ", callback_data=f"action_typeinenglish_{message.from_user.id}|{search.strip()}")
    ],
    # 📞 বড় বোতাম - Contact for Problem
    [InlineKeyboardButton("📞 ᴄᴏɴᴛᴀᴄᴛ ꜰᴏʀ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ 💬", callback_data=f"action_contact_{message.from_user.id}|{search.strip()}")],        
    # ❗ পাশাপাশি দুইটা - Not Available & Premium Required
    [
        InlineKeyboardButton("🚫 ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ", callback_data=f"action_notavailable_{message.from_user.id}|{search.strip()}"),
        InlineKeyboardButton("💎 ᴩʀᴇᴍɪᴜᴍ ʀᴇǫᴜɪʀᴇᴅ", callback_data=f"action_premium_{message.from_user.id}|{search.strip()}")
    ],
    # 💥 বড় বোতাম - Close
    [InlineKeyboardButton("💥 ᴄʟᴏsᴇ 💥", callback_data="close_data")]
])
                )
                return
    else:
        message = msg.message.reply_to_message
        search, files, offset, total_results = spoll
        m = await message.reply_text(
            f'🤖 <i>{search} <b>sᴇᴀʀᴄʜɪɴɢ...</b></i>',
            reply_to_message_id=message.id
        )
        settings = await get_settings(message.chat.id)
        await msg.message.delete()

    # সার্চ ফলাফল সেভ করা
    key = f"{message.chat.id}-{message.id}"
    FRESH[key] = search
    temp.GETALL[key] = files
    temp.SHORT[message.from_user.id] = message.chat.id

    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{silent_size(file.file_size)}| {extract_tag(file.file_name)} {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", callback_data=f'file#{file.file_id}'
                ),
            ]
            for file in files
        ]
        btn.insert(0, 
            [
                InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0"),
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0"),
                InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0")
            ]
        )
        btn.insert(1, [
            InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}")
            
        ])
    else:
        btn = []
        btn.insert(0, 
            [
                InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0"),
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0"),
                InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0")
            ]
        )
        btn.insert(1, [
            InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}")
            
        ])
    if offset != "":
        req = message.from_user.id if message.from_user else 0
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
                )
            else:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="↭ ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ↭",callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
    remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
    TEMPLATE = script.IMDB_TEMPLATE_TXT
    if imdb:
        cap = TEMPLATE.format(
            qurey=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
        temp.IMDB_CAP[message.from_user.id] = cap
        if not settings["button"]:
            for file_num, file in enumerate(files, start=1):
                cap += f"\n\n<b>{file_num}. <a href='https://telegram.me/{temp.U_NAME}?start=file_{message.chat.id}_{file.file_id}'>{get_size(file.file_size)} | {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}</a></b>"
    else:
        if settings["button"]:
            cap =f"<b>📂 ʜᴇʀᴇ ɪ ꜰᴏᴜɴᴅ ꜰᴏʀ ʏᴏᴜʀ sᴇᴀʀᴄʜ <code>{search}</code></b>\n\n"
        else:
            cap =f"<b>📂 ʜᴇʀᴇ ɪ ꜰᴏᴜɴᴅ ꜰᴏʀ ʏᴏᴜʀ sᴇᴀʀᴄʜ <code>{search}</code></b>\n\n"            
            for file_num, file in enumerate(files, start=1):
                cap += f"<b>{file_num}. <a href='https://telegram.me/{temp.U_NAME}?start=file_{message.chat.id}_{file.file_id}'>{get_size(file.file_size)} | {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}\n\n</a></b>"                
    if imdb and imdb.get('poster'):
        try:
            hehe = await m.edit_photo(photo=imdb.get('poster'), caption=cap, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(DELETE_TIME)
                    await hehe.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(DELETE_TIME)
                await hehe.delete()
                await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg") 
            hmm = await m.edit_photo(photo=poster, caption=cap, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)
            try:
               if settings['auto_delete']:
                    await asyncio.sleep(DELETE_TIME)
                    await hmm.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(DELETE_TIME)
                await hmm.delete()
                await message.delete()
        except Exception as e:
            logger.exception(e)
            fek = await m.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(DELETE_TIME)
                    await fek.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(DELETE_TIME)
                await fek.delete()
                await message.delete()
    else:
        fuk = await m.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        try:
            if settings['auto_delete']:
                await asyncio.sleep(DELETE_TIME)
                await fuk.delete()
                await message.delete()
        except KeyError:
            await save_group_settings(message.chat.id, 'auto_delete', True)
            await asyncio.sleep(DELETE_TIME)
            await fuk.delete()
            await message.delete()

async def ai_spell_check(chat_id, wrong_name):
    async def search_movie(wrong_name):
        search_results = imdb.search_movie(wrong_name)
        movie_list = [movie['title'] for movie in search_results]
        return movie_list
    movie_list = await search_movie(wrong_name)
    if not movie_list:
        return
    for _ in range(5):
        closest_match = process.extractOne(wrong_name, movie_list)
        if not closest_match or closest_match[1] <= 80:
            return 
        movie = closest_match[0]
        files, offset, total_results = await get_search_results(chat_id=chat_id, query=movie)
        if files:
            return movie
        movie_list.remove(movie)

async def advantage_spell_chok(client, message):
    mv_id = message.id
    search = message.text
    chat_id = message.chat.id
    settings = await get_settings(chat_id)

    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", message.text, flags=re.IGNORECASE)
    query = query.strip() + " movie"

    try:
        movies = await get_poster(search, bulk=True)
    except:
        k = await message.reply(script.I_CUDNT.format(message.from_user.mention))
        await asyncio.sleep(60)
        await k.delete()
        return

    if not movies:
        google = search.replace(" ", "+")
        button = [[
            InlineKeyboardButton("🔍 ᴄʜᴇᴄᴋ sᴘᴇʟʟɪɴɢ ᴏɴ ɢᴏᴏɢʟᴇ 🔎", url=f"https://www.google.com/search?q={google}")
        ]]
        k = await message.reply_text(
            text=script.I_CUDNT.format(search),
            reply_markup=InlineKeyboardMarkup(button)
        )
        await asyncio.sleep(30)
        await k.delete()
        return

    user = message.from_user.id if message.from_user else 0
    buttons = [[
        InlineKeyboardButton(text=movie.get('title'), callback_data=f"spol#{movie.movieID}#{user}")
    ] for movie in movies]
    buttons.append([
        InlineKeyboardButton(text="🚫 ᴄʟᴏsᴇ 🚫", callback_data='close_data')
    ])
    d = await message.reply_text(
        text=script.CUDNT_FND.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons),
        reply_to_message_id=message.id
    )
    await asyncio.sleep(10)
    await d.delete()
    

async def manual_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        await save_group_settings(group_id, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(DELETE_TIME)
                                            await joelkb.delete()
                                    except KeyError:
                                        await save_group_settings(group_id, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(DELETE_TIME)
                                            await joelkb.delete()
                            except KeyError:
                                await save_group_settings(group_id, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)

                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        await save_group_settings(group_id, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(DELETE_TIME)
                                            await joelkb.delete()
                                    except KeyError:
                                        await save_group_settings(group_id, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(DELETE_TIME)
                                            await joelkb.delete()
                            except KeyError:
                                await save_group_settings(group_id, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            protect_content=True if settings["file_secure"] else False,
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    await save_group_settings(group_id, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await asyncio.sleep(DELETE_TIME)
                                        await joelkb.delete()
                                except KeyError:                                    
                                    await save_group_settings(group_id, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await asyncio.sleep(DELETE_TIME)
                                        await joelkb.delete()
                        except KeyError:
                            await save_group_settings(group_id, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)

                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    await save_group_settings(group_id, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await asyncio.sleep(DELETE_TIME)
                                        await joelkb.delete()
                                except KeyError:
                                    await save_group_settings(group_id, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await asyncio.sleep(DELETE_TIME)
                                        await joelkb.delete()
                        except KeyError:                            
                            await save_group_settings(group_id, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False

async def global_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            manual = await manual_filters(client, message)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message)
                                        try:
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                        except KeyError:
                                            await save_group_settings(group_id, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings['auto_delete']:
                                                await asyncio.sleep(DELETE_TIME)
                                                await joelkb.delete()
                                        except KeyError:                                          
                                            await save_group_settings(group_id, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await asyncio.sleep(DELETE_TIME)
                                                await joelkb.delete()
                                except KeyError:
                                    await save_group_settings(group_id, 'auto_ffilter', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message) 
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    await save_group_settings(group_id, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            
                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                            manual = await manual_filters(client, message)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message)
                                        try:
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                        except KeyError:                                           
                                            await save_group_settings(group_id, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings['auto_delete']:
                                                await asyncio.sleep(DELETE_TIME)
                                                await joelkb.delete()
                                        except KeyError:                                            
                                            await save_group_settings(group_id, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await asyncio.sleep(DELETE_TIME)
                                                await joelkb.delete()
                                except KeyError:
                                    await save_group_settings(group_id, 'auto_ffilter', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message) 
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    await save_group_settings(group_id, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                        manual = await manual_filters(client, message)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:                                        
                                        await save_group_settings(group_id, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(DELETE_TIME)
                                            await joelkb.delete()
                                    except KeyError:                                        
                                        await save_group_settings(group_id, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(DELETE_TIME)
                                            await joelkb.delete()
                            except KeyError:                                
                                await save_group_settings(group_id, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message) 
                        else:
                            try:
                                if settings['auto_delete']:
                                    await joelkb.delete()
                            except KeyError:                                
                                await save_group_settings(group_id, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await joelkb.delete()

                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        manual = await manual_filters(client, message)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        
                                        await save_group_settings(group_id, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(DELETE_TIME)
                                            await joelkb.delete()
                                    except KeyError:                                        
                                        await save_group_settings(group_id, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(DELETE_TIME)
                                            await joelkb.delete()
                            except KeyError:                                
                                await save_group_settings(group_id, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message) 
                        else:
                            try:
                                if settings['auto_delete']:
                                    await joelkb.delete()
                            except KeyError:
                                await save_group_settings(group_id, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await joelkb.delete()

                                
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False





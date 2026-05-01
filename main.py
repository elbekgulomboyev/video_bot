from aiogram import Bot,Dispatcher
from aiogram.types import Message,BufferedInputFile,InlineKeyboardButton,InlineKeyboardMarkup,CallbackQuery
from aiogram.filters import Command
import os
from asyncio import run
import yt_dlp
TOKEN="8747184855:AAHafNLc6_1emWz6UcX9EG9BGDW_OERLPYM"
DOWNLOAD_MANZIL="downloads"
bot=Bot(token=TOKEN)
dp=Dispatcher()
# sfsdfsdfsdgf
if not os.path.exists(DOWNLOAD_MANZIL):
    os.makedirs(DOWNLOAD_MANZIL)

async def download_video(url:str,download_type:str="video"):
    ydl_opts={
        'outtmpl':os.path.join(DOWNLOAD_MANZIL,'%{title}s.%{ext}s'),
        'quiet':True,
        'no_warnings':True
    }
    if download_type=="audio":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:  # video
        ydl_opts.update({






            
            'format': 'best[height<=720]',  
            'merge_output_format': 'mp4',
        })
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)
            
            if download_type == "audio":
                
                file_name = os.path.splitext(file_name)[0] + '.mp3'
            
            return file_name, info.get('title', 'video'), None
    except Exception as e:
        return None, None, f"Xatolik yuz berdi: {str(e)}"

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        " *Video Yuklab Oluvchi Botga xush kelibsiz*\n\n"
        "Instagram yoki YouTube dan video yoki audio yuklab olish uchun "
        "linkni yuboring.\n\n"
        "Masalan:\n"
        "https://youtube.com/watch?v=...\n"
        "https://instagram.com/reel/...\n\n"
        "⚡️ *Yordam:* /help",
        parse_mode="Markdown"
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        " *Qanday ishlatish?*\n"
        "1. YouTube yoki Instagram linkini yuboring.\n"
        "2. Videoni yoki faqat ovozini yuklashni tanlang.\n\n"
        " *Izoh:* Bot 720p gacha sifatni qo'llab-quvvatlaydi. "
        "Katta fayllar biroz vaqt olishi mumkin."
    )

@dp.message(lambda message: message.text and ("youtube.com" in message.text or "youtu.be" in message.text or "instagram.com" in message.text))
async def handle_link(message: Message):
    url = message.text.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=" Video Yuklash", callback_data=f"video|{url}"),
            InlineKeyboardButton(text=" Audio Yuklash (MP3)", callback_data=f"audio|{url}")
        ]
    ])
    
    await message.answer(
        " *Yuklab olish opsiyasini tanlang:*",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query()
async def process_download(callback: CallbackQuery):
    action, url = callback.data.split("|", 1)
    await callback.message.edit_text(f" Yuklab olinmoqda... Bu bir necha daqiqa olishi mumkin.")
    
    file_path, title, error = await download_video(url, download_type=action)
    
    if error:
        await callback.message.answer(f"xatolikku {error}")
        return
    
    if not file_path or not os.path.exists(file_path):
        await callback.message.answer("Yuklab olishda xatolik yuz berdi")
        return
    
    try:
        if action == "video":
            with open(file_path, 'rb') as video_file:
                await callback.message.answer_video(
                    video=BufferedInputFile(video_file.read(), filename=os.path.basename(file_path)),
                    caption=f"zur *{title}*",
                    parse_mode="Markdown"
                )
        else:  
            with open(file_path, 'rb') as audio_file:
                await callback.message.answer_audio(
                    audio=BufferedInputFile(audio_file.read(), filename=os.path.basename(file_path)),
                    title=title,
                    performer="Downloader Bot"
                )
        
        await callback.message.delete()
        
    except Exception as e:
        await callback.message.answer(f"Faylni yuborishda xatolik: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    run(main())
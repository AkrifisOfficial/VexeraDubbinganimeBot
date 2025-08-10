from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.keyboards import create_anime_keyboard, create_episodes_keyboard

def register_handlers(dp, db):
    # Регистрация обработчиков
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(search_command, commands=['search'])
    dp.register_callback_query_handler(show_anime_details, lambda c: c.data.startswith('anime_'))
    dp.register_callback_query_handler(show_episode, lambda c: c.data.startswith('ep_'))

async def start_command(message: types.Message):
    await message.answer(
        "🍥 Привет! Я бот для просмотра аниме с озвучкой от VexeraDubbing.\n\n"
        "🔍 Чтобы найти аниме, используй команду: /search <название>\n"
        "👨‍💻 Админ: @ваш_ник"
    )

async def search_command(message: types.Message):
    query = message.get_args().strip()
    if not query:
        await message.answer("❌ Пожалуйста, укажи название аниме после команды\nПример: /search Наруто")
        return
    
    if len(query) < 3:
        await message.answer("🔎 Запрос должен содержать минимум 3 символа")
        return
    
    results = db.search_anime(query)
    
    if not results:
        await message.answer("😢 Ничего не найдено. Попробуй другой запрос")
        return
    
    for anime in results[:5]:  # Ограничим 5 результатами
        keyboard = create_anime_keyboard(anime['id'])
        caption = f"🎬 <b>{anime['title']}</b>\n🔊 Озвучка: {anime['voiceover']}"
        
        if anime.get('poster_url'):
            await message.answer_photo(
                anime['poster_url'],
                caption=caption,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await message.answer(
                caption,
                reply_markup=keyboard,
                parse_mode="HTML"
            )

async def show_anime_details(callback_query: types.CallbackQuery):
    anime_id = int(callback_query.data.split('_')[1])
    anime = db.get_anime_by_id(anime_id)
    
    if not anime:
        await callback_query.answer("❌ Аниме не найдено")
        return
    
    episodes = db.get_episodes(anime_id)
    
    if not episodes:
        await callback_query.answer("😢 Нет доступных серий")
        return
    
    message_text = (
        f"🎬 <b>{anime['title']}</b>\n\n"
        f"📝 <i>{anime['description'][:250]}...</i>\n\n"
        f"🔊 Озвучка: {anime['voiceover']}\n"
        f"📺 Доступные серии:"
    )
    
    keyboard = create_episodes_keyboard(anime_id, episodes)
    
    if anime.get('poster_url'):
        await callback_query.message.answer_photo(
            anime['poster_url'],
            caption=message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback_query.message.answer(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    await callback_query.answer()

async def show_episode(callback_query: types.CallbackQuery):
    _, anime_id, episode_number = callback_query.data.split('_')
    anime_id = int(anime_id)
    episode_number = int(episode_number)
    
    episode_url = db.get_episode_url(anime_id, episode_number)
    
    if not episode_url:
        await callback_query.answer("❌ Серия не найдена")
        return
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
        "▶️ Смотреть в VK", 
        url=episode_url
    ))
    
    await callback_query.message.answer(
        f"🎥 Серия {episode_number} готова к просмотру!\n"
        "📱 Видео откроется в приложении VK",
        reply_markup=keyboard
    )
    
    await callback_query.answer()

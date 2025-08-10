from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_anime_keyboard(anime_id: int):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("📋 Подробнее", callback_data=f"anime_{anime_id}")
    )

def create_episodes_keyboard(anime_id: int, episodes: list):
    keyboard = InlineKeyboardMarkup(row_width=5)
    for ep in episodes:
        keyboard.insert(InlineKeyboardButton(
            f"{ep['episode_number']}",
            callback_data=f"ep_{anime_id}_{ep['episode_number']}"
        ))
    return keyboard

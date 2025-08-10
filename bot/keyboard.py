from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_anime_keyboard(anime_id: int):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        "📋 Подробнее и список серий",
        callback_data=f"anime_{anime_id}"
    ))
    return keyboard

def create_episodes_keyboard(anime_id: int, episodes: list):
    keyboard = InlineKeyboardMarkup(row_width=5)
    
    # Группируем серии по 5 в ряд
    buttons = []
    for ep in episodes:
        buttons.append(InlineKeyboardButton(
            f"{ep['episode_number']}",
            callback_data=f"ep_{anime_id}_{ep['episode_number']}"
        ))
    
    # Добавляем кнопки рядами по 5
    for i in range(0, len(buttons), 5):
        keyboard.row(*buttons[i:i+5])
    
    return keyboard

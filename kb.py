from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from text import text_templates

"""
Using keyboards
"""


"""
start keyboard with options
"""
START_INSTRUCTIONS = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text=text_templates["OPTIONS"]["PHOTO_REQUIREMENTS_QUESTION"]
            ),
            KeyboardButton(text=text_templates["OPTIONS"]["IMPORTANT_QUESTION"]),
        ],
        [
            KeyboardButton(text=text_templates["OPTIONS"]["MUSHROOMS_BASE_QUESTION"]),
            KeyboardButton(text=text_templates["OPTIONS"]["ABOUT_PROJECT_QUESTION"]),
        ],
    ],
    input_field_placeholder=text_templates["SELECT_OPTIONS_BELOW"],
)

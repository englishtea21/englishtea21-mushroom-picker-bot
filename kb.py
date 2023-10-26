from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import text

"""
Using keyboards
"""


"""
start keyboard with options
"""

LANGUAGE_SELECTION = None

START_INSTRUCTIONS = None


def update_keyboards():
    global LANGUAGE_SELECTION
    LANGUAGE_SELECTION = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=language_name)
                for language_name in sorted(text.languages_dict.keys())
            ]
        ],
        resize_keyboard=True,
    )

    global START_INSTRUCTIONS
    START_INSTRUCTIONS = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=text.text_templates["OPTIONS"]["PHOTO_REQUIREMENTS_QUESTION"]
                ),
                KeyboardButton(
                    text=text.text_templates["OPTIONS"]["IMPORTANT_QUESTION"]
                ),
            ],
            [
                KeyboardButton(
                    text=text.text_templates["OPTIONS"]["MUSHROOMS_BASE_QUESTION"]
                ),
                KeyboardButton(
                    text=text.text_templates["OPTIONS"]["ABOUT_PROJECT_QUESTION"]
                ),
            ],
            [KeyboardButton(text=text.text_templates["OPTIONS"]["CHANGE_LANGUAGE"])],
        ],
        input_field_placeholder=text.text_templates["SELECT_OPTIONS_BELOW"],
    )


if LANGUAGE_SELECTION is None or START_INSTRUCTIONS is None:
    update_keyboards()

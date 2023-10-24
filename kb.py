from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import text

'''
Using keyboards
'''


'''
start keyboard with options
'''
START_INSTRUCTIONS = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=text.PHOTO_REQUIREMENTS_QUESTION)],
        [KeyboardButton(text=text.IMPORTANT_QUESTION)],
        [KeyboardButton(text=text.MUSHROOMS_BASE_QUESTION)],
        [KeyboardButton(text=text.ABOUT_PROJECT_QUESTION)],
    ],
    input_field_placeholder=text.SELECT_OPTIONS_BELOW,
)

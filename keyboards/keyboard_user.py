from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import logging


def keyboard_company() -> InlineKeyboardMarkup:
    logging.info("keyboard_registration")
    button_1 = InlineKeyboardButton(text='Строительная компания', callback_data=f'company_1')
    button_2 = InlineKeyboardButton(text='Дизайнерская студия', callback_data=f'company_2')
    button_3 = InlineKeyboardButton(text='Частное лицо', callback_data=f'company_3')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]],)
    return keyboard


def keyboard_KP() -> InlineKeyboardMarkup:
    logging.info("keyboard_registration")
    button_1 = InlineKeyboardButton(text='Да', callback_data=f'KP_Да')
    button_2 = InlineKeyboardButton(text='Нет', callback_data=f'KP_Нет')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard


def keyboards_get_contact() -> ReplyKeyboardMarkup:
    logging.info("keyboards_get_contact")
    button_1 = KeyboardButton(text='Отправить свой контакт ☎️',
                              request_contact=True)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1]],
        resize_keyboard=True
    )
    return keyboard

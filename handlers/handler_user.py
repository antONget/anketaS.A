from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state

from config_data.config import Config, load_config
import database.requests as rq
import keyboards.keyboard_user as kb
from filter.filter import validate_russian_phone_number
from services.googlesheets import append_row
import logging


router = Router()
config: Config = load_config()


class Stage(StatesGroup):
    name = State()
    phone = State()


@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Запуск бота - нажата кнопка "Начать" или введена команда "/start"
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f"process_start_command {message.chat.id}")
    await state.set_state(default_state)
    data = {"tg_id": message.chat.id, "username": message.from_user.username}
    await rq.add_user(tg_id=message.chat.id, data=data)
    await message.answer_photo(photo='AgACAgIAAxkBAAMnZuGrqFwdnbXv5wNqo8esoK1NzWUAAgjgMRuqRwlL1VbVH3yUyQsBAAMCAAN4AAM2BA',
                               caption=f'Уже 11 лет наши склады снабжают строительные объекты  по всей России.\n'
                                       f'Наши клиенты:\n'
                                       f'Правительство Москвы, РЖД, РосАтом, архитектурное бюро Zaha Hadid,'
                                       f' Земсков, строительные рынки, строительные и дизайнерские компании.')
    await message.answer(text='Кем Вы являетесь?',
                         reply_markup=kb.keyboard_company())


@router.callback_query(F.data.startswith('company'))
async def select_company(callback: CallbackQuery, state: FSMContext):
    """
    Выбор типа компании
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f"select_company {callback.message.chat.id}")
    company_dict = {'1': 'Строительная компания', '2': 'Дизайнерская студия', '3': 'Частное лицо'}
    await state.update_data(company=company_dict[callback.data.split('_')[1]])
    await callback.message.edit_text(text=f'Хотели бы Вы получить индивидуальное КП?',
                                     reply_markup=kb.keyboard_KP())
    await callback.answer()


@router.callback_query(F.data.startswith('KP'))
async def select_KP(callback: CallbackQuery, state: FSMContext):
    """
    Получение коммерческих предложений
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'select_KP {callback.message.chat.id}')
    answer = callback.data.split('_')[1]
    await state.update_data(kp=answer)
    await callback.message.edit_text(text=f'Укажите как вас зовут:',
                                     reply_markup=None)
    await state.set_state(Stage.name)
    await callback.answer()


@router.message(F.text, Stage.name)
async def anketa_get_username(message: Message, state: FSMContext):
    """
    Получаем имя пользователя. Запрашиваем номер телефона
    :param message:
    :param state:
    :return:
    """
    logging.info(f'anketa_get_username: {message.from_user.id}')
    name = message.text
    await state.update_data(name=name)
    await message.answer(text=f'Рад вас приветствовать {name}. Поделитесь вашим номером телефона ☎️',
                         reply_markup=kb.keyboards_get_contact())
    await state.set_state(Stage.phone)


@router.message(or_f(F.text, F.contact), StateFilter(Stage.phone))
async def process_validate_russian_phone_number(message: Message, state: FSMContext, bot: Bot) -> None:
    """Получаем номер телефона пользователя (проводим его валидацию). Подтверждаем введенные данные"""
    logging.info("process_start_command_user")
    if message.contact:
        phone = str(message.contact.phone_number)
    else:
        phone = message.text
        if not validate_russian_phone_number(phone):
            await message.answer(text="Неверный формат номера. Повторите ввод, например 89991112222:")
            return
    await state.update_data(phone=phone)
    await state.set_state(default_state)
    data = await state.get_data()
    for admin in config.tg_bot.admin_ids.split(','):
        try:
            await bot.send_message(chat_id=admin,
                                   text=f'Пользователь @{message.from_user.username} оставил анкетные данные:\n\n'
                                        f'<b>Компания</b>: {data.get("company", "none")}\n'
                                        f'<b>Согласны получать КП</b>: {data.get("kp", "none")}\n'
                                        f'<b>Имя</b>: {data.get("name", "none")}\n'
                                        f'<b>Телефон</b>: {data.get("phone", "none")}')
        except:
            pass
    await append_row(order=[message.from_user.username, data.get("company", "none"), data.get("kp", "none"),
                            data.get("name", "none"), data.get("phone", "none")])
    await message.answer(text=f'Спасибо за обращение!\n'
                              f'Мы с Вами свяжемся в ближайшее время',
                         reply_markup=ReplyKeyboardRemove())

import asyncio

from aiogram import Bot, types
from aiogram.enums import ParseMode

import packages.backend.apps.tg_bot.repository as repository
import packages.backend.apps.tg_bot.service as service

from packages.backend.apps.tg_bot.custom_types import ChatState
from packages.backend.libs.email_sender import send_email


main_page_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='💡 Контрагенты'),
            types.KeyboardButton(text='🏞 Отправка Письма'),
        ],
    ],
    resize_keyboard=True,
)

contragents_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='➕ Добавить агента'),
            types.KeyboardButton(text='🗑 Удалить агента'),
        ],
        [
            types.KeyboardButton(text='🏘 Главное меню'),
            types.KeyboardButton(text='🪪 Список агентов'),
        ],
    ],
    one_time_keyboard=True,
    resize_keyboard=True,
)


confirm_email_send_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Да", callback_data="confirm_send_email"),
            types.InlineKeyboardButton(text="Отмена", callback_data="cancel_send_email")
        ]
    ])

send_email_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='🏘 Главное меню'),
        ],
    ],
    input_field_placeholder='Прикрепите изображение',
    one_time_keyboard=True,
    resize_keyboard=True,
)


async def go_to_main_page(bot: Bot, message: types.Message, chat_id: str):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(
        text=(
            '🚀 VOYAGER AI🚀:\n\n Твой Универсальный Цифровой Ассистент\n\n'
            'Добро пожаловать в будущее коммуникаций и продуктивности!\n\n'
            'Давай творить будущее вместе! 🌟\n\n'
            '🏠 Главное меню \n\nВыберите нужный раздел 👇'
        ),
        reply_markup=main_page_keyboard,
    )
    await repository.update_chat_state(chat_id=chat_id, chat_state=ChatState.main_page)


async def go_to_contragents_screen(bot: Bot, message: types.Message, chat_id: str):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(
        text=(
            f'🔥 Вы в режиме работы с контрагентами\n\n'
            f'Выберите желаемое действие 👇\n\n'
        ),
        reply_markup=contragents_keyboard,
        parse_mode=ParseMode.HTML,
    )
    await repository.update_chat_state(chat_id=chat_id, chat_state=ChatState.contragents)


async def go_to_send_email_screen(bot: Bot, message: types.Message, chat_id: str):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(
        text=(
            f'🔥 Раздел отправки изображений.\n\n'
            f'Отправьте мне изображение для отправки по email\n\n'

        ),
        reply_markup=send_email_keyboard,
        parse_mode=ParseMode.HTML,
    )
    await repository.update_chat_state(chat_id=chat_id, chat_state=ChatState.send_email)


async def confirm_send(bot, message, chat_id):
    if message.photo:
        file_id = message.photo[-1].file_id
        filename = "photo.jpg"
    elif message.document:
        file_id = message.document.file_id
        filename = message.document.file_name
    else:
        await message.answer("❌ Файл не найден. Пожалуйста, отправьте фото или документ.")
        return
    service.save_pending_file(chat_id, file_id, filename)

    await message.answer(
        text="Вы уверены, что хотите отправить этот файл по email?",
        reply_markup=confirm_email_send_keyboard
    )
    return


async def send_photo_emails(bot, chat_id, call):
    pending_data = service.get_pending_file(chat_id)
    if not pending_data:
        await call.answer("Файл не найден или время ожидания истекло. Попробуйте заново.", show_alert=True)
        return False

    file_id = pending_data['file_id']
    filename = pending_data['filename']

    file = await bot.download(file_id)
    file_bytes = file.read()

    contragents = await repository.get_all_contragents_emails()
    if not contragents:
        await call.message.answer('❌ Нет контрагентов для отправки.')
        await repository.update_chat_state(chat_id, ChatState.main_page)
        return False

    tasks = []
    for contragent_email in contragents:
        task = asyncio.create_task(
            send_email(
                to_email=contragent_email,
                subject="📎 Файл для вас",
                body="Здравствуйте! Высылаем вам запрошенный файл.",
                attachment=file_bytes,
                filename=filename
            )
        )
        tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)

    await repository.update_chat_state(chat_id, ChatState.main_page)
    await call.message.answer(
        text='✅ Файл успешно отправлен всем контрагентам по email.\n🏘 Возвращаемся в главное меню.',
        reply_markup=main_page_keyboard,
    )
    service.delete_pending_file(chat_id)
    await call.answer("Файл отправлен!")
    return True


async def confirm_agent_input(message: types.Message, chat_id: int, email_text: str) -> None:
    pending_data = service.get_pending_agent(chat_id)
    if not pending_data:
        await message.answer("Что-то пошло не так. Попробуйте ещё раз.")
        return

    pending_data["email"] = email_text
    service.save_pending_agent(chat_id, pending_data)

    confirm_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Да", callback_data="confirm_add_agent"),
            types.InlineKeyboardButton(text="Отмена", callback_data="cancel_add_agent")
        ]
    ])

    await message.answer(
        text=f"Подтвердите добавление агента:\nИмя: {pending_data['name']}\nEmail: {pending_data['email']}",
        reply_markup=confirm_keyboard
    )


async def confirm_agent_deletion(message: types.Message, chat_id: int, username_text: str) -> None:
    pending_data = {"username": username_text}
    service.save_pending_deletion(chat_id, pending_data)

    agent = await repository.get_agent_by_username(username_text)
    if not agent:
        await message.answer("Агент с таким username не найден. Попробуйте ещё раз.")
        service.delete_pending_deletion(chat_id)
        return

    pending_data["agent"] = agent
    service.save_pending_deletion(chat_id, pending_data)

    confirm_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Да", callback_data="confirm_delete_agent"),
            types.InlineKeyboardButton(text="Отмена", callback_data="cancel_delete_agent")
        ]
    ])

    await message.answer(
        text=f"Подтвердите удаление агента:\nИМЯ: {agent['username']}\nEMAIL: {agent['email']}",
        reply_markup=confirm_keyboard
    )


async def show_agent_list(message: types.Message):
    agents = await repository.get_all_agents()

    if not agents:
        await message.answer("Список агентов пуст.")
        return

    response_text = "🪪 Список агентов:\n\n"
    for agent in agents:
        response_text += f"👤 {agent['username']} --- {agent['email']}\n"

    await message.answer(text=response_text,
                         reply_markup=contragents_keyboard)
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command

import packages.backend.apps.tg_bot.message_fn as fn
import packages.backend.apps.tg_bot.repository as repository
import packages.backend.apps.tg_bot.service as service

from packages.backend.apps.tg_bot.custom_types import ChatState
from packages.backend.libs.config.tg_config import tg_config
from packages.backend.libs.database.db_instance import db


bot = Bot(tg_config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()
password = tg_config.password


@dp.message(Command('start'))
async def command_start_handler(message: types.Message) -> None:
    chat_state = ChatState.enter_password
    await repository.init_tg_chat(
            chat=message.chat,
            user=message.from_user,
            chat_state=chat_state,
        )
    await message.answer(
            text=(
                '🔑 <b>Добро пожаловать!</b>\n'
                'Пожалуйста, введите пароль для доступа к главному меню:'
            ),
            parse_mode=ParseMode.HTML
        )


@dp.callback_query()
async def callback_query_handler(call: types.CallbackQuery):
    chat = await repository.get_chat_by_remote_id(call.message.chat.id)
    if not chat:
        await call.message.answer('Чтобы воспользоваться данными кнопками, перезапустите бота: "/start".')
        return

    chat_id = chat.get('id', None)
    chat_state = chat.get('state', None)

    if chat_state == ChatState.send_email:
        if call.data == 'confirm_send_email':
            await bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None
            )
            await fn.send_photo_emails(bot, chat_id, call)
        elif call.data == "cancel_send_email":
            service.delete_pending_photo(chat_id)
            await bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Отправка фото отменена.\n"
                     "Пожалуйста, отправьте изображение заново, чтобы отправить по email."
            )
            await call.answer("Отмена")

    if chat_state == ChatState.add_agent_email:
        if call.data == "confirm_add_agent":
            pending_data = service.get_pending_agent(chat_id)
            if not pending_data:
                await call.answer("Временные данные не найдены, попробуйте заново.", show_alert=True)
                return

            await repository.add_contragent(name=pending_data["name"], email=pending_data["email"])

            service.delete_pending_agent(chat_id)

            await repository.update_chat_state(chat_id, ChatState.contragents)

            await bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None
            )
            await call.message.answer("Агент успешно добавлен!", reply_markup=fn.contragents_keyboard)
            await call.answer("Добавлено!")

        elif call.data == "cancel_add_agent":
            service.delete_pending_agent(chat_id)
            await repository.update_chat_state(chat_id, ChatState.contragents)

            await bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None
            )
            await call.message.answer("Добавление агента отменено.", reply_markup=fn.contragents_keyboard)
            await call.answer("Отмена")
        return
    if chat_state == ChatState.delete_agent:
        if call.data == "confirm_delete_agent":
            pending_data = service.get_pending_deletion(chat_id)
            if not pending_data or "agent" not in pending_data:
                await call.answer("Временные данные не найдены, попробуйте ещё раз.", show_alert=True)
                return

            agent = pending_data["agent"]
            await repository.delete_agent_by_username(agent["username"])

            service.delete_pending_deletion(chat_id)
            await repository.update_chat_state(chat_id, ChatState.contragents)

            await bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None
            )
            await call.message.answer("Агент успешно удалён!", reply_markup=fn.contragents_keyboard)
            await call.answer("Удалено!")

        elif call.data == "cancel_delete_agent":
            service.delete_pending_deletion(chat_id)
            await repository.update_chat_state(chat_id, ChatState.contragents)

            await bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None
            )
            await call.message.answer("Удаление агента отменено.", reply_markup=fn.contragents_keyboard)
            await call.answer("Отмена")
    return



@dp.message()
async def message_handler(message: types.Message) -> None:
    try:
        chat = await repository.get_chat_by_remote_id(message.chat.id)
        if not chat:
            await message.answer('Упс! Начни, пожалуйста, заново "/start". Мы кое что обновили')
            return

        if message.text is None and not message.photo:
            await message.answer('На данный момент можно отправлять только текстовые сообщения...)')
            return

        chat_id = chat['id']
        chat_state = chat['state']
        message_text = message.text.strip() if message.text else ''

        # ----- Handle main page menu buttons -----

        if message_text == password and chat_state == ChatState.enter_password:
            await fn.go_to_main_page(bot, message, chat_id=chat_id)
            return

        if message_text == '🏘 Главное меню':
            await fn.go_to_main_page(bot, message, chat_id=chat_id)
            return

        if message_text == '🏞 Отправка Письма' and chat_state == ChatState.main_page:
            await fn.go_to_send_email_screen(bot, message, chat_id=chat_id)
            return

        if message_text == '💡 Контрагенты' and chat_state == ChatState.main_page:
            await fn.go_to_contragents_screen(bot, message, chat_id=chat_id)
            return

        if chat_state == ChatState.main_page:
            await message.answer(
                text='🤷‍♂️ Неизвестная команда. \nВыберите, пожалуйста, в меню нужный пункт 👇',
                reply_markup=fn.main_page_keyboard,
            )
            return


        # ----- Handle Image send to contragents -----

        if chat_state == ChatState.send_email:
            if not message.photo:
                await message.answer('❌ Это не фото. Пожалуйста, отправьте изображение для отправки по email.')
                return

            await fn.confirm_send(bot, message, chat_id)
            return

        if message.text is None:
            await message.answer('На данный момент можно отправлять только текстовые сообщения.')
            return

        # ----- Handle communication with contragents -----

        if chat_state == ChatState.contragents:
            if message_text == "➕ Добавить агента":
                await repository.update_chat_state(chat_id, ChatState.add_agent_name)
                await message.answer("Введите имя нового агента:")
                return
            elif message_text == "🗑 Удалить агента":
                await repository.update_chat_state(chat_id, ChatState.delete_agent)
                await message.answer("Введите имя агента, которого нужно удалить:")
                return

        if chat_state == ChatState.add_agent_name:
            pending_data = {"name": message_text}
            service.save_pending_agent(chat_id, pending_data)
            await repository.update_chat_state(chat_id, ChatState.add_agent_email)
            await message.answer("Введите email нового агента:")
            return

        if chat_state == ChatState.add_agent_email:
            await fn.confirm_agent_input(message, chat_id, message_text)
            return

        if chat_state == ChatState.delete_agent:
            await fn.confirm_agent_deletion(message, chat_id, message_text)
            return

    except Exception as e:
        print('[tg_bot][message_handler] error:', e)
        await message.answer('Упс! У меня ошибка... Наши разработчики уже работают над решением проблемы')


async def main() -> None:
    await db.connect()
    await dp.start_polling(bot)
    await db.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

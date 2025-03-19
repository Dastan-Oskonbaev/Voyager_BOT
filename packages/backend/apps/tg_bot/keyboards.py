from aiogram import types

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
            types.KeyboardButton(text='🖊 Отредактировать агента'),
            types.KeyboardButton(text='🪪 Список агентов'),
        ],
        [
            types.KeyboardButton(text='➕ Добавить получателя для тестового письма'),
            types.KeyboardButton(text='🗑 Удалить получателя для тестового письма'),
        ],
        [
            types.KeyboardButton(text='🪪 Список получателей тестового письма'),
            types.KeyboardButton(text='🏘 Главное меню'),
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
            types.KeyboardButton(text='⚙️ Изменить Заголовок письма'),
            types.KeyboardButton(text='🛠 Изменить Текст письма'),
        ],
        [
            types.KeyboardButton(text='🕹 Тестовое письмо'),
            types.KeyboardButton(text='💌 Просмотреть Заголовок и Текст письма')
        ],
        [
            types.KeyboardButton(text='🏘 Главное меню')
        ]
    ],
    input_field_placeholder='Прикрепите файл или изображение',
    one_time_keyboard=True,
    resize_keyboard=True,
)

confirm_delete_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
    [
        types.InlineKeyboardButton(text="Да", callback_data="confirm_delete_agent"),
        types.InlineKeyboardButton(text="Отмена", callback_data="cancel_delete_agent")
    ]
])

confirm_add_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
    [
        types.InlineKeyboardButton(text="Да", callback_data="confirm_add_agent"),
        types.InlineKeyboardButton(text="Отмена", callback_data="cancel_add_agent")
    ]
])


redact_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
    [
        types.InlineKeyboardButton(text="ФИО", callback_data="customer_username"),
        types.InlineKeyboardButton(text="Email", callback_data="customer_email"),
        types.InlineKeyboardButton(text="Отмена", callback_data="cancel_redact_agent")
    ]
])



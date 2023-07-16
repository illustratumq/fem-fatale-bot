from aiogram import Dispatcher
from aiogram.types import Message

from app.keyboards.reply.menu import basic_kb, Buttons


async def info_select_cmd(msg: Message):
    await msg.answer(
        'Дізнайся про нас більше! Обери, що тебе цікавить',
        reply_markup=basic_kb([
             [Buttons.menu.rules, Buttons.menu.how_it_work],
             [Buttons.menu.about_us],
             [Buttons.menu.back]
         ])
    )


async def info_how_it_works_cmd(msg: Message):
    text = (
        '<b>Зроби 3 прості кроки та отримуй гроші!</b>\n\n'
        '1️⃣ Назви номер карти Femme Fatale в самому закладі або зроби попереднє бронювання\n'
        '2️⃣ Повідом нас про відвідування закладу\n'
        '3️⃣ Замов обмін нарахованих балів на гроші, вказавши реквізити банківської карти\n\n'
        '<b>Гроші отримаєш протягом 30 хвилин - все працює дуже швидко!</b>\n'
        'Для отримання додаткової інформації про сервіс Femme Fatale, '
        'ознайомся з розділом “<b>Правила роботи сервісу</b>”!'
        '<b>Є запитання? Будь ласка, телефонуй або пиши на нашу службу підтримки!</b>'
        '☎  380633941971'
        'Telegram - @FFcashback'
    )
    await msg.answer(text, reply_markup=basic_kb([[Buttons.menu.help], [Buttons.back.info]]))


async def info_about_us_cmd(msg: Message):
    text = (
        '<b>Проєкт Femme Fatale – перший кешбек-сервіс в Україні, який надає можливість '
        'кожній дівчині отримувати гроші за відвідування та рекомендації найпрестижніших закладів нашої країни!</b>\n\n'
        'Тільки для вас, дорогі наші жінки та дівчата, ми об’єднали в єдину мережу ресторани, готелі, '
        'Спа-комплекси та інші напрямки преміум сегменту, виплачуючи гроші за кожен чек у цих закладах!\n\n'
        'Попереду на вас чекає багато цікавого – розширення мережі ресторанів, магазинів, '
        'партнерських компаній, які надають послуги VIP-рівня, а також, '
        'неповторні акції, бонуси та подарунки від нашого сервісу!\n\n'
        'Ми цінуємо кожну з вас та робимо все, щоб ви не тільки проводили час із задоволенням, '
        'але й отримували за це гроші!\n\n'
        'З повагою та любов’ю, команда сервісу Femme Fatale! ❤️'
    )
    await msg.answer(text, reply_markup=basic_kb([[Buttons.menu.help], [Buttons.back.info]]))


async def info_rules_cmd(msg: Message):
    text = (
        'Цей розділ ще в розробці... :)'
    )
    await msg.answer(text, reply_markup=basic_kb([[Buttons.menu.help], [Buttons.back.info]]))


async def info_developer_cmd(msg: Message):
    text = (
        'Цей бот був розроблений @engineer_spock 😎'
    )
    await msg.answer(text, reply_markup=basic_kb([Buttons.back.info]))


def setup(dp: Dispatcher):
    dp.register_message_handler(info_select_cmd, text=(Buttons.menu.about, Buttons.back.info), state='*')
    dp.register_message_handler(info_how_it_works_cmd, text=Buttons.menu.how_it_work, state='*')
    dp.register_message_handler(info_about_us_cmd, text=Buttons.menu.about_us, state='*')
    # dp.register_message_handler(info_developer_cmd, text=Buttons.menu.about_bot, state='*')
    dp.register_message_handler(info_rules_cmd, text=Buttons.menu.rules, state='*')
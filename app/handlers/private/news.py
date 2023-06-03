from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, MediaGroup, InputMediaPhoto

from app.database.services.enums import UserRoleEnum, ArticleStatusEnum
from app.database.services.repos import ArticleRepo, MediaRepo, UserRepo
from app.keyboards import Buttons
from app.keyboards.reply.menu import basic_kb


async def pre_paginate_news_cmd(msg: Message, article_db: ArticleRepo, media_db: MediaRepo, user_db: UserRepo,
                                state: FSMContext):
    await state.update_data(page=0)
    await paginate_news_cmd(msg, article_db, media_db, user_db, state)


async def paginate_news_cmd(msg: Message, article_db: ArticleRepo, media_db: MediaRepo, user_db: UserRepo,
                            state: FSMContext):
    data = await state.get_data()
    page = data['page']
    user = await user_db.get_user(msg.from_user.id)

    status = ArticleStatusEnum.ACTIVE
    buttons = [
        [Buttons.articles.prev, Buttons.articles.next], [Buttons.back.menu]
    ]
    if user.role == UserRoleEnum.ADMIN:
        buttons.insert(0, [Buttons.articles.publish])
        status = '*'

    articles = await article_db.get_article_status(status)

    if not articles:
        await msg.answer('Згодом тут будуть цікаві акції та новини!')
        return

    if msg.text == Buttons.articles.next:
        if len(articles) > 2:
            page = (page + 1) % len(articles)
        else:
            await msg.answer('Поки що є тільки одна новина')
            return
    elif msg.text == Buttons.articles.prev:
        if len(articles) > 2:
            page = (page - 1) % len(articles)
        else:
            await msg.answer('Поки що є тільки одна новина')
            return

    article: ArticleRepo.model = articles[page]
    text = f'{article.title}\n\n{article.description}'
    reply_markup = basic_kb(buttons)

    await state.update_data(page=page)
    await state.set_state(state='news')
    if article.media_id:
        media = await media_db.get_media(article.media_id)
        if len(media.files) > 1:
            data = dict(caption=text)
            await msg.answer('.', reply_markup=reply_markup)
            group = MediaGroup([InputMediaPhoto(file, **(data if media.files[-1] == file else {})) for file in media.files])
            await msg.answer_media_group(group)
        else:
            await msg.answer_photo(media.files[0], caption=text, reply_markup=reply_markup)
    else:
        await msg.answer(text, reply_markup=reply_markup)


def setup(dp: Dispatcher):
    dp.register_message_handler(pre_paginate_news_cmd, text=Buttons.menu.news, state='*')
    dp.register_message_handler(paginate_news_cmd, state='news')


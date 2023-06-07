from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, MediaGroup, InputMediaPhoto

from app.database.services.enums import UserRoleEnum, ArticleStatusEnum, UserStatusEnum
from app.database.services.repos import ArticleRepo, MediaRepo, UserRepo
from app.filters import IsAdminFilter
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
        if len(articles) > 1:
            page = (page + 1) % len(articles)
        else:
            await msg.answer('Поки що є тільки одна новина')
            return
    elif msg.text == Buttons.articles.prev:
        if len(articles) > 1:
            page = (page - 1) % len(articles)
        else:
            await msg.answer('Поки що є тільки одна новина')
            return

    article: ArticleRepo.model = articles[page]
    if article.title and article.description:
        text = f'{article.title}\n\n{article.description}'
    else:
        text = article.description
    reply_markup = basic_kb(buttons)

    await state.update_data(page=page, article_id=article.id)
    await state.set_state(state='news')
    if article.media_id:
        media = await media_db.get_media(article.media_id)
        if media.is_media_group():
            await msg.answer(f'Стаття {articles.index(article) + 1} з {len(articles)}', reply_markup=reply_markup)
            await msg.answer_media_group(media.get_media_group(text))
        else:
            await msg.answer_photo(media.files[0], caption=text, reply_markup=reply_markup)
    else:
        await msg.answer(text, reply_markup=reply_markup)


async def send_to_all_confirm(msg: Message, state: FSMContext):
    await msg.answer('Підтвредіть, що бажаєте опублікувати цю новину',
                     reply_markup=basic_kb([[Buttons.articles.publish], [Buttons.menu.back]]))
    await state.set_state(state='confirm_publish')


async def send_to_all(msg: Message, article_db: ArticleRepo, media_db: MediaRepo, user_db: UserRepo,
                      state: FSMContext):
    data = await state.get_data()
    article = await article_db.get_article(data['article_id'])

    if article.title and article.description:
        text = f'{article.title}\n\n{article.description}'
    else:
        text = article.description

    if article.media_id:
        media = await media_db.get_media(article.media_id)
        if len(media.files) > 1:
            data = dict(caption=text)
            group = MediaGroup([InputMediaPhoto(file, **(data if media.files[-1] == file else {})) for file in media.files])
            func = msg.bot.send_media_group
            kwargs = dict(media=group)
        else:
            func = msg.bot.send_photo
            kwargs = dict(photo=media.files[0], caption=text)
    else:
        func = msg.bot.send_message
        kwargs = dict(text=text)

    active = 0
    inactive = 0
    for user in await user_db.get_user_status(UserStatusEnum.ACTIVE):
        try:
            await func(**kwargs, chat_id=user.user_id)
            active += 1
        except:
            await user_db.update_user(user.user_id, status=UserStatusEnum.INACTIVE)
            inactive += 1
    await msg.answer(f'Новина була успішно опублікована. '
                     f'Отримали повідомлення {active} користувачів. Заблокували бота {inactive}.',
                     reply_markup=basic_kb([Buttons.menu.back]))


def setup(dp: Dispatcher):
    dp.register_message_handler(pre_paginate_news_cmd, text=Buttons.menu.news, state='*')
    dp.register_message_handler(send_to_all_confirm, IsAdminFilter(), state='news', text=Buttons.articles.publish)
    dp.register_message_handler(send_to_all, IsAdminFilter(), state='confirm_publish', text=Buttons.articles.publish)
    dp.register_message_handler(paginate_news_cmd, state='news', text=(Buttons.articles.next, Buttons.articles.prev))



class Back:
    categories: str = 'В категорії'
    partners: str = '◀ До партнерів'
    card: str = 'Повернутись до карти'
    menu: str = 'В головне меню'
    media: str = '◀ Назад в медіа'
    info: str = '◀ До інформації'


class Partners:
    next: str = '▶'
    prev: str = '◀'


class Articles:
    publish: str = 'Опублікувати 📬'
    next: str = 'Наступна ▶'
    prev: str = '◀ Попередня'


class History:
    next: str = 'Наступний ▶'
    prev: str = '◀ Попередній'


class Admin:
    #  panel
    cancel_chat: str = 'Завершити діалог 💬'
    database: str = 'База даних 📗'
    media: str = 'Медіа 🌠'
    database_clients: str = 'Клієнти 👥'
    database_partners: str = 'Партнери 🌉'
    search: str = 'Знайти клієнта 🔍'
    create_payout_panel: str = 'Створити платіж'
    create_chat_panel: str = 'Створити чат з клієнтом'

    #  events
    make_done: str = 'Відмітити як виконане ✅'
    create_message: str = 'Відправити разове повідомлення 📧'
    create_payout: str = 'Створити платіж'
    create_chat: str = 'Створити чат з клієнтом 💬'
    cancel: str = 'Відмінити'
    plus: str = 'Нарахувати бали'
    minus: str = 'Зняти бали'
    skip: str = 'Пропустити'
    back: str = 'Повернутись назад'
    to_admin: str = 'В адмін панель'


class Menu:
    admin: str = 'В адмін панель 🖥'
    partners: str = 'Наші партнери 👜'
    card: str = 'Моя карта 🆔'
    cashback: str = 'Виплата кешбеку 💰'
    reserv: str = 'Забронювати 🛎'
    about: str = 'Про наш сервіс ℹ'
    news: str = 'Акції і новини 🆕'
    balance: str = 'Мій баланс 💰'
    history: str = 'Історя балансу 🧾'
    help: str = 'В мене є питання 💭'
    phone: str = 'Поділитись телефоном 📲'
    auth: str = 'Авторизуватися 📲'
    skip: str = 'Пропустити цей крок 👉'
    skipping: str = 'Пропустити'
    back: str = '◀ Назад'
    introduction: str = 'Зрозуміло 👌'
    rules: str = 'Правила сервісу'
    about_us: str = 'Про нас'
    how_it_work: str = 'Як це працює'
    about_bot: str = 'Про бота'


class Buttons:
    menu = Menu()
    back = Back()
    partners = Partners()
    articles = Articles()
    admin = Admin()
    history = History()

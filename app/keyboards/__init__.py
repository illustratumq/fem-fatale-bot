
class Back:
    categories: str = 'В категорії'
    partners: str = '◀ До партнерів'
    menu: str = 'В головне меню'


class Partners:
    next: str = '▶'
    prev: str = '◀'


class Articles:
    publish: str = 'Опублікувати 📬'
    next: str = 'Наступна ▶'
    prev: str = '◀ Попередня'


class Menu:
    partners: str = 'Наші партнери 👜'
    card: str = 'Моя карта 🆔'
    cashback: str = 'Виплата кешбеку 💰'
    reserv: str = 'Забронювати 🛎'
    about: str = 'Про наш сервіс ℹ'
    news: str = 'Акції і новини 🆕'
    balance: str = 'Мій баланс та історя переказів 💰'
    help: str = 'В мене є питання 💭'
    phone: str = 'Поділитись телефоном 📲'
    auth: str = 'Авторизуватися 📲'
    skip: str = 'Пропустити цей крок 👉'
    skipping: str = 'Пропустити'
    back: str = '◀ Назад'
    introduction: str = 'Зрозуміло 👌'


class Buttons:
    menu = Menu()
    back = Back()
    partners = Partners()
    articles = Articles()

import os

from PIL import Image, ImageFont, ImageDraw


def make_event_photo(title: str, description: str, status: str, client: str):
    file_number = len(os.listdir('app/data/')) + 1
    logo = Image.open('app/data/event.png')
    drawer = ImageDraw.Draw(logo)
    font = ImageFont.truetype('calibri.ttf', 65)
    drawer.text((50, 120), split_string(title, n=22), fill='black', font=font, stroke_width=1)
    font = ImageFont.truetype('calibri.ttf', 35)
    drawer.text((50, 215 + 50 * (len(title) // 23)), split_string(description), fill='#afafaf', font=font)
    drawer.text((50, 500), f'Статус: {status}', fill='#afafaf', font=font)
    drawer.text((50, 460), f'Клієнт: {client}', fill='#afafaf', font=font)
    new_path = f'app/data/{file_number}.png'
    logo.save(new_path)
    return new_path


def make_card_photo(card: str):
    logo = Image.open('app/data/logo.png')
    path = f'app/data/{card}.png'
    font = ImageFont.truetype('arial.ttf', 120)
    drawer = ImageDraw.Draw(logo)
    drawer.text((450 - len(card)/2*65, 515), card, fill='black', font=font)
    logo.save(path)
    return path


def split_string(string: str, n: int = 45):
    new_string = ''
    symbols = 0
    for word in string.split(' '):
        if symbols >= 230:
            return new_string[:230] + '[...]'
        if len(new_string.split('\n')[-1] + word) > n:
            new_string += f'\n{word}'
            symbols += n
        else:
            new_string += word
        new_string += ' '
    return new_string



import telebot
from PIL import Image, ImageFont, ImageDraw
from random import randint
from telebot import types
import re
import os
import time

my_bot = telebot.TeleBot('token')
re_x = '^X-\d+$'
re_y = '^Y-\d+$'


def create_list_gifts(part):
    return [os.path.join(part, name) for name in os.listdir(part)]


class Gifts:

    def __init__(self):
        self.list_gifts_win = create_list_gifts("gif_win")
        self.list_gifts_lose = create_list_gifts("gif_lose")
        self.list_gifts_miss = create_list_gifts("gif_miss")

    def next_gif_win(self):
        if not self.list_gifts_win:
            self.list_gifts_win = create_list_gifts("gif_win")
        if len(self.list_gifts_win) == 1:
            part = self.list_gifts_win.pop(0)
        else:
            num = randint(0, len(self.list_gifts_win)-1)
            part = self.list_gifts_win.pop(num)
        return part

    def next_gif_lose(self):
        if not self.list_gifts_lose:
            self.list_gifts_lose = create_list_gifts("gif_lose")
        if len(self.list_gifts_lose) == 1:
            part = self.list_gifts_lose.pop(0)
        else:
            num = randint(0, len(self.list_gifts_lose)-1)
            part = self.list_gifts_lose.pop(num)
        return part

    def next_gif_miss(self):
        if not self.list_gifts_miss:
            self.list_gifts_miss = create_list_gifts("gif_miss")
        if len(self.list_gifts_miss) == 1:
            part = self.list_gifts_miss.pop(0)
        else:
            num = randint(0, len(self.list_gifts_miss)-1)
            part = self.list_gifts_miss.pop(num)
        return part


class Game:

    def __init__(self):

        """Общие параметры игры"""
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.col_step = 6
        self.dict_step = {}
        self.step = 0
        self.hit_x = 0
        self.hit_y = 0
        self.time_x = False
        self.time_y = False
        self.size_text = 14
        self.col_choose_coordinate = 6
        self.font = ImageFont.truetype("ARLRDBD.TTF", self.size_text)
        self.step_list_coordinate = 5
        self.half_size_main_line = 15
        self.radius_main_point = 6
        """Параметры игрового поля"""
        self.color_elements = 'black'
        self.weight_place = 370
        self.height_place = 555
        self.indent_x = 40
        self.indent_y = 30
        self.step_count = 50
        self.color_place = 'white'
        self.place_img = None

    def create_trajectory_rocket(self):
        self.start_y = self.height_place - randint(60, 95)
        self.start_x = randint(self.indent_x * 3, self.weight_place - self.indent_x * 3)
        self.end_x = self.weight_place // 2
        self.end_y = 0
        self.dict_step[0] = {"x": self.start_x, "y": self.start_y}
        for i in range(1, self.col_step):
            temp_start_x = self.dict_step[i-1]['x']
            temp_start_y = self.dict_step[i-1]['y']
            cur_x = abs(temp_start_x - self.end_x) // (self.col_step - i)
            cur_y = (self.end_y - temp_start_y) // (self.col_step - i)
            if temp_start_x < self.end_x:
                temp_start_x += cur_x
            else:
                temp_start_x -= cur_x
            self.dict_step[i] = {"x": temp_start_x + randint(-50, 50), "y": temp_start_y + cur_y - randint(10, 25) +
                                 randint(10, 25)}
        self.dict_step[self.col_step - 1] = {"x": self.end_x, "y": self.end_y}

    def create_place(self):
        self.place_img = Image.new('RGB', (self.weight_place, self.height_place), self.color_place)
        pencil = ImageDraw.Draw(self.place_img)
        """Создание оси и нулевой координат, сначала ось Х, потом ось У и далее нулевая точка"""
        pencil.rectangle((0, self.height_place - self.indent_y, self.weight_place, self.height_place - self.indent_y),
                         fill=self.color_elements)
        pencil.polygon(((self.indent_x, 0), (self.indent_x - 5, 15), (self.indent_x + 5, 15)), fill=self.color_elements)

        pencil.rectangle((self.indent_x, 0, self.indent_x, self.height_place), fill=self.color_elements)
        pencil.polygon(((self.weight_place, self.height_place - self.indent_y),
                        (self.weight_place - 15, self.height_place - self.indent_y - 5),
                        (self.weight_place - 15, self.height_place - self.indent_y + 5)), fill=self.color_elements)

        pencil.ellipse((self.indent_x - 4, self.height_place - self.indent_y - 4,
                        self.indent_x + 4, self.height_place - self.indent_y + 4),
                       fill=self.color_elements)
        pencil.text((self.indent_x - 20, self.height_place - self.indent_y + self.size_text / 2 + 1), "0",
                    font=self.font, fill=self.color_elements)
        """Нанесение шкалы на ось Х"""
        for i in range(self.step_count, self.weight_place - self.indent_x, self.step_count):
            if not ((i // self.step_count) % 2):
                pencil.text((self.indent_x + i - self.size_text + 2,
                             self.height_place - self.indent_y + self.size_text / 2 + 1), str(i),
                            font=self.font, fill=self.color_elements)
                half = 6
            else:
                half = 4
            pencil.rectangle((self.indent_x + i, self.height_place - self.indent_y - half, self.indent_x + i,
                              self.height_place - self.indent_y + half), fill=self.color_elements)

        """Нанесение шкалы на ось Y"""
        for i in range(self.step_count, self.height_place - self.indent_y, self.step_count):
            if not ((i // self.step_count) % 2):
                pencil.text((5, self.height_place - self.indent_y - i - self.size_text / 2 - 1), str(i),
                            font=self.font, fill=self.color_elements)
                half = 6
            else:
                half = 4
            pencil.rectangle((self.indent_x - half, self.height_place - self.indent_y - i, self.indent_x + half,
                              self.height_place - self.indent_y - i), fill=self.color_elements)


new_game = Game()
gifts = Gifts()


@my_bot.message_handler(commands=['start'])
def start(message):
    my_bot.send_message(message.from_user.id, "Привіт!", reply_markup=create_main_menu())


@my_bot.message_handler(content_types=['text'])
def work(message):
    if message.text == "Правила гри":
        rules = "Тобі необхідно знищити неопізнаний об\'єкт (НО), який наближается до тебе.В тебе буде п\'ять спроб." \
                " Щоб знищити НО, тобі необхідно визначити його координати и вибрати окремо значення " \
                "\"X\" та \"Y\" з представлених варіантів. Якщо перше значення вибрано невірно," \
                " то ти переходиш к наступній спробі.Щасти!"
        my_bot.send_message(message.from_user.id, rules, reply_markup=create_main_menu())
    elif message.text == 'Нова гра':
        new_game.__init__()
        new_game.create_trajectory_rocket()
        new_game.create_place()
        new_game.time_x = True
        new_game.time_y = False
        new_game.create_trajectory_rocket()
        send_task(message, 'X')
    elif re.match(re_x, message.text) is not None and new_game.time_x is True:
        new_game.time_x = False
        new_game.time_y = True
        new_game.hit_x = int(message.text.split('-')[1])
        if new_game.dict_step[new_game.step]['x'] == new_game.hit_x:
            send_task(message, 'Y', text="Координата Х вказана вірно!")
        elif new_game.step == (new_game.col_step - 2):
            send_task(message, 'LOSE')
        else:
            new_game.step += 1
            send_task(message, 'X', text="Промахнувся!")
    elif re.match(re_y, message.text) is not None and new_game.time_y is True:
        new_game.time_x = True
        new_game.time_y = False
        new_game.hit_y = int(message.text.split('-')[1])
        if new_game.dict_step[new_game.step]['y'] == new_game.hit_y:
            send_task(message, 'WIN')
        elif new_game.step == (new_game.col_step - 2):
            send_task(message, 'LOSE')
        else:
            new_game.step += 1
            send_task(message, 'X', "MISS")
    elif message.text == 'chit':
        send_task(message, 'chit')


def send_task(message, type_coordinate, text=""):
    if type_coordinate == 'X':
        if text == "MISS":
            my_bot.send_message(message.from_user.id, text="Це .......")
            time.sleep(2)
            gif = open(gifts.next_gif_miss(), 'rb')
            my_bot.send_video(message.chat.id, gif)
            gif.close()
            time.sleep(2)
            my_bot.send_message(message.from_user.id, text='Мимо, але спроби ще є!')
            time.sleep(2)
        elif text != "" and text != "MISS":
            my_bot.send_message(message.from_user.id, text=text)

        x = new_game.dict_step[new_game.step]['x'] + new_game.indent_x
        y = new_game.height_place - new_game.dict_step[new_game.step]['y'] - new_game.indent_y
        pencil = ImageDraw.Draw(new_game.place_img)
        pencil.ellipse((x - new_game.radius_main_point, y - new_game.radius_main_point, x + new_game.radius_main_point,
                        y + new_game.radius_main_point), fill=new_game.color_elements)
        pencil.rectangle((x-new_game.half_size_main_line, y, x+new_game.half_size_main_line, y),
                         fill=new_game.color_elements)
        pencil.rectangle((x, y-new_game.half_size_main_line, x, y+new_game.half_size_main_line),
                         fill=new_game.color_elements)
        my_bot.send_photo(message.from_user.id, new_game.place_img,
                          reply_markup=create_random_menu_coordinates(new_game.dict_step[new_game.step]['x'],
                                                                      type_coordinate))
        new_game.time_x = True
        new_game.time_y = False
    elif type_coordinate == 'Y':
        my_bot.send_message(message.from_user.id, text=text,
                            reply_markup=create_random_menu_coordinates(new_game.dict_step[new_game.step]['y'],
                                                                      type_coordinate))
    elif type_coordinate == "WIN":
        my_bot.send_message(message.from_user.id, text="Це .......")
        time.sleep(2)
        gif = open(gifts.next_gif_win(), 'rb')
        my_bot.send_video(message.chat.id, gif)
        gif.close()
        time.sleep(1)
        my_bot.send_message(message.from_user.id, text='Влучний постріл, ти переміг!', reply_markup=create_main_menu())
    elif type_coordinate == "LOSE":
        my_bot.send_message(message.from_user.id, text="Це .......")
        time.sleep(2)
        gif = open(gifts.next_gif_lose(), 'rb')
        my_bot.send_video(message.chat.id, gif)
        gif.close()
        time.sleep(1)
        my_bot.send_message(message.from_user.id, text='Гра закінчена, тобі капець!', reply_markup=create_main_menu())
    elif type_coordinate == "chit":
        my_bot.send_message(message.from_user.id, text=f"x = {new_game.dict_step[new_game.step]['x']};"
                                                       f" y = {new_game.dict_step[new_game.step]['y']}")


def create_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Правила гри', 'Нова гра')
    return markup


def create_random_menu_coordinates(numb, type_coordinate):
    locate_coordinate = randint(0, new_game.col_choose_coordinate-1)
    min_coordinate = numb - locate_coordinate * new_game.step_list_coordinate
    l_c = [f"{type_coordinate}-{min_coordinate + i * new_game.step_list_coordinate}" for i in
           range(new_game.col_choose_coordinate)]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(l_c[0], l_c[1], l_c[2], l_c[3], l_c[4], l_c[5], 'Правила гри', 'Нова гра')
    return markup


my_bot.polling(none_stop=True, interval=0)

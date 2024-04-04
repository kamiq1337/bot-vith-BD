import telebot
import sqlite3


photo_url1= 'https://imgur.com/a/tEnEHmP'#мои фильмы
photo_url2= 'https://imgur.com/a/LRjrPca'#админ запрос
photo_url3= 'https://imgur.com/a/eqdAia3'#добавить фильм
# Создаем бота
bot = telebot.TeleBot('token')

# Создаем клавиатуру для inline-кнопок
keyboard = telebot.types.InlineKeyboardMarkup()
btn_add_film = telebot.types.InlineKeyboardButton(text="Добавить фильм", callback_data='add_films')
btn_show_user_films = telebot.types.InlineKeyboardButton(text="Мои фильмы", callback_data='show_user_films')
btn_show_all_user_films = telebot.types.InlineKeyboardButton(text="Все фильмы пользователей", callback_data='show_all_user_films')
btn_request_admin_rights = telebot.types.InlineKeyboardButton(text="Анкета на админа", callback_data='request_admin_rights')



keyboard.add(btn_add_film, btn_show_user_films, btn_show_all_user_films, btn_request_admin_rights)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Я бот для работы с базой данных. напиши привет или используй кнопки')
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)
    

def echo(message):
    if message.text.__contains__('привет') or message.text.__contains__('Привет'):
        bot.send_message(message.chat.id, 'привет!))')
    elif message.text.__contains__('пока'):
        bot.send_message(message.chat.id, 'покеда!')
# Обработчик текстовых сообщений для добавления фильма
@bot.message_handler(func=lambda message: True)
def add_film_step(message):
    conn = sqlite3.connect('BDforPython.db')
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS films (_id INTEGER PRIMARY KEY, title TEXT, year INTEGER, type TEXT, director TEXT, achievement TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS userfilms (user_id INTEGER, films_id INTEGER)")
    
    # Создаем таблицу usersteps, если она не существует
    cursor.execute("CREATE TABLE IF NOT EXISTS usersteps (user_id INTEGER PRIMARY KEY, step INTEGER, title TEXT, year INTEGER, type TEXT, director TEXT, achievement TEXT)")
    
    # Проверяем на каком этапе добавления фильма находится пользователь
    cursor.execute("SELECT * FROM usersteps WHERE user_id=?", (message.chat.id,))
    user_step = cursor.fetchone()
    
    if not user_step:
        # Если пользователь еще не начал добавление фильма, начинаем с первого шага
        cursor.execute("INSERT INTO usersteps (user_id, step) VALUES (?, ?)", (message.chat.id, 1))
        conn.commit()
    else:
        step = user_step[1]
        if step == 1:
            # Добавляем название фильма
            cursor.execute("UPDATE usersteps SET step=2, title=? WHERE user_id=?", (message.text, message.chat.id))
            conn.commit()
            bot.send_message(message.chat.id, "Введите год выпуска фильма:")
        elif step == 2:
            # Добавляем год выпуска фильма
            cursor.execute("UPDATE usersteps SET step=3, year=? WHERE user_id=?", (message.text, message.chat.id))
            conn.commit()
            bot.send_message(message.chat.id, "Введите тип фильма (художественный или документальный):")
        elif step == 3:
            # Добавляем тип фильма
            cursor.execute("UPDATE usersteps SET step=4, type=? WHERE user_id=?", (message.text, message.chat.id))
            conn.commit()
            bot.send_message(message.chat.id, "Введите автора фильма:")
        elif step == 4:
            # Добавляем автора фильма
            cursor.execute("UPDATE usersteps SET step=5, director=? WHERE user_id=?", (message.text, message.chat.id))
            conn.commit()
            bot.send_message(message.chat.id, "Введите награду фильма:")
        elif step == 5:
            # Добавляем награду фильма и завершаем добавление
            cursor.execute("INSERT INTO films (title, year, type, director, achievement) VALUES (?, ?, ?, ?, ?)",
                           (user_step[2], user_step[3], user_step[4], user_step[5], message.text))
            conn.commit()
            
            # Добавляем запись о том, что пользователь добавил этот фильм
            film_id = cursor.lastrowid
            cursor.execute("INSERT INTO userfilms (user_id, films_id) VALUES (?, ?)", (message.chat.id, film_id))
            conn.commit()
            
            bot.send_message(message.chat.id, f"Фильм {user_step[2]} успешнодобавлен в базу данных!")
            
            # Сбрасываем шаг пользователя
            cursor.execute("DELETE FROM usersteps WHERE user_id=?", (message.chat.id,))
            conn.commit()
    
    cursor.close()
    conn.close()

# Обработчик инлайн-кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'add_films':
        bot.send_photo(call.message.chat.id, photo=photo_url3)
        bot.send_message(call.message.chat.id, "Начнем добавление фильма. Введите название дважды:")
    elif call.data == 'show_user_films':
        conn = sqlite3.connect('BDforPython.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT title FROM films WHERE _id IN (SELECT films_id FROM userfilms WHERE user_id=?)", (call.message.chat.id,))
        user_films = cursor.fetchall()
        
        if user_films:
            films_list = "\n".join([film[0] for film in user_films])
            bot.send_photo(call.message.chat.id, photo=photo_url1)
            bot.send_message(call.message.chat.id, f"Ваши фильмы:\n{films_list}")
        else:
            bot.send_message(call.message.chat.id, "У вас пока нет добавленных фильмов.")
        
        cursor.close()
        conn.close()
    elif call.data == 'show_all_user_films':
        if call.message.chat.id == 6498420510:
            conn = sqlite3.connect('BDforPython.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT title FROM films")
            all_films = cursor.fetchall()
            
            if all_films:
                films_list = "\n".join([film[0] for film in all_films])
                bot.send_message(call.message.chat.id, f"Фильмы всех пользователей:\n{films_list}")
            else:
                bot.send_message(call.message.chat.id, "Пока нет добавленных фильмов.")
        else:
            bot.send_message(call.message.chat.id, "У вас нет прав доступа к этой функции.")
        
        cursor.close()
        conn.close()
    elif call.data == 'request_admin_rights':
        conn = sqlite3.connect('BDforPython.db')
        cursor = conn.cursor()
        # Создание таблицы requests_for_admin
        cursor.execute('''CREATE TABLE IF NOT EXISTS requests_for_admin (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER
                 )''')
        
        cursor.execute("INSERT INTO requests_for_admin (user_id) VALUES (?)", (call.message.chat.id,))
        conn.commit()
        
        bot.send_message(call.message.chat.id, "Запрос на админские права отправлен. когда вы получите админские права у вас появиться возможность смотреть какие фильмы добавили пользователи")
        bot.send_photo(call.message.chat.id, photo=photo_url2)

        cursor.close()
        conn.close()
    
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
            text="ЭТО ТЕСТОВОЕ УВЕДОМЛЕНИЕ!!")

# Запускаем бота
bot.polling()


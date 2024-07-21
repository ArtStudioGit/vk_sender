from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from configparser import ConfigParser
import climage, threading, time, logging, random, requests, datetime, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.DEBUG, filename="bot_log.txt", filemode="w", format="%(asctime)s %(levelname)s %(message)s")
settings = ConfigParser()
settings.read('config.txt')
ver = "v5_stab-beta5"
token, stopped, users, limit, mlimit, latency, number, paused, attempt = "", False, [], 24 * 3600, 999, "90-160", 0, False, "Пусто"
with open("login.txt", 'r', encoding="utf-8") as file:
    login = file.read().strip()
with open("password.txt", 'r', encoding="utf-8") as file:
    password = file.read().strip()
with open("token.txt", 'r', encoding="utf-8") as file:
    token = file.read().strip()

def get_token():
    try:
        global token
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://oauth.vk.com/authorize?client_id=6287487&scope=1073737727&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1')
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, 'email')))
        login_form = driver.find_element(By.NAME, 'email')
        login_form.send_keys(login)
        password_form = driver.find_element(By.NAME, 'pass')
        password_form.send_keys(password)
        accept_button = driver.find_element(By.ID, 'install_allow')
        accept_button.click()
        logging.debug("Get Token: Login")
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'oauth_captcha')))
            logging.debug("Get Token: Captcha")
            captcha_image = driver.find_elements(By.CLASS_NAME, 'oauth_captcha')
            for image in captcha_image:
                image_data = image.screenshot_as_png
                with open('captcha.png', 'wb') as file:
                    file.write(image_data)
                print(climage.convert('captcha.png', is_unicode=True, width=150))
            captcha_form = driver.find_element(By.NAME, 'captcha_key')
            captcha_form.send_keys(input("Введите текст с капчи: "))
            logging.debug("Get Token: Captcha Succesfully")
        except Exception as e:
            print(f"Кажется, капчи не было.")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="oauth_wrap_content"]/div[3]/div/div[1]/button[1]')))
        button = driver.find_element(By.XPATH, '//*[@id="oauth_wrap_content"]/div[3]/div/div[1]/button[1]')
        button.click()
        logging.debug("Get Token: Redirect")

    except Exception as e:
        logging.debug(f"Get Token: Error: {e}")
        print(e)

    finally:
        try:
            redirected_url = driver.current_url
            start = redirected_url.split("access_token=")[1]
            token = start.split("&expires_in")[0]
            with open("token.txt", 'w', encoding="utf-8") as file:
                file.write(token)
                logging.debug("Get Token: Succesfully writed token in file")
                file.close()
            print(f"\n\n\nТокен: {token}")
            logging.debug(f"Get Token: Succesfully, Token: {token}")
            driver.quit()
        except Exception as e:
            logging.debug(f"Get Token: Error: {e}")
            print(e)

def token_reget():
    logging.debug("Token Reget: Started")
    while True:
        time.sleep(12 * 3600)
        get_token()
        logging.debug("Token Reget: Regeted")
token_reget_thread = threading.Thread(target = token_reget)
token_reget_thread.start()

def commands():
    global stopped, limit, latency, number, mlimit, ver, token, paused, attempt
    with open("token.txt", 'r', encoding="utf-8") as file:
        token = file.read().strip()
        logging.debug(f"Longpoll: Token: {token}")
    vk_session = VkApi(token=token)
    vk = vk_session.get_api()
    try:
        longpoll = VkLongPoll(vk_session)
        logging.debug("Longpoll: Started")
        print("BOT STARTED")
        vk.messages.send(user_id=vk.users.get()[0]['id'], message=f"Бот запущен, для вывода возможных команд и статистики используйте команду /info\nВерсия: {ver}", random_id=0)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                try:
                    if "ИНФО" in event.text:
                        continue
                    if '/' in event.text:
                        logging.debug(f"Longpoll: Geted command {event.text}")
                    if event.text == "/info":
                        logging.debug(f"Longpoll: Command {event.text} started")
                        vk.messages.send(user_id=event.user_id, message=f"""
                        ИНФО:
                                         
                        Как установить сообщение?
                        Создайте файл с сообщением, его имя не имеет значения. 
                        Если вы хотите чтобы бот мог отправлять сообщения выбираемые случайно, то разделяйте их символом #
                        Пример:
                        Сообщение1
                        #
                        Сообщение2
                        #
                        Сообщение3               
                        Отправьте файл боту с сообщением message
                        Готово.
                                         
                        Как установить список пользователей?
                        Создайте файл со списком, его имя не имеет значения. 
                        Отправьте файл боту с сообщением users
                        Готово.

                        Команда: /start
                        Команда для старта бота

                        Команда: /stop
                        Команда для остановки бота     

                        Команда: /pause
                        Команда для приостановки бота
                        Внимание! Бот проверяет приостановлен ли он каждые 5 секунд вместо меньшего промежутка для увеличения скорости работы сервера и бота на нем                     

                        Команда: /latency
                        Команда для установки случайной задержки(в секундах) между сообщениями. По умолчанию случайно 90-160 секунд.
                        Пример: /latency 30-90

                        Команда: /mlimit
                        Команда для установки лимита сообщений сообщений в день(24 часа)
                        Пример: /mlimit 5
                            
                        Команда: /limit
                        Команда для установки времени(в часах) которое будет ждать бот когда отправит максимально количество сообщений в день(24 часа)
                        Пример: /limit 5
                                         
                        Команда: /test
                        Команда для тестирования бота, ставит задержку 10-20, лимит сообщений 5, а ждать бот после достижения лимита будет 20 секунд. Все, что нужно для тестов.
                        Пример: /test
                                         
                        Команда: /check
                        Команда для получения информации о последней попытке отправки
                        Пример: /check

                        Команда: /check
                        Команда для получения информации о последней попытке отправки
                        Пример: /check

                        Команда: /save
                        Команда для настроек бота(лимит, время ожидания, задержка)
                        Пример: /save

                        Команда: /load
                        Команда для загрузки настроек
                        Пример: /load                                         

                        Текущие параметры:

                        Версия бота: {ver}
                        Токен: {token}
                        Бот остановлен: {stopped}
                        Бот приостановлен: {paused}
                        Бот ждет часов после достижения лимита:  {limit / 3600} часа
                        Лимит сообщений в день: {mlimit} сообщений
                        Задержка между сообщениями: {latency} секунд
                        Отправлено сообщений за эти 24 часа: {number} сообщений
                        """, random_id=0)
                        logging.debug(f"Longpoll: Command {event.text} ended")
                    if event.text == "/start":
                        logging.debug(f"Longpoll: Command {event.text} started")
                        vk.messages.send(user_id=event.user_id, message="Бот запущен", random_id=0)
                        stopped = False
                        main_cycle_thread = threading.Thread(target = main_cycle)
                        main_cycle_thread.start()
                        logging.debug(f"Longpoll: Command {event.text} ended")
                    if event.text == "/stop":
                        logging.debug(f"Longpoll: Command {event.text} started")
                        vk.messages.send(user_id=event.user_id, message="Бот остановлен", random_id=0)
                        stopped = True
                        number = 0
                        logging.debug(f"Longpoll: Command {event.text} ended")
                    if event.text == "/pause":
                        logging.debug(f"Longpoll: Command {event.text} started")
                        paused = not paused
                        vk.messages.send(user_id=event.user_id, message=f"Пауза: {paused}", random_id=0)
                        logging.debug(f"Longpoll: Command {event.text} ended")
                    if "/limit" in event.text:
                        logging.debug(f"Longpoll: Command {event.text} started")
                        limit = int(event.text.split(' ')[1]) * 3600
                        vk.messages.send(user_id=event.user_id, message=f"Бот будет ждать {limit / 3600} часов после достижения лимита", random_id=0)
                        logging.debug(f"Longpoll: Command {event.text} ended")
                    if "/mlimit" in event.text:
                        logging.debug(f"Longpoll: Command {event.text} started")
                        mlimit = event.text.split(' ')[1]
                        vk.messages.send(user_id=event.user_id, message=f"Лимит количества сообщений в день теперь равен: {mlimit} сообщений", random_id=0)
                        logging.debug(f"Longpoll: Command {event.text} ended")
                    if "/latency" in event.text:
                        logging.debug(f"Longpoll: Command {event.text} started")
                        latency = event.text.split(' ')[1].split('-')
                        vk.messages.send(user_id=event.user_id, message=f"Бот будет ждать {latency[0]}-{latency[1]} секунд перед отправкой сообщения", random_id=0)
                        logging.debug(f"Longpoll: Command {event.text} ended")
                    if event.text == "/check":
                        logging.debug(f"Longpoll: Command {event.text} started")
                        vk.messages.send(user_id=event.user_id, message=attempt, random_id=0)
                        logging.debug(f"Longpoll: Command {event.text} ended")
                    if event.text == "/save":
                        logging.debug(f"Longpoll: Command {event.text} started")
                        if not settings.has_section('settings'): settings.add_section('settings')
                        settings.set('settings', 'limit', str(limit))
                        settings.set('settings', 'mlimit', str(mlimit))
                        settings.set('settings', 'latency', str(latency))
                        with open('config.txt', 'w') as f:
                            settings.write(f)
                        vk.messages.send(user_id=event.user_id, message="Настройки сохранены", random_id=0)
                        logging.debug(f"Longpoll: Command {event.text} ended")
                    if event.text == "/load":
                        logging.debug(f"Longpoll: Command {event.text} started")
                        limit = json.loads(settings.get('settings', 'limit'))
                        mlimit = json.loads(settings.get('settings', 'mlimit'))
                        latency = json.loads(settings.get('settings', 'latency'))
                        vk.messages.send(user_id=event.user_id, message="Настройки загружены", random_id=0)
                        logging.debug(f"Longpoll: Command {event.text} ended")
                    if "users" in event.text:
                        logging.debug(f"Longpoll: Command {event.text} started")
                        attachments = vk.messages.getById(message_ids=event.message_id, extended=True, fields='attachments')['items'][0]['attachments']
                        if attachments:
                            attachment = attachments[0]
                            if attachment['type'] == 'doc':
                                doc = attachment['doc']
                                response = requests.get(doc['url'])
                                with open("users.txt", "wb") as f:
                                    f.write(response.content)
                                logging.debug(f"Longpoll: Users.txt writed")
                                vk.messages.send(user_id=event.user_id, message=f"Список пользователей получен", random_id=0)
                        logging.debug(f"Longpoll: Command {event.text} ended")
                    if "message" in event.text:
                        logging.debug(f"Longpoll: Command {event.text} started")
                        attachments = vk.messages.getById(message_ids=event.message_id, extended=True, fields='attachments')['items'][0]['attachments']
                        if attachments:
                            attachment = attachments[0]
                            if attachment['type'] == 'doc':
                                doc = attachment['doc']
                                response = requests.get(doc['url'])
                                with open("message.txt", "wb") as f:
                                    f.write(response.content)
                                logging.debug(f"Longpoll: Message.txt writed")
                                vk.messages.send(user_id=event.user_id, message=f"Сообщение получено", random_id=0)
                    if "/test" in event.text:
                        logging.debug(f"Longpoll: Command {event.text} started")
                        latency = [10, 20]
                        vk.messages.send(user_id=event.user_id, message=f"Бот будет ждать {latency[0]}-{latency[1]} секунд перед отправкой сообщения", random_id=0)
                        limit = 20
                        vk.messages.send(user_id=event.user_id, message=f"Бот будет ждать {limit} секунд после достижения лимита", random_id=0)
                        mlimit = 5
                        vk.messages.send(user_id=event.user_id, message=f"Лимит количества сообщений в день теперь равен: {mlimit} сообщений", random_id=0)
                        vk.messages.send(user_id=event.user_id, message="Бот запущен", random_id=0)
                        stopped = False
                        main_cycle_thread = threading.Thread(target = main_cycle)
                        main_cycle_thread.start()           
                except Exception as e:
                    logging.debug(f"Longpoll: Error: {e} Command: {event.text}")
                    vk.messages.send(user_id=event.user_id, message=f"Произошла ошибка: {e}\nс командой: {event.text}", random_id=0)
                    print(e)
                    time.sleep(20)
    except Exception as e:
        if "access_token" in str(e):
            logging.debug(f"Longpoll: access_token error: {e}")
            get_token()
            logging.debug(f"Longpoll: get_token() sucessfully finished")
        logging.debug(f"Longpoll: Error: {e}")
        commands_thread = threading.Thread(target = commands)
        commands_thread.start()
        logging.debug("Longpoll: Restarted")
        print(e)

def limiter():
    global number
    while True:
        try:
            time.sleep(24 * 3600)
            number = 0
        except Exception as e:
            logging.debug(f"Limiter: Error: {e}")
            print(e)

def main_cycle(): 
    logging.debug("Main Cycle: Started")
    global stopped, token, number, mlimit, users, paused, attempt
    with open("token.txt", 'r', encoding="utf-8") as file:
        token = file.read().strip()
    try:
        with open("users.txt", 'r', encoding="utf-8") as file:
            logging.debug("Main Cycle: users.txt opened")
            for line in file:
                if "id" in line.strip():
                    users.append(line.strip().split("id")[1])
                    continue
                else:
                    users.append(line.strip())
        with open("message.txt", 'r', encoding="utf-8") as file:
            logging.debug("Main Cycle: message.txt opened")
            message = file.read().strip().split("#")
            print(f"Всего сообщений: {len(message)}, Сообщения: {message}")
        logging.debug("Main Cycle: users.txt readed")
        vk_session = VkApi(token=token)
        vk = vk_session.get_api()
        logging.debug("Main Cycle: Vk Session started")
        try:
            for user_id in users:
                if paused == True:
                    time.sleep(5)
                    continue
                if number >= int(mlimit):
                    print(f"Лимит достигнут, лимит сообщений был: {mlimit}\nСообщений отправлено: {number}\nБот ждет: {limit / 3600} часов")
                    logging.debug(f"Main Cycle: Limit exceeded, number = {number}, mlimit = {mlimit}, waiting {limit / 3600} hours...")
                    vk.messages.send(user_id=vk.users.get()[0]['id'], message=f"Лимит достигнут, лимит сообщений был: {mlimit}\nСообщений отправлено: {number}\nБот ждет: {limit / 3600} часов", random_id=0)
                    number = 0
                    time.sleep(limit)
                if stopped == True:
                    logging.debug("Main Cycle: Bot stopped")
                    break
                try:
                    num = random.randint(0, len(message) - 1)
                    vk.messages.send(user_id=int(user_id), message=message[num], random_id=0)
                    print(f"Отправлено: {user_id}, Сообщение: {num}, Номер в списке: {number}")
                    logging.debug(f"Main Cycle: Sended message to: {user_id}, Number: {number}")
                    attempt = f"Попытка отправки пользователю: @id{user_id} ({user_id})\nУспешно отправлено\nВремя попытки: {datetime.datetime.now()}\nНомер контакта в списке: {number}"
                    number += 1
                except Exception as e:
                    print(f"Не отправлено: {user_id}\nОшибка: {e}")
                    attempt = f"Попытка отправки пользователю: @id{user_id} ({user_id})\nОшибка: {e}\nВремя попытки: {datetime.datetime.now()}\nНомер контакта в списке: {number}"
                    logging.debug(f"Main Cycle: Not sended message to: {user_id} Error: {e}")
                    if "access_token" in str(e):
                        logging.debug(f"Main Cycle: access_token error: {e}")
                        get_token()
                        logging.debug(f"Main Cycle: get_token() sucessfully finished")
                    if "spam" in str(e):
                        logging.debug(f"Main Cycle: Error with spam: {e}")
                        while True:
                            time.sleep(3600)
                            try:
                                vk.messages.send(user_id=int(user_id), message=message, random_id=0)
                            except Exception as e:
                                if "spam" in str(e):
                                    logging.debug(f"Main Cycle: Error with spam continues")
                                    continue
                            logging.debug(f"Main Cycle: Error with spam ended")
                            break
                if latency == "90-160":
                    waittime = random.randint(90, 160)
                    print(f"Бот будет ждать: {waittime} секунд, latency: {latency[0]}-{latency[1]}")
                    time.sleep(waittime)
                else:
                    waittime = random.randint(int(latency[0]), int(latency[1]))
                    print(f"Бот будет ждать: {waittime} секунд, latency: {latency[0]}-{latency[1]}")
                    time.sleep(waittime)
            print("Все успешно отправлено, выход...")
            logging.debug("Main Cycle: Breaking...")
            vk.messages.send(user_id=vk.users.get()[0]['id'], message="Все сообщения успешно отправлены)", random_id=0)
        except Exception as e:
            logging.debug(f"Main Cycle: Error: {e}")
            print(f"Ошибка: {e}")
            if "Captcha needed" in str(e):
                logging.debug(f"Main Cycle: Captcha needed, waiting 20 sec...")
                time.sleep(20)
                logging.debug(f"Main Cycle: Captcha needed, waiting completed")
            if "access_token" in str(e):
                logging.debug(f"Main Cycle: access_token error: {e}")
                get_token()
                logging.debug(f"Main Cycle: get_token() sucessfully finished")
            if "spam" in str(e):
                logging.debug(f"Main Cycle: Error with spam: {e}")
                while True:
                    time.sleep(12 * 3600)
                    try:
                        vk.messages.send(user_id=int(user_id), message=message, random_id=0)
                    except Exception as e:
                        if "spam" in str(e):
                            logging.debug(f"Main Cycle: Error with spam continues")
                            continue
                    logging.debug(f"Main Cycle: Error with spam ended")
                    break
    except Exception as e:
            logging.debug(f"Main Cycle: Error: {e}")
            print(f"Ошибка: {e}")
            if "access_token" in str(e):
                logging.debug(f"Main Cycle: access_token error: {e}")
                get_token()
                logging.debug(f"Main Cycle: get_token() sucessfully finished")
            if "spam" in str(e):
                logging.debug(f"Main Cycle: Error with spam: {e}")
                while True:
                    time.sleep(3600)
                    try:
                        vk.messages.send(user_id=int(user_id), message=message, random_id=0)
                    except Exception as e:
                        if "spam" in str(e):
                            logging.debug(f"Main Cycle: Error with spam continues")
                            continue
                    logging.debug(f"Main Cycle: Error with spam ended")
                    break
            main_cycle_thread = threading.Thread(target = main_cycle)
            main_cycle_thread.start()

commands_thread = threading.Thread(target = commands)
commands_thread.start()
logging.debug(f"Starter: Bot version: {ver}")
logging.debug("Starter: First Vk Session started")
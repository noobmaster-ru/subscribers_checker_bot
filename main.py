from gspread import Client,service_account
from telethon.sync import TelegramClient
import telebot
import os 
from dotenv import load_dotenv

# создаём клиента для работы с Google Sheets
def client_init_json() -> Client:
    return service_account(filename='placa-tables-7b37297f8489.json')

# получаем нашу таблицу по ссылке url
def get_table_by_url(client: Client, table_url):
    return client.open_by_url(table_url)


def main():
    load_dotenv()
    # если будем заливать на сервер нужно ли им передавать эти значения?????
    # ссылка на таблицу
    table_url = os.getenv('table_url')

    # api и hash для google cloud account
    api_google_sheets_id = os.getenv("api_google_sheets_id")
    api_google_sheets_hash = os.getenv("api_google_sheets_hash")

    # токен бота
    bot_token = os.getenv("bot_token")

    # id канала, у которого будем проверять подписку
    channel_id = os.getenv("channel_id") # id канала Placa

    # Создаем клиента и открываем нашу таблицу DB v0
    client = client_init_json()
    spreadsheet = get_table_by_url(client, table_url)

    # открываем лист Рыжий Active
    ginger_active_sheet = spreadsheet.worksheet("Рыжий Active")

    # получаем список списков - все данные из гугл-формы по нашим клиентам 
    list_of_lists = ginger_active_sheet.get_all_values()

    # Получаем индекс последней заполненной строки
    last_row_index = len(list_of_lists)

    # записываем в client_tg_nicknames_list - все тг ники наших клиентов
    clients_tg_nicknames_list = [client[1] for client in list_of_lists]
    
    # удаляем хедер 
    clients_tg_nicknames_list.pop(0) 

    # список id всех клиентов
    clients_ids_list = []
    bot = TelegramClient('bot', api_google_sheets_id, api_google_sheets_hash).start(bot_token=bot_token)

    # добавляем в список все id
    with bot:
        for nick in clients_tg_nicknames_list:
            try:
                user_id = bot.get_peer_id(nick)
                clients_ids_list.append(user_id)
            except Exception:
                clients_ids_list.append("Error_in_nickname")

    # получаем доступ к листу "subscribers_tracker"
    subscribers_tracker_sheet = spreadsheet.worksheet("subscribers_tracker")

    # список айдишек клиентов для записи в колонку Е листа "subscribers_tracker"
    E_column = subscribers_tracker_sheet.range(f'E2:E{last_row_index}')

    # записываем в список все айдишки 
    for i, val in enumerate(clients_ids_list):  
        E_column[i].value = val 

    # записываем айдишки в таблицу в лист "subscribers_tracker" в колонку E
    subscribers_tracker_sheet.update_cells(E_column)

    # список для каждого клиента с sub/not sub
    sub_not_sub = []

    # добавляем в список трекер для каждого клиента: подписан/неподписан на канал
    bot = telebot.TeleBot(bot_token)
    for id in clients_ids_list:
        try:
            result = bot.get_chat_member(channel_id, id)
            sub_not_sub.append('sub')
        except Exception:
            sub_not_sub.append("not_sub")

    # список sub/not_sub клиентов для записи в колонку F листа "subscribers_tracker"
    f_column = subscribers_tracker_sheet.range(f'F2:F{last_row_index}')

    # записываем в список все sub/not_sub
    for i, val in enumerate(sub_not_sub):  
        f_column[i].value = val
    
    # записываем все значения sub/not_sub в лист  "subscribers_tracker" в колонку F
    subscribers_tracker_sheet.update_cells(f_column)


if __name__ == "__main__":
    main()
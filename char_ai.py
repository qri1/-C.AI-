import asyncio
from PyCharacterAI import Client
import time
from pythmc import ChatLink
import os
import sys

#=================================== Переменные ==============================================

token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkVqYmxXUlVCWERJX0dDOTJCa2N1YyJ9.eyJpc3MiOiJodHRwczovL2NoYXJhY3Rlci1haS51cy5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMTU3OTEwMjQ1Mzk5NjkyODQzNjciLCJhdWQiOlsiaHR0cHM6Ly9hdXRoMC5jaGFyYWN0ZXIuYWkvIiwiaHR0cHM6Ly9jaGFyYWN0ZXItYWkudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY5MDgyODIyMCwiZXhwIjoxNjkzNDIwMjIwLCJhenAiOiJkeUQzZ0UyODFNcWdJU0c3RnVJWFloTDJXRWtucVp6diIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwifQ.M1mjxfc-TTfeNd4q9ZVsmqU88oRu4G0zXwSRUbIPB2w6lGgHJHZlmyU4EUDYgna3ETdvEIgbLzZNtok7emTHhCCGvmxTg6Qocy27EpdLNgVlv7vbyOzrXcSUKmHB9_XQnlcrz2UcPT_Sv7w-FrF68_4epxn-Tjp9hf77IgSAbYQU6D1N5IlRvZ4EKOQ5KlKlIJQ_8KTCkTw9RGgqg80UiS1kWy2aRd1fW4NeIIcgKOP4090hqskjhAR-Mq4J8hlUV4r2jLB0kkOgqrordEMiBwmNP5YG0FTbrsdPS1Xtyn3StMxMWP4Ddb5LW91FXbsSgUdxsLC7ESbUmP47sFtnNw"
chatMC = ChatLink()

WhiteList = []
is_sended = ""
players_status = {}
players_chats = {}

#==================================== Функции ================================================

#-----Проверка WhiteList-----
def _white_list_check():
    global WhiteList
    with open("WhiteList.txt", "r") as f:
        for name in f.readlines():
            name = name.replace("\n", "")
            if not(name in WhiteList):
                WhiteList.append(name)

#-----Проверка статусов игроков-----
def _player_status_check():
    global players_status
    for name in WhiteList:
        try:
            value = players_status[name]
        except KeyError:
            players_status[name] = False

#-----Сообщение без ника-----
def _cut_name_from_message(mes, name):
    return f"{mes}"[len(f"{name}: "):]

#-----Наличие ника в сообщении-----
def _name_in_message(name, mes):
    if mes[:len(name)] == name:
        return True
    else: 
        return False

#-----Наличие команд в сообщении-----
def _comand_in_chat():
    global is_sended

    message_list = chatMC.get_history(limit=1)
    for messageMC in message_list:
        for name in WhiteList:
            if (_name_in_message(name, messageMC.content)) and (messageMC.content != is_sended):
                if "+nipa" in messageMC.content:
                    k = 0
                    for player in WhiteList:
                        if players_status[player] == True:
                            k += 1
                    if k == 0:
                        players_status[name] = True
                        is_sended = messageMC.content
                        return 0
                elif "-nipa" in messageMC.content:
                    players_status[name] = False
                    is_sended = messageMC.content
                    return 0
    time.sleep(0.1)


#=============================== Создание дирректорий =======================================

#-----Создание файла WhiteList-----
if not(os.path.exists("WhiteList.txt")):
    with open("WhiteList.txt", "w") as f:
        print("", end="", file=f)
    input("Введите в WhiteList.txt список ников (каждый ник на новой строке)")
    sys.exit()

#-----Добавление статуса False игрокам-----
for name in WhiteList:
    players_status[name] = False

#================================ Исполнительная чать кода ======================================

async def main():
    global is_sended
    global players_chats

    client = Client()
    await client.authenticate_with_token(token)
    
    username = (await client.fetch_user())['user']['username']
    print(f'Authenticated as {username}')


    character_id = "WdpPgJHqMCRfoDFlsZNEQ-qaF1buA_VDgLS9V1vsB8M"



    _white_list_check()
    _player_status_check()

    #-----Создание каждому игроку чата-----
    for name in WhiteList:
        players_chats[name] = await client.create_or_continue_chat(character_id)


    while True:
        _comand_in_chat()
        message_list = chatMC.get_history(limit=1)
        for messageMC in message_list:
            for name in WhiteList:
                if (len(players_status) != 0) and players_status[name]:
                    if (_name_in_message(name, messageMC.content)) and (messageMC.content != is_sended):
                        if not("+nipa" in messageMC.content) and not("-nipa" in messageMC.content):
                            message = messageMC.content[len(f"{name}: "):]
                            answer = await players_chats[name].send_message(message)
                            chatMC.send(answer.text)
                            is_sended = messageMC.content
        time.sleep(0.1)


asyncio.run(main())
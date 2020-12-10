# quiz_bot
 
Этот проект позволяет создать своего бота для викторин (VK, Telegram). Этого бота еще нужно улучшать, стандарты MVP выполнены.

![пример телеграм](https://i.imgur.com/qY9j7Bc.png)

## Подготовка к запуску Mac OS
Сначала зарегестрируйтесь на [redis](https://redis.io/)     
Уставновить [Python 3+](https://www.python.org/downloads/)

Установить, создать и активировать виртуальное окружение

```
pip3 install virtualenv
python3 -m venv env
source env/bin/activate
```

Установить библиотеки командой

```
pip3 install -r requirements.txt
```

Запуск ботов 

```
python3 tg_bot.py
python3 vk_bot.py
```

Создайте файл ".env" в него надо прописать ваши token'ы.   
В переменную `TG_TOKEN` его можно получить в отце всех ботов @botfather в телеграме.    
В переменную `REDIS_HOST` адрес базы данных.    
В переменную `REDIS_PORT` порт базы данных.    
В переменную `REDIS_PASSWORD` пароль от базы данных.    
    
**Пример**  
```
TG_TOKEN=1429262980:AAF0N4110ovItQ63HPsfb7d4hWg02re4Nr0
VK_TOKEN=74a0755ce12b361b1a036811792f842e09c885d3ec4d33d5d903552268678488c250029645fa607c1ccdf
REDIS_HOST=redis-14895.c92.us-east-1-3.ec2.cloud.redislabs.com
REDIS_PORT=11835
REDIS_PASSWORD=s2aH9KMojd4afChrCtOxxKbdzwRO2hSR
```

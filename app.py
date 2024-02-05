import io
import g4f
import json
import requests
from flask import Flask, request

BOT_TOKEN = '6949099878:AAFLahQxI31DjKTlmWR_usBYtYHv40czRxk'
ADMIN = 5934725286

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_webhook():
    try:
        process(json.loads(request.get_data()))
        return 'Success!'
    except Exception as e:
        print(e)
        return 'Error'


def process(update):
    if 'message' in update:
        if 'text' in update['message']:
            message = update['message']['text']
            if message == '/start':
                if not any(str(update['message']['from']['id']) in line.split()[0] for line in open('users.txt')):
                    with open('users.txt', 'a') as file:
                        file.write(f"{update['message']['from']['id']} {update['message']['from']['first_name'].split()[0]}\n")
                    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',params={'chat_id': update['message']['from']['id'],'text': f"✅ *Hello <a href='tg://user?id={update['message']['from']['id']}'>{update['message']['from']['first_name']}</a> !*", 'parse_mode': 'Markdown'})
                with open(f"{update['message']['from']['id']}.txt", 'w') as file:
                    file.write(' ')
                menu(update['message']['from']['id'])
            elif message == '/ChatGPT' or message == '/Bing' or message == '/You':
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage", data={"chat_id": update['message']['from']['id'],"message_id": update['message']['message_id']})
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',params={'chat_id': update['message']['from']['id'], 'text': f"✅ *You are using {message[:1]} AI!*",'parse_mode': 'Markdown'})
                with open(f"{update['message']['from']['id']}.txt", 'w') as file:
                    file.write(message)
            elif message == '/menu':
                menu(update['message']['from']['id'])
            else:
                try:
                    with open(f"{update['message']['from']['id']}.txt", 'r') as file:
                        model = file.readline()
                    core(update['message']['from']['id'], model, update['message']['text'])
                except:
                    with open(f"{update['message']['from']['id']}.txt", 'w') as file:
                        file.write(' ')
                    menu(update['message']['from']['id'])
    elif 'callback_query' in update and 'data' in update['callback_query']:
        data = update['callback_query']['data']
        if data == '/ChatGPT' or data == '/Bing' or data == '/You':
            reaction = {
                "/ChatGPT": "❤️",
                "/Bing": "❤️‍🔥",
                "/You": "💘",
            }
            with open(f"{update['callback_query']['from']['id']}.txt", 'w') as file:
                file.write(data)
            reply_markup = {'inline_keyboard': [
                [{'text': f"Bing AI ❤️‍🔥", 'callback_data': f"/Bing"}],
                [{'text': f"ChatGPT ❤️", 'callback_data': f"/ChatGPT"}],
                [{'text': f"You AI 💘", 'callback_data': f"/You"}]
            ]}
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',params={'chat_id': update['callback_query']['from']['id'], 'message_id': update['callback_query']['message']['message_id'],'text': f"_You chose_ *{data[1:]} AI*", 'parse_mode': 'Markdown','reply_markup': json.dumps(reply_markup)}).json()
            params = {'chat_id': update['callback_query']['from']['id'],'message_id': update['callback_query']['message']['message_id'],'is_big': True,'reaction': json.dumps([{'type': 'emoji', 'emoji': f"{reaction.get(data)}"}])}
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction', params=params).json()
        elif data[0] == 'R':
            with open(f"{update['callback_query']['from']['id']}.txt", 'r') as file:
                model = file.readline()
            core(update['callback_query']['from']['id'], model, data[2:])
        elif data == 'Change':
            menu(update['callback_query']['from']['id'])
    return
def menu(user_id):
    reply_markup = {'inline_keyboard': [
        [{'text': f"Bing AI ❤️‍🔥", 'callback_data': f"/Bing"}],
        [{'text': f"ChatGPT ❤️", 'callback_data': f"/ChatGPT"}],
        [{'text': f"You AI 💘", 'callback_data': f"/You"}]
    ]}
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',params={'chat_id': user_id, 'text': f"*Choose one:*",'parse_mode': 'Markdown', 'reply_markup': json.dumps(reply_markup)})
    return
def core(user_id, mode, query):
    if mode == '/ChatGPT':
        model = 'gpt-3.5-turbo'
        provider = g4f.Provider.Liaobots
    elif mode == '/Bing':
        model = 'gpt-4-32k-0613'
        provider = g4f.Provider.Bing
    elif mode == '/You':
        model = 'gpt-3.5-turbo'
        provider = g4f.Provider.You
    response = g4f.ChatCompletion.create(
        model=model,
        provider=provider,
        messages=[{'role': 'user', 'content': query}],
        stream=True,
    )
    output = ""
    for message in response:
        output += message
    reply_markup = {'inline_keyboard': [[{'text': f"Regenerate ♻️", 'callback_data': f'R {query}'}, {'text': f"Alter AI 〽️", 'callback_data': 'Change'}]]}
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', json={'chat_id': user_id,'text': f'{output}','parse_mode': 'Markdown','reply_markup': reply_markup}).json()
    return

def send_users():
    with open('users.txt', 'r') as file:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",params={'chat_id': ADMIN},files={'document': ('Users.txt', io.StringIO(''.join(file.readlines())))})
    file.close()
    return

if __name__ == '__main__':
    app.run(debug=False)

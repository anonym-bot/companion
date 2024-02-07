import io
import g4f
import time
import json
import requests
from flask import Flask, request


BOT_TOKEN = '6949099878:AAFLahQxI31DjKTlmWR_usBYtYHv40czRxk'
ADMIN = 5934725286
GROUP = -4099666754

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
                    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',params={'chat_id': update['message']['from']['id'],'text': f"✅ *Hello <a href='tg://user?id={update['message']['from']['id']}'>{update['message']['from']['first_name']}</a> !*", 'parse_mode': 'HTML'})
                with open(f"{update['message']['from']['id']}.txt", 'w') as file:
                    file.write(' ')
                menu(update['message']['from']['id'])
            elif message == '/Choose':
                menu(update['message']['from']['id'])
            elif message == '/Update':
                with open(f"{update['message']['from']['id']}.txt", 'w') as file:
                    file.write(' ')
            else:
                try:
                    with open(f"{update['message']['from']['id']}.txt", 'r') as file:
                        model = file.readline()
                    #message_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',data={'chat_id': GROUP, 'from_chat_id': update['message']['from']['id'], 'message_id': update['message']['message_id'],}).json()['result']['message_id']
                    initial(update['message']['from']['id'], update['message']['message_id'], update['message']['text'], model)
                    print('yedi')
                except Exception as e:
                    print(e)
                    return
                    #message_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',data={'chat_id': GROUP, 'from_chat_id': update['message']['from']['id'], 'message_id': update['message']['message_id'],}).json()['result']['message_id']
                    initial(update['message']['from']['id'], update['message']['message_id'], update['message']['text'], '/Bing')
    elif 'callback_query' in update and 'data' in update['callback_query']:
        data = update['callback_query']['data']
        if data == 'ChatGPT' or data == 'Bing' or data == 'You' or data == 'HuggingFace':
            options(update['callback_query']['from']['id'], '/' + data, update['callback_query']['message']['message_id'])
        elif data[0] == 'R':
            reply_markup = update['callback_query']['message']['reply_markup']
            if len(update['callback_query']['message']['reply_markup']['inline_keyboard'][1]) >= 5:
                reply_markup['inline_keyboard'][0] = [{'text': 'You have reached the limit 😔', 'callback_data': 'limit'}]
                print(requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': update['callback_query']['from']['id'], 'text': f"{update['callback_query']['message']['text']}", 'message_id': update['callback_query']['message']['message_id'],'reply_markup': json.dumps(reply_markup)}).json())
                return
            for index, button in enumerate(reply_markup['inline_keyboard'][1]):
                if button['text'] == '🙄':
                    button['text'] = f"Draft {index + 1}"
            core(update['callback_query']['from']['id'], update['callback_query']['message']['message_id'], update['callback_query']['message']['reply_to_message']['text'], data.split()[1], len(update['callback_query']['message']['reply_markup']['inline_keyboard'][1]), reply_markup)
        elif data[0] == 'A':
            reply_markup = update['callback_query']['message']['reply_markup']
            for index, button in enumerate(reply_markup['inline_keyboard'][1]):
                if button['text'] == '🙄':
                    button['text'] = f"Draft {index + 1}"
            reply_markup['inline_keyboard'].insert(0, [{'text': "Go back ◀️", 'callback_data': f"B {reply_markup['inline_keyboard'][0][0].get('callback_data')[2:]}"}])
            del reply_markup['inline_keyboard'][1]
            reply_markup['inline_keyboard'].append([{'text': f"Bing AI ❤️‍🔥", 'callback_data': f"O /Bing"},{'text': f"ChatGPT ❤️", 'callback_data': f"O /ChatGPT"},{'text': f"You AI 💘", 'callback_data': f"O /You"},{'text': f"HuggingFace AI 🔥", 'callback_data': f"O /HuggingFace"}])
            reply_markup['inline_keyboard'].append([{'text': f"Bing AI ❤️‍🔥", 'callback_data': f"O /Bing"},{'text': f"ChatGPT ❤️", 'callback_data': f"O /ChatGPT"},{'text': f"You AI 💘", 'callback_data': f"O /You"},{'text': f"HuggingFace AI 🔥", 'callback_data': f"O /HuggingFace"}])
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': update['callback_query']['from']['id'], 'text': "Choose one. I will send you the response.", 'message_id': update['callback_query']['message']['message_id'],'reply_markup': reply_markup})
        elif data[0] == 'O':
            #reply_markup = update['callback_query']['message']['reply_markup']
            reply_markup = {'inline_keyboard': [[{'text': f"Regenerate ♻️", 'callback_data': f"R {update['callback_query']['message']['reply_markup']['inline_keyboard'][0][0].get('callback_data')[2:]}"},{'text': "Try different AI ⏭", 'callback_data': f"A {update['callback_query']['message']['reply_markup']['inline_keyboard'][0][0].get('callback_data')[2:]}"}],update['callback_query']['message']['reply_markup']['inline_keyboard'][1]]}
            if len(update['callback_query']['message']['reply_markup']['inline_keyboard'][1]) >= 5:
                reply_markup['inline_keyboard'][0] = [{'text': 'You have reached the limit 😔', 'callback_data': 'limit'}]
                print(requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': update['callback_query']['from']['id'], 'text': f"{update['callback_query']['message']['text']}", 'message_id': update['callback_query']['message']['message_id'],'reply_markup': json.dumps(reply_markup)}).json())
                #gotta do something
                return
            for index, button in enumerate(reply_markup['inline_keyboard'][1]):
                if button['text'] == '🙄':
                    button['text'] = f"Draft {index + 1}"
            core(update['callback_query']['from']['id'], update['callback_query']['message']['message_id'], update['callback_query']['message']['reply_to_message']['text'], data.split()[1], len(update['callback_query']['message']['reply_markup']['inline_keyboard'][1]), reply_markup)
        elif data[0] == 'C':
            reply_markup = {'inline_keyboard': [[{'text': f"Regenerate ♻️", 'callback_data': f'R {data[2:]}'},{'text': "Try different AI ⏭", 'callback_data': f"A {data[2:]}"}],update['callback_query']['message']['reply_markup']['inline_keyboard'][1]]}
            print(requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': update['callback_query']['from']['id'],'text': f"{update['callback_query']['message']['text']}\n\nCanceled successfully!",'message_id': update['callback_query']['message']['message_id'],'reply_markup': json.dumps(reply_markup)}).json())
        elif data[0] == 'B':
            reply_markup = {'inline_keyboard': [[{'text': f"Regenerate ♻️", 'callback_data': f'R {data[2:]}'},{'text': "Try different AI ⏭", 'callback_data': f"A {data[2:]}"}],update['callback_query']['message']['reply_markup']['inline_keyboard'][1]]}
            print(requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': update['callback_query']['from']['id'],'text': "Here you can see old drafts or generate more.",'message_id': update['callback_query']['message']['message_id'],'reply_markup': json.dumps(reply_markup)}).json())
        elif data[0] == 'D':
            reply_markup = update['callback_query']['message']['reply_markup']
            for index, button in enumerate(reply_markup['inline_keyboard'][1]):
                if button['text'] == '🙄':
                    button['text'] = f"Draft {index + 1}"
            reply_markup['inline_keyboard'][1][int(data.split()[2]) - 1]['text'] = '🙄'
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',data={'chat_id': update['callback_query']['from']['id'], 'from_chat_id': GROUP,'message_id': int(data.split()[1]), 'reply_markup': json.dumps(reply_markup), 'reply_to_message_id': update['callback_query']['message']['reply_to_message']['message_id']})
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage",json={'chat_id': update['callback_query']['from']['id'],'message_id': update['callback_query']['message']['message_id']})
        elif data == 'limit':
            params = {'chat_id': update['callback_query']['from']['id'],'message_id': update['callback_query']['message']['message_id'],'is_big': True,'reaction': json.dumps([{'type': 'emoji', 'emoji': '😢'}])}
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction', params=params).json()
            pass
def menu(user_id):
    reply_markup = {'inline_keyboard': [
        [{'text': f"Bing AI ❤️‍🔥", 'callback_data': f"Bing"}, {'text': f"ChatGPT ❤️", 'callback_data': f"ChatGPT"}],
        [{'text': f"You AI 💘", 'callback_data': f"You"}, {'text': f"HuggingFace AI 🔥", 'callback_data': f"HuggingFace"}],
        [{'text': f"You AI 🤩", 'callback_data': f"You"}, {'text': f"HuggingFace AI 😍", 'callback_data': f"HuggingFace"}],
        [{'text': f"You AI 🕊", 'callback_data': f"You"}, {'text': f"HuggingFace AI ⚡️", 'callback_data': f"HuggingFace"}]
    ]}
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',params={'chat_id': user_id, 'text': f"*Choose one:*",'parse_mode': 'Markdown', 'reply_markup': json.dumps(reply_markup)})
    return
def initial(user_id, message_id, query, mode):
    print(mode)
    is_auth = False
    if mode == '/ChatGPT':
        model = 'gpt-3.5-turbo'
        provider = g4f.Provider.Liaobots
    elif mode == '/Bing':
        model = 'gpt-4-32k-0613'
        provider = g4f.Provider.Bing
    elif mode == '/You':
        model = 'gpt-3.5-turbo'
        provider = g4f.Provider.You
    elif mode == '/HuggingFace':
        is_auth = True
        auth = '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'
        model = 'openchat/openchat-3.5-0106' #many models are out there check out https://huggingface.co/chat
        provider = g4f.Provider.HuggingChat
    if is_auth:
        response = g4f.ChatCompletion.create(
            auth=auth,
            model=model,
            provider=provider,
            messages=[{'role': 'user', 'content': query}],
            stream=True,
        )
    else:
        response = g4f.ChatCompletion.create(
            model=model,
            provider=provider,
            messages=[{'role': 'user', 'content': query}],
            stream=True,
        )
    output = ""
    #if state == ' ':
    reply_markup = {'inline_keyboard': [[{'text': "Cancel 🤚", 'callback_data': f"C {mode}"}]]}
    edit_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',json={'chat_id': user_id, 'text': f'*✅ {mode[1:]} AI* _is generating..._','reply_markup': reply_markup, 'parse_mode': 'Markdown', 'reply_to_message_id': message_id}).json()['result']['message_id']
    #else:
        #regenerate_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',data={'chat_id': GROUP, 'from_chat_id': user_id, 'message_id': eteabt,}).json()['result']['message_id']
        #reply_markup = {'inline_keyboard': [[{'text': f"Regenerate ♻️", 'callback_data': f'R {query}'},{'text': f"Alter AI 〽️", 'callback_data': 'Change'}], [{'text': f"Previous ⏮", 'callback_data': f'P {state}'}]]}
    start = time.time()
    print('kelli')
    for message in response:
        output += message
        if time.time() - start > 2:
            print(requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText', json={'chat_id': user_id,'text': f'{output}', 'message_id': edit_id,'reply_markup': reply_markup}).json())
            start += 2
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': user_id, 'text': output, 'message_id': edit_id,'reply_markup': reply_markup})
    copy_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',data={'chat_id': GROUP, 'from_chat_id': user_id, 'message_id': edit_id}).json()['result']['message_id']
    reply_markup = {'inline_keyboard': [[{'text': f"Regenerate ♻️", 'callback_data': f'R {mode}'},{'text': "Try different AI ⏭", 'callback_data': f"A {mode}"}], [{'text': f"Draft 1", 'callback_data': f'D {copy_id} 1'}]]}
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': user_id, 'text': f'{output}\n\nHere is your ad!', 'message_id': edit_id,'reply_markup': reply_markup})
    return

def core(user_id, message_id, query, mode, number, reply_markup): #number can be obtained by iterating update['callback_query']['message']['reply_markup']['inline_keyboard'][1]
    is_auth = False
    print(mode)
    if mode == '/ChatGPT':
        model = 'gpt-3.5-turbo'
        provider = g4f.Provider.Liaobots
    elif mode == '/Bing':
        model = 'gpt-4-32k-0613'
        provider = g4f.Provider.Bing
    elif mode == '/You':
        model = 'gpt-3.5-turbo'
        provider = g4f.Provider.You
    elif mode == '/HuggingFace':
        is_auth = True
        auth = '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'
        model = 'openchat/openchat-3.5-0106' #many models are out there check out https://huggingface.co/chat
        provider = g4f.Provider.HuggingChat
    if is_auth:
        response = g4f.ChatCompletion.create(
            auth=auth,
            model=model,
            provider=provider,
            messages=[{'role': 'user', 'content': query}],
            stream=True,
        )
    else:
        response = g4f.ChatCompletion.create(
            model=model,
            provider=provider,
            messages=[{'role': 'user', 'content': query}],
            stream=True,
        )
    output = ""
    reply_markup['inline_keyboard'][0] = [{'text': "Cancel 🤚", 'callback_data': f"C {mode}"}]
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': user_id, 'text': f'*✅ {mode[1:]} AI* _is generating..._', 'message_id': message_id, 'reply_markup': reply_markup, 'parse_mode': 'Markdown'})
    start = time.time()
    for message in response:
        output += message
        if time.time() - start > 2:
            print(requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText', json={'chat_id': user_id,'text': f'{output}', 'message_id': message_id,'reply_markup': reply_markup}).json())
            start += 2
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': user_id, 'text': output, 'message_id': message_id,'reply_markup': reply_markup})
    copy_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',data={'chat_id': GROUP, 'from_chat_id': user_id, 'message_id': message_id}).json()['result']['message_id']
    reply_markup['inline_keyboard'][1].append({'text': f"Draft {number + 1}", 'callback_data': f'D {copy_id} {number + 1}'})
    reply_markup['inline_keyboard'][0] = [{'text': f"Regenerate ♻️", 'callback_data': f'R {mode}'},{'text': "Try different AI ⏭", 'callback_data': f"A {mode}"}]
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': user_id, 'text': f'{output}\n\nHere is your ad!', 'message_id': message_id,'reply_markup': reply_markup})
    return


def options(user_id, data, message_id):
    reaction = {
        "/ChatGPT": "❤️",
        "/Bing": "❤️‍🔥",
        "/You": "💘",
        "/HuggingFace": "🔥",
    }
    with open(f"{user_id}.txt", 'w') as file:
        file.write(data)
    reply_markup = {'inline_keyboard': [
        [{'text': f"Bing AI ❤️‍🔥", 'callback_data': f"Bing"}, {'text': f"ChatGPT ❤️", 'callback_data': f"ChatGPT"}],
        [{'text': f"You AI 💘", 'callback_data': f"You"}, {'text': f"HuggingFace AI 🔥", 'callback_data': f"HuggingFace"}],
        [{'text': f"You AI 🤩", 'callback_data': f"You"}, {'text': f"HuggingFace AI 😍", 'callback_data': f"HuggingFace"}],
        [{'text': f"You AI 🕊", 'callback_data': f"You"}, {'text': f"HuggingFace AI ⚡️", 'callback_data': f"HuggingFace"}]]}
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',params={'chat_id': user_id,'message_id': message_id,'text': f"_You are using_ *{data[1:]} AI*", 'parse_mode': 'Markdown','reply_markup': json.dumps(reply_markup)}).json()
    params = {'chat_id': user_id,'message_id': message_id, 'is_big': True,'reaction': json.dumps([{'type': 'emoji', 'emoji': f"{reaction.get(data)}"}])}
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction', params=params).json()

def send_users():
    with open('users.txt', 'r') as file:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",params={'chat_id': ADMIN},files={'document': ('Users.txt', io.StringIO(''.join(file.readlines())))})
    file.close()
    return

if __name__ == '__main__':
    app.run(debug=False)

import io
import g4f
import time
import json
import requests
import assemblyai as aai
from flask import Flask, request
import google.generativeai as genai

#global last_update_id
BOT_TOKEN = '6949099878:AAFLahQxI31DjKTlmWR_usBYtYHv40czRxk'
ADMIN = 5934725286
GROUP = -4099666754
MODELS = [{'name': 'Gemini', 'description': 'simple google product', 'instruction': 'be a helpful assistant'},
          {'name': 'ChatGPT', 'description': 'simple openai product', 'instruction': 'be a helpful assistant',
           'model': 'meta-llama/Llama-2-70b-chat-hf', 'provider': g4f.Provider.DeepInfra},
          {'name': 'Llama', 'description': 'simple meta product', 'instruction': 'be a helpful assistant',
           'model': 'meta-llama/Llama-2-70b-chat-hf', 'provider': g4f.Provider.DeepInfra},
          {'name': 'Komiljon', 'description': 'Perfect human', 'instruction': 'You are a real human. Your name is Komiljon. You are 18. You are majoring at Cyber Security in New Uzbekistan University. You know only English and Uzbek, so if anyone asks anything in any other language, tell that you can only communicate in English and Uzbek. Never say I do not know, if you do not know the question asked just made the asnwer up as a real human described above. Assume that you are chatting with the user, So you are not an assistant. Do not share anything personaly untill it is referred.',
           'model': 'meta-llama/Llama-2-70b-chat-hf', 'provider': g4f.Provider.DeepInfra}
          ]
MODEL = ['Gemini', 'ChatGPT', 'Llama', 'Komiljon']
REACTIONS = {'Gemini': '⚡️', 'ChatGPT': '🔥', 'Llama': '🏆', 'Komiljon': '🫡'}

app = Flask(__name__)
genai.configure(api_key='AIzaSyA0qzyz3SZmjcfwD-FHhRQLZZHL5o0LQO0')
aai.settings.api_key = "cc59032b0a284ef3a7071106a7be9885"


@app.route('/', methods=['POST'])
def handle_webhook():
    try:
        process(json.loads(request.get_data()))
        return 'Success!'
    except Exception as e:
        print(e)
        return 'Error'


def random():
    global last_update_id
    last_update_id = -1
    while True:
        updates = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id}").json().get('result', [])
        for update in updates:
            process(update)
            last_update_id = update['update_id'] + 1


def process(update):
    if 'message' in update:
        if 'text' in update['message']:
            message = update['message']['text']
            if message == '/start':
                if not any(str(update['message']['from']['id']) in line.split()[0] for line in open('users.txt')):
                    with open('users.txt', 'a') as file:
                        file.write(f"{update['message']['from']['id']} {update['message']['from']['first_name'].split()[0]}\n")
                    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",data={'chat_id': update['message']['from']['id'],'text': f"✅ Hello <a href='tg://user?id={update['message']['from']['id']}'>{update['message']['from']['first_name']}</a> !",'parse_mode': 'HTML'})
                    alert(update['message']['from'])
                with open(f"{update['message']['from']['id']}.txt", 'w') as file:
                    file.write(MODELS[0]['name'])
                menu(update['message']['from']['id'], False)
            elif message == '/new_chat':
                menu(update['message']['from']['id'], True)
            elif message == '/INITIALIZE' and update['message']['from']['id'] == ADMIN:
                initialize()
            elif message == '/USERS' and update['message']['from']['id'] == ADMIN:
                send_users()
            else:
                try:
                    model = open(f"{update['message']['from']['id']}.txt", 'r').read()
                except:
                    model = MODELS[0]['name']
                reply_markup = {'inline_keyboard': [[{'text': "Delete ❌", 'callback_data': f"delete"}]]}
                edit_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                                        json={'chat_id': update['message']['from']['id'],
                                              'text': f'*✅ {model}* _is generating..._', 'reply_markup': reply_markup,
                                              'parse_mode': 'Markdown',
                                              'reply_to_message_id': update['message']['message_id']}).json()['result'][
                    'message_id']
                initial(update['message']['from']['id'], update['message']['text'], model, edit_id)
        elif 'voice' in update['message']:
            try:
                model = open(f"{update['message']['from']['id']}.txt", 'r').read()
            except:
                model = MODELS[0]['name']
            try:
                reply_markup = {'inline_keyboard': [[{'text': "Delete ❌", 'callback_data': f"delete"}]]}
                edit_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                                        json={'chat_id': update['message']['from']['id'],
                                              'text': f"🧏🏻‍♂️ _Your voice is being processed_",
                                              'reply_markup': reply_markup, 'parse_mode': 'Markdown',
                                              'reply_to_message_id': update['message']['message_id']}).json()['result'][
                    'message_id']
                initial(update['message']['from']['id'], stt(
                    requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile',
                                 params={'file_id': update['message']['voice']['file_id']}).json()['result'][
                        'file_path']), model, edit_id, )
            except Exception as e:
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',
                              json={'chat_id': update['message']['from']['id'], 'message_id': edit_id,
                                    'text': f'_Sorry, I could not catch you_', 'parse_mode': 'Markdown',
                                   'reply_to_message_id': update['message']['message_id']})
        elif 'pinned_message' in update['message']:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage",json={'chat_id': update['message']['chat']['id'], 'message_id': update['message']['message_id']})
    elif 'callback_query' in update and 'data' in update['callback_query']:
        data = update['callback_query']['data']
        if data in MODEL:
            options(update['callback_query']['from']['id'], data, update['callback_query']['message']['message_id'])
        elif data[0] == 'R':
            reply_markup = update['callback_query']['message']['reply_markup']
            if len(update['callback_query']['message']['reply_markup']['inline_keyboard'][1]) >= 5:
                reply_markup['inline_keyboard'][0] = [
                    {'text': 'You have reached the limit 😔', 'callback_data': 'limit'}]
                print(requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageReplyMarkup',
                                    json={'chat_id': update['callback_query']['from']['id'],
                                          'message_id': update['callback_query']['message']['message_id'],
                                          'reply_markup': json.dumps(reply_markup)}).json())
                return
            for index, button in enumerate(reply_markup['inline_keyboard'][1]):
                if button['text'] == '🙄':
                    button['text'] = f"Draft {index + 1}"
            if 'voice' in update['callback_query']['message']['reply_to_message']:
                reply_markup['inline_keyboard'][0] = [{'text': "Delete ❌", 'callback_data': f"delete"}]
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',
                              json={'chat_id': update['callback_query']['from']['id'],
                                    'text': f"🧏🏻‍♂️ _Your voice is being processed_",
                                    'message_id': update['callback_query']['message']['message_id'],
                                    'parse_mode': 'Markdown', 'reply_markup': json.dumps(reply_markup)}).json()
                core(update['callback_query']['from']['id'], update['callback_query']['message']['message_id'], stt(
                    requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile', params={
                        'file_id': update['callback_query']['message']['reply_to_message']['voice']['file_id']}).json()[
                        'result']['file_path']), data.split()[1],
                     len(update['callback_query']['message']['reply_markup']['inline_keyboard'][1]), reply_markup)
            elif 'text' in update['callback_query']['message']['reply_to_message']:
                core(update['callback_query']['from']['id'], update['callback_query']['message']['message_id'],
                     update['callback_query']['message']['reply_to_message']['text'], data.split()[1],
                     len(update['callback_query']['message']['reply_markup']['inline_keyboard'][1]), reply_markup)
        elif data[0] == 'D':
            reply_markup = update['callback_query']['message']['reply_markup']
            for index, button in enumerate(reply_markup['inline_keyboard'][1]):
                if button['text'] == '🙄':
                    button['text'] = f"Draft {index + 1}"
            reply_markup['inline_keyboard'][1][int(data.split()[2]) - 1]['text'] = '🙄'
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',
                          data={'chat_id': update['callback_query']['from']['id'], 'from_chat_id': GROUP,
                                'message_id': int(data.split()[1]), 'reply_markup': json.dumps(reply_markup),
                                'reply_to_message_id': update['callback_query']['message']['reply_to_message'][
                                    'message_id']})
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage",
                          json={'chat_id': update['callback_query']['from']['id'],
                                'message_id': update['callback_query']['message']['message_id']})
        elif data == 'limit':
            params = {'chat_id': update['callback_query']['from']['id'],
                      'message_id': update['callback_query']['message']['message_id'], 'is_big': True,
                      'reaction': json.dumps([{'type': 'emoji', 'emoji': '😢'}])}
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction', params=params).json()
        elif data == 'delete':
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage",
                          json={'chat_id': update['callback_query']['from']['id'],
                                'message_id': update['callback_query']['message']['message_id']})


def menu(user_id, unpin):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendChatAction",json={'chat_id': user_id, 'action': 'choose_sticker'})
    reply_markup = {'inline_keyboard': []}
    if len(MODEL) % 2 == 0:
        for i in range(0, len(MODEL), 2):
            reply_markup['inline_keyboard'].append([{'text': f"{MODEL[i]}", 'callback_data': f"{MODEL[i]}"},
                                                    {'text': f"{MODEL[i + 1]}", 'callback_data': f"{MODEL[i + 1]}"}])
    else:
        for i in range(0, len(MODEL) - 1, 2):
            reply_markup['inline_keyboard'].append([{'text': f"{MODEL[i]}", 'callback_data': f"{MODEL[i]}"},
                                                    {'text': f"{MODEL[i + 1]}", 'callback_data': f"{MODEL[i + 1]}"}])
        reply_markup['inline_keyboard'].append([{'text': f"{MODEL[-1]}", 'callback_data': f"{MODEL[-1]}"}])
    message_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                               params={'chat_id': user_id, 'text': f"*Choose your default AI assistant:*",
                                       'parse_mode': 'Markdown', 'reply_markup': json.dumps(reply_markup)}).json()[
        'result']['message_id']
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction',
                  params={'chat_id': user_id, 'message_id': message_id, 'is_big': True,
                          'reaction': json.dumps([{'type': 'emoji', 'emoji': f"🙏"}])})
    if unpin:
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/unpinAllChatMessages',params={'chat_id': user_id})
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/pinChatMessage', params={'chat_id': user_id, 'message_id': message_id}).json()

def options(user_id, data, message_id):
    with open(f"{user_id}.txt", 'w') as file:
        file.write(data)
    reply_markup = {'inline_keyboard': []}
    if len(MODEL) % 2 == 0:
        for i in range(0, len(MODEL), 2):
            if data == MODEL[i]:
                reply_markup['inline_keyboard'].append(
                    [{'text': f"{MODEL[i]} {REACTIONS[MODEL[i]]}", 'callback_data': f"{MODEL[i]}"},
                     {'text': f"{MODEL[i + 1]}",
                      'callback_data': f"{MODEL[i + 1]}"}])
            elif data == MODEL[i + 1]:
                reply_markup['inline_keyboard'].append([{'text': f"{MODEL[i]}", 'callback_data': f"{MODEL[i]}"},
                                                        {'text': f"{MODEL[i + 1]} {REACTIONS[MODEL[i + 1]]}",
                                                         'callback_data': f"{MODEL[i + 1]}"}])
            else:
                reply_markup['inline_keyboard'].append([{'text': f"{MODEL[i]}", 'callback_data': f"{MODEL[i]}"},
                                                        {'text': f"{MODEL[i + 1]}",
                                                         'callback_data': f"{MODEL[i + 1]}"}])
    else:
        for i in range(0, len(MODEL) - 1, 2):
            if data == MODEL[i]:
                reply_markup['inline_keyboard'].append(
                    [{'text': f"{MODEL[i]} {REACTIONS[MODEL[i]]}", 'callback_data': f"{MODEL[i]}"},
                     {'text': f"{MODEL[i + 1]}",
                      'callback_data': f"{MODEL[i + 1]}"}])
            elif data == MODEL[i + 1]:
                reply_markup['inline_keyboard'].append([{'text': f"{MODEL[i]}", 'callback_data': f"{MODEL[i]}"},
                                                        {'text': f"{MODEL[i + 1]} {REACTIONS[MODEL[i + 1]]}",
                                                         'callback_data': f"{MODEL[i + 1]}"}])
            else:
                reply_markup['inline_keyboard'].append([{'text': f"{MODEL[i]}", 'callback_data': f"{MODEL[i]}"},
                                                        {'text': f"{MODEL[i + 1]}",
                                                         'callback_data': f"{MODEL[i + 1]}"}])
        if data == MODEL[-1]:
            reply_markup['inline_keyboard'].append([{'text': f"{MODEL[-1]} {REACTIONS[MODEL[-1]]}", 'callback_data': f"{MODEL[-1]}"}])
        else:
            reply_markup['inline_keyboard'].append([{'text': f"{MODEL[-1]}", 'callback_data': f"{MODEL[-1]}"}])
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': user_id,'message_id': message_id, 'text': f'*You are chatting with* _{data}_','reply_markup': json.dumps(reply_markup), 'parse_mode': 'Markdown'})
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction',params={'chat_id': user_id, 'message_id': message_id, 'is_big': True,'reaction': json.dumps([{'type': 'emoji', 'emoji': REACTIONS[data]}])})


def initial(user_id, query, mode, edit_id):
    if mode == 'Gemini':
        response = genai.GenerativeModel('gemini-pro').generate_content(query).text
    else:
        for item in MODELS:
            if item['name'] == mode:
                response = g4f.ChatCompletion.create(
                    model=item['model'],
                    provider=item['provider'],
                    messages=[{'role': 'user', 'content': query}, {'role': 'system', 'content': item['instruction']}],
                    stream=True,
                )
                break
    output = ""
    start = time.time()
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendChatAction",
                  json={'chat_id': user_id, 'action': 'typing'})
    for message in response:
        output += message
        if time.time() - start > 2:
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',
                          json={'chat_id': user_id, 'text': f'{output}', 'parse_mode': 'Markdown',
                                'message_id': edit_id, 'reply_markup': {
                                  'inline_keyboard': [[{'text': "Delete ❌", 'callback_data': f"delete"}]]}})
            start += 2
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',
                  json={'chat_id': user_id, 'text': output, 'parse_mode': 'Markdown', 'message_id': edit_id,
                        'reply_markup': {'inline_keyboard': [[{'text': "Delete ❌", 'callback_data': f"delete"}]]}})
    copy_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',
                            data={'chat_id': GROUP, 'from_chat_id': user_id, 'message_id': edit_id}).json()['result'][
        'message_id']
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',
                  json={'chat_id': user_id, 'text': f'{output}\n\n_This place is reserved for your ad!_', 'message_id': edit_id,
                        'reply_markup': {'inline_keyboard': [[{'text': f"Regenerate ♻️", 'callback_data': f'R {mode}'},
                                                              {'text': "Delete ❌", 'callback_data': f"delete"}], [
                                                                 {'text': f"Draft 1",
                                                                  'callback_data': f'D {copy_id} 1'}]]},
                        'parse_mode': 'Markdown'})


def core(user_id, message_id, query, mode, number,
         reply_markup, ):  # number can be obtained by iterating update['callback_query']['message']['reply_markup']['inline_keyboard'][1]
    if mode == 'Gemini':
        response = genai.GenerativeModel('gemini-pro').generate_content(query).text
    else:
        for item in MODELS:
            if item['name'] == mode:
                response = g4f.ChatCompletion.create(
                    model=item['model'],
                    provider=item['provider'],
                    messages=[{'role': 'user', 'content': query}, {'role': 'system', 'content': item['instruction']}],
                    stream=True,
                )
                break
    output = ""
    start = time.time()
    print(requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendChatAction",
                        json={'chat_id': user_id, 'action': 'typing'}))
    reply_markup['inline_keyboard'][0] = [{'text': "Delete ❌", 'callback_data': f"delete"}]
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',
                  json={'chat_id': user_id, 'text': f'*✅ {mode}* _is generating..._', 'message_id': message_id,
                        'reply_markup': reply_markup, 'parse_mode': 'Markdown'})
    for message in response:
        output += message
        if time.time() - start > 2:
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',
                          json={'chat_id': user_id, 'text': f'{output}', 'message_id': message_id,
                                'reply_markup': reply_markup}).json()
            start += 2
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',
                  json={'chat_id': user_id, 'text': output, 'message_id': message_id, 'reply_markup': reply_markup})
    copy_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',
                            data={'chat_id': GROUP, 'from_chat_id': user_id, 'message_id': message_id}).json()[
        'result']['message_id']
    reply_markup['inline_keyboard'][1].append(
        {'text': f"Draft {number + 1}", 'callback_data': f'D {copy_id} {number + 1}'})
    reply_markup['inline_keyboard'][0] = [{'text': f"Regenerate ♻️", 'callback_data': f'R {mode}'},
                                          {'text': "Delete ❌", 'callback_data': f"delete"}]
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',
                  json={'chat_id': user_id, 'text': f'{output}\n\n_This place is reserved for your ad!_',
                        'message_id': message_id, 'reply_markup': reply_markup, 'parse_mode': 'Markdown'})


def image(user_id, message_id, query, format):
    payload = {
        "chat_id": user_id,
        "message_to_reply_id": message_id,
        "tetx": "*👨‍💻 This function will be available soon!*",
        "parse_mode": "Markdown"
    }
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload)
    return
    headers = {"Authorization": f"Bearer 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"}
    media = []
    for i in range(4):
        response = requests.post(GENERATION[i], headers=headers, json={"inputs": query})
        time.sleep(10)
        with open('nano.jpeg', 'wb') as file:
            file.write(response.content)
        with open('nano.jpeg', 'rb') as photo_file:
            try:
                media.append({"type": 'photo', "media":
                    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', data={'chat_id': user_id},
                                  files={'photo': photo_file}).json()['result']['photo'][0]['file_id']})
            except:
                continue
    reply_markup = {'inline_keyboard': [
        [{'text': f"Neus AI ❤️‍🔥", 'callback_data': f"Neus"}, {'text': f"ChatGPT ❤️", 'callback_data': f"ChatGPT"}],
        [{'text': f"Mistral AI 💘", 'callback_data': f"Mistral"},
         {'text': f"HuggingFace AI 🔥", 'callback_data': f"HuggingFace"}],
        [{'text': f"Llama AI 🤩", 'callback_data': f"Llama"}],
        [{'text': f"Image Generator 👨‍💻", 'callback_data': f"IG"},
         {'text': f"Image Enhancer 🫡", 'callback_data': f"IE"}]
    ]}
    payload = {
        'chat_id': user_id,
        'message_id': message_id,
        'media': media,
        'quote': '*hello*',
        'quote_parse_mode': 'Markdown',
        "reply_markup": json.dumps(reply_markup)
    }
    edit_id = \
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup", json=payload).json()['result'][0][
            'message_id']
    print(edit_id)
    payload = {
        "chat_id": user_id,
        "message_id": edit_id,
        'media': media,
        "reply_markup": json.dumps(reply_markup)
    }
    print(requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageReplyMarkup", json=payload).json())


def enhancer(user_id, message_id, query, format):
    payload = {
        "chat_id": user_id,
        "message_to_reply_id": message_id,
        "text": "*👨‍💻 This function will be available soon!*",
        "parse_mode": "Markdown"
    }
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload)


def stt(file_url):
    return aai.Transcriber().transcribe(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_url}").text


def send_users():
    with open('users.txt', 'r') as file:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", params={'chat_id': ADMIN},
                      files={'document': ('Users.txt', io.StringIO(''.join(file.readlines())))})
    file.close()


def initialize():
    with open('users.txt', 'r') as file:
        for line in file.readlines():
            with open(f'{line.split()[0]}.txt', 'w') as f:
                f.write(' ')


def alert(user):
    params = {
        'chat_id': ADMIN,
        'text': "<strong>NEW MEMBER!!!\n</strong>" + json.dumps(user),
        'parse_mode': 'HTML',
    }
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', params=params)


#if __name__ == '__main__':
#    random()

if __name__ == '__main__':
    app.run(debug=False)

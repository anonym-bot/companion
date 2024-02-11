import io
import os
import g4f
import time
import json
import requests
from gtts import gTTS
from flask import Flask, request
import assemblyai as aai


BOT_TOKEN = '6949099878:AAFLahQxI31DjKTlmWR_usBYtYHv40czRxk'
ADMIN = 5934725286
GROUP = -4099666754
GENERATION = ["https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.", "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5", "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4", "https://api-inference.huggingface.co/models/prompthero/openjourney"]

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
                    keyboard(update['message']['from']['id'], f"✅ Hello <a href='tg://user?id={update['message']['from']['id']}'>{update['message']['from']['first_name']}</a> !")
                with open(f"{update['message']['from']['id']}.txt", 'w') as file:
                    file.write('/Neus T')
                menu(update['message']['from']['id'])
                delivery_type(update['message']['from']['id'])
            elif message == '/choose':
                menu(update['message']['from']['id'])
            elif message == '/preference':
                delivery_type(update['message']['from']['id'])
            elif message == '/INITIALIZE' and update['message']['from']['id'] == ADMIN:
                initialize()
            elif message == '/USERS' and update['message']['from']['id'] == ADMIN:
                send_users()
            else:
                with open(f"{update['message']['from']['id']}.txt", 'r') as file:
                    a = file.readline()
                    model = a.split()[0]
                    format = a.split()[1]
                if model == 'IG':
                    image(update['message']['from']['id'], update['message']['message_id'], update['message']['text'], format)
                elif model == 'IE':
                    enhancer(update['message']['from']['id'], update['message']['message_id'], update['message']['text'], format)
                elif model[0] == '/':
                    reply_markup = {'inline_keyboard': [[{'text': "Cancel 🤚", 'callback_data': f"c {model}"}]]}
                    edit_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',json={'chat_id': update['message']['from']['id'], 'text': f'*✅ {model[1:]} AI* _is generating..._','reply_markup': reply_markup, 'parse_mode': 'Markdown','reply_to_message_id': update['message']['message_id']}).json()['result']['message_id']
                    initial(update['message']['from']['id'], update['message']['text'], model, edit_id, format)
                    pass
        elif 'voice' in update['message']:
            try:
                with open(f"{update['message']['from']['id']}.txt", 'r') as file:
                    a = file.readline()
                    model = a.split()[0]
                    format = a.split()[1]
                aai.settings.api_key = "cc59032b0a284ef3a7071106a7be9885"
                reply_markup = {'inline_keyboard': [[{'text': "Cancel 🤚", 'callback_data': f"c {model}"}]]}
                file_url = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile', params={'file_id': update['message']['voice']['file_id']}).json()['result']['file_path']
                edit_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',json={'chat_id': update['message']['from']['id'],'text': f"🧏🏻‍♂️ _Your voice is being processed_",'reply_markup': reply_markup, 'parse_mode': 'Markdown','reply_to_message_id': update['message']['message_id']}).json()['result']['message_id']
                transcript = aai.Transcriber().transcribe(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_url}").text
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': update['message']['from']['id'],'message_id': edit_id,'text': f'*✅ {model[1:]} AI* _is generating..._','reply_markup': reply_markup, 'parse_mode': 'Markdown','reply_to_message_id': update['message']['message_id']})
                initial(update['message']['from']['id'], transcript, model, edit_id, format)
            except:
                print('yemadi')
                return
    elif 'callback_query' in update and 'data' in update['callback_query']:
        data = update['callback_query']['data']
        if data == 'ChatGPT' or data == 'Neus' or data == 'Mistral' or data == 'HuggingFace' or data == 'Llama':
            options(update['callback_query']['from']['id'], '/' + data, update['callback_query']['message']['message_id'])
        elif data == 'IG' or data == 'IE':
            options(update['callback_query']['from']['id'], data, update['callback_query']['message']['message_id'])
        elif data[0] == 'R':
            reply_markup = update['callback_query']['message']['reply_markup']
            if len(update['callback_query']['message']['reply_markup']['inline_keyboard'][1]) >= 5:
                reply_markup['inline_keyboard'][0] = [{'text': 'You have reached the limit 😔', 'callback_data': 'limit'}]
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': update['callback_query']['from']['id'], 'text': f"{update['callback_query']['message']['text']}", 'message_id': update['callback_query']['message']['message_id'],'reply_markup': json.dumps(reply_markup)}).json()
                return
            for index, button in enumerate(reply_markup['inline_keyboard'][1]):
                if button['text'] == '🙄':
                    button['text'] = f"Draft {index + 1}"
            if 'voice' in update['callback_query']['message']['reply_to_message']:
                reply_markup['inline_keyboard'][0] = [{'text': "Cancel 🤚", 'callback_data': f"C {data.split()[1]}"}]
                aai.settings.api_key = "cc59032b0a284ef3a7071106a7be9885"
                file_url = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile', params={'file_id': update['callback_query']['message']['reply_to_message']['voice']['file_id']}).json()['result']['file_path']
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': update['callback_query']['from']['id'], 'text': f"🧏🏻‍♂️ _Your voice is being processed_", 'message_id': update['callback_query']['message']['message_id'],'parse_mode':'Markdown','reply_markup': json.dumps(reply_markup)}).json()
                transcript = aai.Transcriber().transcribe(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_url}").text
                core(update['callback_query']['from']['id'], update['callback_query']['message']['message_id'], transcript, data.split()[1], len(update['callback_query']['message']['reply_markup']['inline_keyboard'][1]), reply_markup)
            elif 'text' in update['callback_query']['message']['reply_to_message']:
                core(update['callback_query']['from']['id'], update['callback_query']['message']['message_id'], update['callback_query']['message']['reply_to_message']['text'], data.split()[1], len(update['callback_query']['message']['reply_markup']['inline_keyboard'][1]), reply_markup)
        elif data[0] == 'A':
            reply_markup = update['callback_query']['message']['reply_markup']
            for index, button in enumerate(reply_markup['inline_keyboard'][1]):
                if button['text'] == '🙄':
                    button['text'] = f"Draft {index + 1}"
            reply_markup['inline_keyboard'].insert(0, [{'text': "Go back ◀️", 'callback_data': f"B {reply_markup['inline_keyboard'][0][0].get('callback_data')[2:]}"}])
            del reply_markup['inline_keyboard'][1]
            reply_markup['inline_keyboard'].append([{'text': f"Neus AI❤️‍🔥", 'callback_data': f"O /Neus"},{'text': f"ChatGPT ❤️", 'callback_data': f"O /ChatGPT"},{'text': f"Mistral AI 💘", 'callback_data': f"O /Mistral"}])
            reply_markup['inline_keyboard'].append([{'text': f"HuggingFace AI 🔥", 'callback_data': f"O /HuggingFace"}, {'text': f"Llama AI 🤩", 'callback_data': f"O /Llama"}])
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': update['callback_query']['from']['id'], 'text': "Choose one. I will send you the response.", 'message_id': update['callback_query']['message']['message_id'],'reply_markup': reply_markup})
        elif data[0] == 'O':
            reply_markup = {'inline_keyboard': [[{'text': f"Regenerate ♻️", 'callback_data': f"R {update['callback_query']['message']['reply_markup']['inline_keyboard'][0][0].get('callback_data')[2:]}"},{'text': "Try different AI ⏭", 'callback_data': f"A {update['callback_query']['message']['reply_markup']['inline_keyboard'][0][0].get('callback_data')[2:]}"}],update['callback_query']['message']['reply_markup']['inline_keyboard'][1]]}
            if len(update['callback_query']['message']['reply_markup']['inline_keyboard'][1]) >= 5:
                reply_markup['inline_keyboard'][0] = [{'text': 'You have reached the limit 😔', 'callback_data': 'limit'}]
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': update['callback_query']['from']['id'], 'text': f"{update['callback_query']['message']['text']}", 'message_id': update['callback_query']['message']['message_id'],'reply_markup': json.dumps(reply_markup)}).json()
                return
            for index, button in enumerate(reply_markup['inline_keyboard'][1]):
                if button['text'] == '🙄':
                    button['text'] = f"Draft {index + 1}"
            if 'voice' in update['callback_query']['message']['reply_to_message']:
                aai.settings.api_key = "cc59032b0a284ef3a7071106a7be9885"
                file_url = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile', params={'file_id': update['callback_query']['message']['reply_to_message']['voice']['file_id']}).json()['result']['file_path']
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': update['callback_query']['from']['id'], 'text': f"🧏🏻‍♂️ _Your voice is being processed_", 'message_id': update['callback_query']['message']['message_id'],'reply_markup': json.dumps(reply_markup)}).json()
                transcript = aai.Transcriber().transcribe(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_url}").text
                core(update['callback_query']['from']['id'], update['callback_query']['message']['message_id'], transcript, data.split()[1], len(update['callback_query']['message']['reply_markup']['inline_keyboard'][1]), reply_markup)
            elif 'text' in update['callback_query']['message']['reply_to_message']:
                core(update['callback_query']['from']['id'], update['callback_query']['message']['message_id'], update['callback_query']['message']['reply_to_message']['text'], data.split()[1], len(update['callback_query']['message']['reply_markup']['inline_keyboard'][1]), reply_markup)
        elif data[0] == 'C':
            reply_markup = {'inline_keyboard': [[{'text': f"Regenerate ♻️", 'callback_data': f'R {data[2:]}'},{'text': "Try different AI ⏭", 'callback_data': f"A {data[2:]}"}],update['callback_query']['message']['reply_markup']['inline_keyboard'][1]]}
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': update['callback_query']['from']['id'],'text': f"{update['callback_query']['message']['text']}\n\nCanceled successfully!",'message_id': update['callback_query']['message']['message_id'],'reply_markup': json.dumps(reply_markup)}).json()
        elif data[0] == 'c':
            reply_markup = {'inline_keyboard': [[{'text': f"Regenerate ♻️", 'callback_data': f'R {data[2:]}'},{'text': "Try different AI ⏭", 'callback_data': f"A {data[2:]}"}],[{'text': "Delete ❌", 'callback_data': "delete"}]]}
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': update['callback_query']['from']['id'],'text': f"{update['callback_query']['message']['text']}\n\nCanceled successfully!",'message_id': update['callback_query']['message']['message_id'],'reply_markup': json.dumps(reply_markup)}).json()
        elif data[0] == 'B':
            reply_markup = {'inline_keyboard': [[{'text': f"Regenerate ♻️", 'callback_data': f'R {data[2:]}'},{'text': "Try different AI ⏭", 'callback_data': f"A {data[2:]}"}],update['callback_query']['message']['reply_markup']['inline_keyboard'][1]]}
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': update['callback_query']['from']['id'],'text': "Here you can see old drafts or generate more.",'message_id': update['callback_query']['message']['message_id'],'reply_markup': json.dumps(reply_markup)}).json()
        elif data[0] == 'D':
            reply_markup = update['callback_query']['message']['reply_markup']
            for index, button in enumerate(reply_markup['inline_keyboard'][1]):
                if button['text'] == '🙄':
                    button['text'] = f"Draft {index + 1}"
            reply_markup['inline_keyboard'][1][int(data.split()[2]) - 1]['text'] = '🙄'
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',data={'chat_id': update['callback_query']['from']['id'], 'from_chat_id': GROUP,'message_id': int(data.split()[1]), 'reply_markup': json.dumps(reply_markup), 'reply_to_message_id': update['callback_query']['message']['reply_to_message']['message_id']})
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage",json={'chat_id': update['callback_query']['from']['id'],'message_id': update['callback_query']['message']['message_id']})
        elif data[0] == 'T':
            set_delivery(update['callback_query']['from']['id'], data, update['callback_query']['message']['message_id'])
        elif data == 'limit':
            params = {'chat_id': update['callback_query']['from']['id'],'message_id': update['callback_query']['message']['message_id'],'is_big': True,'reaction': json.dumps([{'type': 'emoji', 'emoji': '😢'}])}
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction', params=params).json()
        elif data == 'delete':
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage",json={'chat_id': update['callback_query']['from']['id'],'message_id': update['callback_query']['message']['message_id']})
    return
def menu(user_id):
    reply_markup = {'inline_keyboard': [
        [{'text': f"Neus AI ❤️‍🔥", 'callback_data': f"Neus"}, {'text': f"ChatGPT ❤️", 'callback_data': f"ChatGPT"}],
        [{'text': f"Mistral AI 💘", 'callback_data': f"Mistral"}, {'text': f"HuggingFace AI 🔥", 'callback_data': f"HuggingFace"}],
        [{'text': f"Llama AI 🤩", 'callback_data': f"Llama"}],
        [{'text': f"Image Generator 👨‍💻", 'callback_data': f"IG"}, {'text': f"Image Enhancer 🫡", 'callback_data': f"IE"}]
    ]}
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',params={'chat_id': user_id, 'text': f"*Choose your default AI assistant:*",'parse_mode': 'Markdown', 'reply_markup': json.dumps(reply_markup)})
    return

def delivery_type(user_id):
    reply_markup = {'inline_keyboard': [[{'text': f"Text ❤️", 'callback_data': f"T T"}, {'text': f"Audio ❤️‍🔥", 'callback_data': f"T A"}]]}
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',params={'chat_id': user_id, 'text': f"*Choose information delivery method:*",'parse_mode': 'Markdown', 'reply_markup': json.dumps(reply_markup)})
    return

def initial(user_id, query, mode, edit_id, format):
    print(format)
    is_auth = False
    if mode == '/ChatGPT':
        is_auth = True
        auth = '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'
        model = 'openchat/openchat-3.5-0106'
        provider = g4f.Provider.HuggingChat
    elif mode == '/Neus':
        is_auth = True
        auth = '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'
        model = 'NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO'
        provider = g4f.Provider.HuggingChat
    elif mode == '/Mistral':
        is_auth = True
        auth = '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'
        model = 'mistralai/Mistral-7B-Instruct-v0.2'
        provider = g4f.Provider.HuggingChat
    elif mode == '/HuggingFace':
        is_auth = True
        auth = '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'
        model = 'mistralai/Mixtral-8x7B-Instruct-v0.1' #many models are out there check out https://huggingface.co/chat
        provider = g4f.Provider.HuggingChat
    elif mode == '/Llama':
        is_auth = True
        auth = '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'
        model = 'meta-llama/Llama-2-70b-chat-hf'
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
    if format == 'T':
        reply_markup = {'inline_keyboard': [[{'text': "Cancel 🤚", 'callback_data': f"c {mode}"}]]}
        start = time.time()
        for message in response:
            output += message
            if time.time() - start > 2:
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText', json={'chat_id': user_id,'text': f'{output}', 'message_id': edit_id,'reply_markup': reply_markup}).json()
                start += 2
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': user_id, 'text': output, 'message_id': edit_id,'reply_markup': reply_markup})
        copy_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',data={'chat_id': GROUP, 'from_chat_id': user_id, 'message_id': edit_id}).json()['result']['message_id']
        reply_markup = {'inline_keyboard': [[{'text': f"Regenerate ♻️", 'callback_data': f'R {mode}'},{'text': "Try different AI ⏭", 'callback_data': f"A {mode}"}], [{'text': f"Draft 1", 'callback_data': f'D {copy_id} 1'}]]}
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': user_id, 'text': f'{output}\n\n_Here could be your ad!_', 'message_id': edit_id,'reply_markup': reply_markup, 'parse_mode': 'Markdown'})
        return
    elif format == 'A':
        for message in response:
            output += message
        if tts(output):
            copy_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendVoice', params={'chat_id': GROUP, 'caption': 'Voice message caption'}, files={'voice': open('random.ogg', 'rb')}).json()['result']['message_id']
            reply_markup = {'inline_keyboard': [[{'text': f"Regenerate ♻️", 'callback_data': f'R {mode}'},{'text': "Try different AI ⏭", 'callback_data': f"A {mode}"}],[{'text': f"Draft 1", 'callback_data': f'D {copy_id} 1'}]]}
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendVoice', params={'chat_id': user_id, 'caption': 'Voice message caption', 'reply_markup':reply_markup}, files={'voice': open('random.ogg', 'rb')})
            if os.path.exists('random.ogg'):
                os.remove('random.ogg')
        else:
            print('yemadi')
            #say the limit has reached or we are having problems
            return
    else:
        return

def core(user_id, message_id, query, mode, number, reply_markup): #number can be obtained by iterating update['callback_query']['message']['reply_markup']['inline_keyboard'][1]
    with open(f"{user_id}.txt", 'r') as file:
        format = file.readline().split()[1]
    is_auth = False
    if mode == '/ChatGPT':
        is_auth = True
        auth = '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'
        model = 'openchat/openchat-3.5-0106'
        provider = g4f.Provider.HuggingChat
    elif mode == '/Neus':
        is_auth = True
        auth = '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'
        model = 'NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO'
        provider = g4f.Provider.HuggingChat
    elif mode == '/Mistral':
        is_auth = True
        auth = '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'
        model = 'mistralai/Mistral-7B-Instruct-v0.2'
        provider = g4f.Provider.HuggingChat
    elif mode == '/HuggingFace':
        is_auth = True
        auth = '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'
        model = 'mistralai/Mixtral-8x7B-Instruct-v0.1' #many models are out there check out https://huggingface.co/chat
        provider = g4f.Provider.HuggingChat
    elif mode == '/Llama':
        is_auth = True
        auth = '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'
        model = 'meta-llama/Llama-2-70b-chat-hf'
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
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText', json={'chat_id': user_id,'text': f'{output}', 'message_id': message_id,'reply_markup': reply_markup}).json()
            start += 2
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': user_id, 'text': output, 'message_id': message_id,'reply_markup': reply_markup})
    copy_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',data={'chat_id': GROUP, 'from_chat_id': user_id, 'message_id': message_id}).json()['result']['message_id']
    reply_markup['inline_keyboard'][1].append({'text': f"Draft {number + 1}", 'callback_data': f'D {copy_id} {number + 1}'})
    reply_markup['inline_keyboard'][0] = [{'text': f"Regenerate ♻️", 'callback_data': f'R {mode}'},{'text': "Try different AI ⏭", 'callback_data': f"A {mode}"}]
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': user_id, 'text': f'{output}\n\n_This place is reserved for your ad!_', 'message_id': message_id,'reply_markup': reply_markup, 'parse_mode': 'Markdown'})
    return

def set_delivery(user_id, data, message_id):
    reaction = {
        "T T": "❤️",
        "T A": "❤️‍🔥"
    }
    message = {
        "T T": "a text",
        "T A": "an audio"
    }
    with open(f"{user_id}.txt", 'r') as file:
        model = file.readline().split()[0]
    with open(f"{user_id}.txt", 'w') as file:
        file.write(f"{model} {data.split()[1]}")
    reply_markup = {'inline_keyboard': [[{'text': f"Text ❤️", 'callback_data': f"T T"}, {'text': f"Audio ❤️‍🔥", 'callback_data': f"T A"}]]}
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',params={'chat_id': user_id, 'text': f"*I will send the response as {message.get(data)}*",'parse_mode': 'Markdown', 'reply_markup': json.dumps(reply_markup)})
    params = {'chat_id': user_id,'message_id': message_id, 'is_big': True,'reaction': json.dumps([{'type': 'emoji', 'emoji': f"{reaction.get(data)}"}])}
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction', params=params).json()

def options(user_id, data, message_id):
    reaction = {
        "/ChatGPT": "❤️",
        "/Neus": "❤️‍🔥",
        "/Mistral": "💘",
        "/HuggingFace": "🔥",
        "/Llama": "🤩",
        "IG": "👨‍💻",
        "IE": "🫡"
    }
    with open(f"{user_id}.txt", 'r') as file:
        delivery = file.readline().split()[1]
    with open(f"{user_id}.txt", 'w') as file:
        file.write(f"{data} {delivery}")
    reply_markup = {'inline_keyboard': [
        [{'text': f"Neus AI ❤️‍🔥", 'callback_data': f"Neus"}, {'text': f"ChatGPT ❤️", 'callback_data': f"ChatGPT"}],
        [{'text': f"Mistral AI 💘", 'callback_data': f"Mistral"}, {'text': f"HuggingFace AI 🔥", 'callback_data': f"HuggingFace"}],
        [{'text': f"Llama AI 🤩", 'callback_data': f"Llama"}],
        [{'text': f"Image Generator 👨‍💻", 'callback_data': f"IG"}, {'text': f"Image Enhancer 🫡", 'callback_data': f"IE"}]
    ]}
    option = {
        "IG": 'Image Generation',
        "IE": 'Image Enhancer'
    }
    if data == 'IG' or data == 'IE':
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',params={'chat_id': user_id,'message_id': message_id,'text': f"_Your default AI assistant is set to_ *{option.get(data)}* AI", 'parse_mode': 'Markdown','reply_markup': json.dumps(reply_markup)}).json()
    else:
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',params={'chat_id': user_id,'message_id': message_id,'text': f"_Your default AI assistant is set to_ *{data[1:]} AI*", 'parse_mode': 'Markdown','reply_markup': json.dumps(reply_markup)}).json()
    params = {'chat_id': user_id,'message_id': message_id, 'is_big': True,'reaction': json.dumps([{'type': 'emoji', 'emoji': f"{reaction.get(data)}"}])}
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction', params=params).json()


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
                media.append({"type": 'photo', "media": requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', data={'chat_id': user_id}, files={'photo': photo_file}).json()['result']['photo'][0]['file_id']})
            except:
                continue
    reply_markup = {'inline_keyboard': [
        [{'text': f"Neus AI ❤️‍🔥", 'callback_data': f"Neus"}, {'text': f"ChatGPT ❤️", 'callback_data': f"ChatGPT"}],
        [{'text': f"Mistral AI 💘", 'callback_data': f"Mistral"}, {'text': f"HuggingFace AI 🔥", 'callback_data': f"HuggingFace"}],
        [{'text': f"Llama AI 🤩", 'callback_data': f"Llama"}],
        [{'text': f"Image Generator 👨‍💻", 'callback_data': f"IG"}, {'text': f"Image Enhancer 🫡", 'callback_data': f"IE"}]
    ]}
    payload = {
        'chat_id': user_id,
        'message_id': message_id,
        'media': media,
        'quote': '*hello*',
        'quote_parse_mode': 'Markdown',
        "reply_markup": json.dumps(reply_markup)
    }
    edit_id = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup", json=payload).json()['result'][0]['message_id']
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
        "tetx": "*👨‍💻 This function will be available soon!*",
        "parse_mode": "Markdown"
    }
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload)
    return

def tts(query):
    # Language (ISO 639-1 language code)
    language = 'en'
    tts = gTTS(text=query, lang=language, slow=False)
    tts.save("random.ogg")
    return True
def keyboard(user_id, text):
    data = {
        'chat_id': user_id,
        'text': text,
        'parse_mode' : 'HTML'
    }
    print(requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data).json())
    return

def send_users():
    with open('users.txt', 'r') as file:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",params={'chat_id': ADMIN},files={'document': ('Users.txt', io.StringIO(''.join(file.readlines())))})
    file.close()
    return

def initialize():
    with open('users.txt', 'r') as file:
        for line in file.readlines():
            with open(f'{line.split()[0]}.txt', 'w') as f:
                f.write(' ')
    return

if __name__ == '__main__':
    app.run(debug=False)

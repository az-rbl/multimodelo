import openai

from decouple import config
import gradio as gr

openai.api_key = config('KEY')
from PIL import Image
from io import BytesIO
import requests






def completion(p):
    response = openai.Completion.create(
        model = "text-davinci-003",
        prompt =f"{p}",
        max_tokens=200,
        temperature =0.8
    )
    return p + response.choices[0].text

def chat_completion(words, content):
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": content},
            {"role": "user", "content": words}
        ]
    )
    return str(response.choices[0].message.content)

def dalle(p):
    response = openai.Image.create(
        prompt = p,
        n=1,
        size="512x512"
    )
    
    return response['data'][0]['url']

def voice_text(x):
    audio_file = open(x,"rb")
    transcript = openai.Audio.transcribe("whisper-1",  audio_file)
    print(transcript["text"])
    return transcript["text"]

def multi_model(audio):
    transcript = voice_text(audio)
    words = transcript.split(maxsplit = 1)
    pattern_traduce = r'\b(t{0,1}r{0,1}a{0,1}d{0,1}u{0,1}c{0,1}e{0,1})\b'
    command = words[0].capitalize()
    prompt = words[1]
    
    if 'Completa' == command:
        return [completion(prompt),None]
    if 'Responde' == command:
        return [chat_completion(prompt,"actua como chatbot"),None]
    if 'Dibuja' == command:
        response = requests.get(dalle(prompt))
        image = Image.open(BytesIO(response.content))
        return [prompt,image]
    if 'Traduce' == command:
        sentences =prompt.split(maxsplit=2)
        return [chat_completion(f"Traduce el siguiente texto a {sentences[1]}: {sentences[2]}","actua como traductor"),None]
    else:
        return["No reconocí el comando, intenta de nuevo", None]
    
if __name__=='__main__':
    output_text = gr.outputs.Textbox()
    output_image = gr.outputs.Image(type='pil')

    demo = gr.Interface(fn= multi_model,   inputs=gr.Audio(source="microphone", type='filepath'), 
   outputs=[output_text, output_image])
    demo.launch()
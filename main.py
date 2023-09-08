
import os
import chainlit as cl
import openai

# whenever message is inputted
@cl.on_message
async def main(message: str):  

    response = openai.ChatCompletion.create(
        model = 'gpt-4',
        messages = [
            {'role': 'assistant', 'content': 'you are a helpful assistant'},
            {'role': 'user', 'content': message}
        ],
        temperature = 1,
        
    )
    response = response['choices'][0]['message']['content']
    await cl.Message(content = response).send()


# Pass the message into ChatGPT API

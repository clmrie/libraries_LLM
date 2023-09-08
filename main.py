
import os
import chainlit as cl
import openai

os.environ['OPENAI_API_KEY'] = "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"
openai.api_key = "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"  

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

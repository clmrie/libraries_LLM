
import os
import openai
from langchain import PromptTemplate, LLMChain, OpenAI
import chainlit as cl

template = """Question: {question}

Answer: Let's think step by step."""

@cl.on_chat_start
def main():
    prompt = PromptTemplate(template = template, input_variables = ["question"])
    # connects the prompt with LLM
    llm_chain = LLMChain(
        prompt = prompt,
        llm = OpenAI(temperature = 1, streaming = True),
        verbose = True,
    )

    # to access it on on_message call   
    cl.user_session.set("llm_chain", llm_chain)

@cl.on_message
async def main(message: str):
    llm_chain = cl.user_session.get("llm_chain")

    res = await llm_chain.acall(message, callbacks = [cl.AsyncLangchainCallbackHandler()])

    await cl.Message(res['text']).send()
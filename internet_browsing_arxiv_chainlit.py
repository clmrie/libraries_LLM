
from langchain.agents import initialize_agent, Tool, AgentExecutor, AgentType
from langchain.agents import load_tools
from langchain.chat_models import ChatOpenAI
import os
import openai
import chainlit as cl

@cl.on_chat_start
def start():
    llm = ChatOpenAI(temperature=0.5, streaming=True)
    tools = load_tools(
        ["arxiv"]
    )

    agent_chain = initialize_agent(
        tools,
        llm,
        max_iteration = 5,
        # making predictions on examples never seen before
        agent = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose = True,
        handle_parsing_errors = True,
    )

    cl.user_session.set("agent", agent_chain)


@cl.on_message
async def main(message):
    agent = cl.user_session.get('agent')
    cb = cl.LangchainCallbackHandler(stream_final_answer = True)

    await cl.make_async(agent.run)(message, callbacks = [cb])

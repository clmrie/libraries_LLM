
import os
import openai

from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType

llm = ChatOpenAI(temperature = 0.3)
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

agent_chain.run(
    "what are the applications of Generative AI?",
)

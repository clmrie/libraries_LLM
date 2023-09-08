import os
import openai


from youtube_search import YoutubeSearch
from langchain.tools import YouTubeSearchTool
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.llms import OpenAI

tool = YouTubeSearchTool()

tools = [
    Tool(
        name = 'Search',
        func = tool.run,
        description="useful for when you need to give links to youtube videos. Remember to put https://youtube.com/ in front of every link to complete it",
    )
]

agent = initialize_agent(
    tools,
    OpenAI(temperature=0),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)
agent.run('i want to watch a video about the benefits of vegan diet')
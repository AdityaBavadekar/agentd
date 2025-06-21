"""
The sub-agent for the agentd system.

Social Media Post Generation Agent: Drafts engaging content for various social media platforms (e.g., LinkedIn, Blog, Twitter) to promote the idea.
"""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from agentd.tools import generate_image_tool

from . import agent_constants

image_generation_agent_tool = AgentTool(
    agent=Agent(
        name=agent_constants.IMAGE_GENERATION_AGENT_NAME,
        model=agent_constants.IMAGE_GENERATION_AGENT_MODEL,
        instruction=agent_constants.IMAGE_GENERATION_AGENT_INSTRUCTION,
        description=agent_constants.IMAGE_GENERATION_AGENT_DESCRIPTION,
        tools=[generate_image_tool],
    ),
    skip_summarization=True,
)


social_media_post_generation_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    tools=[image_generation_agent_tool],
    output_key="social_media_posts",
)

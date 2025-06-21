"""
The sub-agent for the agentd system.

Idea Image Generation Agent: Creates conceptual advertisement images or visual representations based on the idea's core concepts and marketing goals.
"""

from google.adk.agents import Agent

from agentd.tools import generate_image_tool

from . import agent_constants

idea_image_generation_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    tools=[generate_image_tool],
    output_key="generated_images",
)

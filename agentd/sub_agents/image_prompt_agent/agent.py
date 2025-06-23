"""
The sub-agent for the agentd system.

Image Prompt Agent: Refines image descriptions and generates images using the improved prompt
"""

from google.adk.tools.agent_tool import AgentTool

from agentd.tools.image_generation import generate_image_tool
from agentd.utils import LinkInjectorAgent

from . import agent_constants

image_prompt_agent_tool = AgentTool(
    agent=LinkInjectorAgent(
        name=agent_constants.AGENT_NAME,
        model=agent_constants.MODEL,
        instruction=agent_constants.AGENT_INSTRUCTION,
        description=agent_constants.AGENT_DESCRIPTION,
        tools=[generate_image_tool],
        output_key="generated_image",
        keep_identifiers=True,
    )
)

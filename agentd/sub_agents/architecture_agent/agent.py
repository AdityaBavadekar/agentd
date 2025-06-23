"""
The sub-agent for the agentd system.

Architecture Agent: Designs a suitable technical architecture with reasoning for technology choices and includes a high-level cost estimation.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search

from . import agent_constants

architecture_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    tools=[google_search],  # so that agent can access actual pricing information
    output_key="architecture_agent",
)

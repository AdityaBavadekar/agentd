"""
The sub-agent for the agentd system.

Competitor Analysis Agent: Investigates existing solutions and competitors in the market, assessing their offerings, strengths, weaknesses, and market positioning.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search

from . import agent_constants

competitor_analysis_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    tools=[google_search],
    output_key="competitor_analysis",
)

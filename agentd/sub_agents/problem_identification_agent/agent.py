"""
The sub-agent for the agentd system.

Problem Identification Agent: Researches and identifies prevalent problems, challenges, and pain points related to the analyzed topic from various data sources.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search

from . import agent_constants

problem_identification_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    tools=[google_search],
    output_key="problem_statements",
)

"""
The sub-agent for the agentd system.

Technical Advisor Agent: Provides recommendations on relevant Google Cloud services (APIs, deployment, databases) and strategies for finding initial test users.
"""

from google.adk.agents import Agent

from . import agent_constants

technical_advisor_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    output_key="technical_advice",
)

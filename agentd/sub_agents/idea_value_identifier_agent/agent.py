"""
The sub-agent for the agentd system.

Idea Value Identifier Agent: Extracts and highlights the unique selling propositions, core value, and competitive advantages of the proposed idea.
"""

from google.adk.agents import Agent

from . import agent_constants

idea_value_identifier_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    output_key="idea_value_identification",
)

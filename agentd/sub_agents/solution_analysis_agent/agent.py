"""
The sub-agent for the agentd system.

Solution Analysis Agent: Brainstorms, evaluates, and proposes potential solutions or features for the initial idea, addressing the identified problems.
"""

from google.adk.agents import Agent

from . import agent_constants

solution_analysis_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    output_key="solutions_analysis",
)

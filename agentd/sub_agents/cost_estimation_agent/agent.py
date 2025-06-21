"""
The sub-agent for the agentd system.

Cost Estimation Agent: Offers a conditional, high-level cost estimation for the suggested technical stack and potential operational expenses.
"""

from google.adk.agents import Agent

from . import agent_constants

# TODO: use [rag + google_search]

cost_estimation_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    output_key="cost_estimation",
)

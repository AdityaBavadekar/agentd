"""
The sub-agent for the agentd system.

Topic Analysis Agent: Analyzes and refines the initial idea or topic provided by the user, identifying core concepts and keywords for further research.
"""

from google.adk.agents import Agent

from . import agent_constants

topic_analysis_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    output_key="topic_analysis",
)

"""The master agent for the agentd system."""

from . import agent
from .agent import AgentD

# run pre checks
agent.run_preliminary_tests()

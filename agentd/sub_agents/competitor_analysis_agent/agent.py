"""
The sub-agent for the agentd system.

Competitor Analysis Agent: Investigates existing solutions and competitors in the market, assessing their offerings, strengths, weaknesses, and market positioning.
"""

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import google_search

from agentd.utils import extract_all_urls, resolve_redirect

from . import agent_constants


def after_agent_callback(callback_context: CallbackContext, *args, **kwargs):
    output = callback_context.state.get("competitor_analysis", "")

    urls = extract_all_urls(output)
    if not urls:
        return None

    for url in urls:
        try:
            resolved_url = resolve_redirect(url)
            if resolved_url:
                output = output.replace(url, resolved_url)
        except Exception as e:
            print(f"Error resolving URL {url}: {e}")

    callback_context.state["competitor_analysis"] = output


competitor_analysis_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    after_agent_callback=after_agent_callback,
    tools=[google_search],
    output_key="competitor_analysis",
)

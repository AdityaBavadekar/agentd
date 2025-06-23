"""
The sub-agent for the agentd system.

Solution Analysis Agent: Brainstorms, evaluates, and proposes potential solutions or features for the initial idea, addressing the identified problems.
"""

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

from . import agent_constants


async def another_simple_after_agent_modifier(
    callback_context: CallbackContext, *_args, **_kwargs
):
    """A simple after model callback that just returns the state as is."""
    print("===" * 8)
    print(f"[Callback] Before model call for agent: {callback_context.agent_name}")
    print("===" * 8)

    callback_context.state["user_input_specs"] = {
        "required": True,
        "agent_name": agent_constants.AGENT_NAME,
        "description": "Please provide the number of the solution you would like to proceed with, or a new problem statement for analysis.",
    }
    print("ADDED user input specs to state")

    from google.genai import types

    return types.Content(
        parts=[
            types.Part(
                text="<ASK>Would you like to proceed with any of the proposed solutions? If so, please specify the problem number or provide a new problem statement for analysis.<ASK>"
            )
        ]
    )


solution_analysis_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    after_agent_callback=another_simple_after_agent_modifier,
    output_key="solutions_analysis",
)

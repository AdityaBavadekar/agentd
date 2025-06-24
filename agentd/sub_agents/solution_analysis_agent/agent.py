"""
The sub-agent for the agentd system.

Solution Analysis Agent: Brainstorms, evaluates, and proposes potential solutions or features for the initial idea, addressing the identified problems.
"""

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools import transfer_to_agent

from . import agent_constants


def simpler_after_model_modifier(
    callback_context: CallbackContext, llm_response: LlmResponse
):
    """A simpler after model callback that just returns the state as is."""
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

    return LlmResponse(
        content=types.Content(
            parts=[
                types.Part(
                    text=(
                        llm_response.content.parts[0].text
                        if llm_response.content.parts
                        else ""
                    )
                ),
                types.Part(
                    function_call=types.FunctionCall(
                        name="transfer_to_agent",
                        args={
                            "agent_name": "root_agent",
                        },
                    )
                ),
            ]
        ),
        grounding_metadata=llm_response.grounding_metadata,
    )


solution_analysis_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    after_model_callback=simpler_after_model_modifier,
    tools=[transfer_to_agent],
    output_key="solutions_analysis",
)

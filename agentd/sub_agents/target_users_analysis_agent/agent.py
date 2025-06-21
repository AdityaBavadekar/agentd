"""
The sub-agent for the agentd system.

Target Users Analysis Agent: Develops detailed user profiles and identifies potential user segments for the idea, based on the proposed solutions and market context.
"""

import json

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool, google_search
from google.genai import types

from agentd.tools import generate_diagrams
from agentd.utils import extract_json_from_text

from . import agent_constants


def generate_diagrams_tool(data: str, *args, **kwargs) -> str:
    """
    - Extracts JSON data from the input text.
    - Generates diagrams based on the extracted JSON data.
    - Removes diagram-specific data from the JSON after generation.
    - Returns the modified JSON data and a list of image public URLs.
    - Handles errors gracefully and returns an error message if JSON extraction fails.

    Args:
        data (str): The input text containing JSON data and diagram generation instructions.

    Returns:
        tuple: A tuple containing:
        - json_data (dict): The modified JSON data after diagram generation.
        - image_public_urls (list): A list of public URLs for the generated diagrams.
        - failure (bool): Indicates if there was an error during diagram generation.

        If no valid JSON data is found, returns None, an empty list, and True for failure.
    """
    failure = True
    image_public_urls = []
    json_data = None
    try:
        json_data = extract_json_from_text(data)
        image_public_urls = generate_diagrams(json_data)
        failure = False
    except Exception as e:
        error_msg = f"Error generating diagrams: {str(e)}, Continue with the analysis."
        print(error_msg)
        failure = True

    if not json_data:
        error_msg = "No valid JSON data found in the input. Cannot generate diagrams."
        print(error_msg)
        return None, [], True

    # remove diagram specific data since we dont require it post diagram generation
    json_data["pie_chart_segments"] = None
    json_data["pain_points_bar_chart_data"] = None
    json_data["word_cloud_text"] = None
    json_data["knowledge_graph_elements"] = None

    return json_data, image_public_urls, failure


def simple_after_model_modifier(callback_context: CallbackContext, *args, **kwargs):
    """Inspects/modifies the LLM request or skips the call."""
    print("===" * 8)
    print(f"[Callback] After model call for agent: {callback_context.agent_name}")
    print("===" * 8)

    callback_context.state["users_analysis_image_urls"] = []

    # generate diagram and remove non-required data
    post_image_generation_result = generate_diagrams_tool(
        callback_context.state["target_users_analysis"]
    )
    json_data, image_public_urls, failure = post_image_generation_result

    if not failure:
        # update the state with the generated image URLs
        callback_context.state["users_analysis_image_urls"] = image_public_urls
        print("Diagrams generated successfully and state updated.")
    else:
        print("Failed to generate diagrams.")

    # update the state with the modified JSON data if available
    if json_data:
        callback_context.state["target_users_analysis"] = json.dumps(
            json_data, indent=2
        )

    return None


target_users_analysis_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    after_agent_callback=simple_after_model_modifier,
    tools=[
        google_search,
    ],
    output_key="target_users_analysis",
)

"""
The sub-agent for the agentd system.

Report Generation Agent: Compiles all gathered research and analysis into a comprehensive 'Idea Feasibility Report' and manages the user's decision to proceed.
"""

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

from agentd.tools.image_generation import generate_image_tool
from agentd.utils import create_and_upload_pdf, json_to_markdown

from . import agent_constants


def simple_after_model_modifier(callback_context: CallbackContext, *args, **kwargs):
    """Generates a PDF report from the report agent's output and uploads it to cloud storage."""

    agent_name = callback_context.agent_name
    print("===" * 8)
    print(f"[Callback] Before model call for agent: {agent_name}")
    print("===" * 8)
    report_content: str = callback_context.state["generated_report"]

    # Replace "@[TARGET_USERS_PLACEHOLDER]@" with JSON Formatted data from previous agent
    report_content = report_content.replace("<DO_NOT_CHANGE>", "")
    report_content = report_content.replace("</DO_NOT_CHANGE>", "")
    import json

    json_target_users_analysis = json.loads(
        callback_context.state["target_users_analysis"]
    )
    report_content.replace(
        "@[TARGET_USERS_PLACEHOLDER]@", json_to_markdown(json_target_users_analysis)
    )
    # also change the state
    callback_context.state["generated_report"] = report_content

    report_content = report_content.removeprefix("```markdown")
    report_content = report_content.removeprefix("```md")
    report_content = report_content.removeprefix("```")
    report_content = report_content.removesuffix("```")
    public_url = create_and_upload_pdf(
        report_content,
        "Idea Feasibility Report",
        local_dir="reports",
        remote_dir="reports",
    )
    print("==== Report generation completed successfully.==== ")
    print(f"Public URL of the report: {public_url}")
    callback_context.state["generated_report_url"] = public_url
    return None


report_generation_agent = Agent(
    name=agent_constants.AGENT_NAME,
    model=agent_constants.MODEL,
    instruction=agent_constants.AGENT_INSTRUCTION,
    description=agent_constants.AGENT_DESCRIPTION,
    after_agent_callback=simple_after_model_modifier,
    tools=[generate_image_tool],
    output_key="generated_report",
)

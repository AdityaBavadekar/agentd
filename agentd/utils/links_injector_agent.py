"""LinkInjector Agent: Handles Masking and Unmasking of URLs."""

import copy
from typing import Any, Dict, Optional

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from .link_utils import extract_and_replace_urls, restore_urls_from_placeholders


def log(message: str, *args, **kwargs):
    """Logging method for the LinkInjectorAgent."""
    print(f"============ [LinkInjectorAgent] {message} ======", *args, **kwargs)


class LinkInjectorAgent(Agent):
    """
    An agent that register two callbacks:
    1. After tool callback: modifies the tool response to extract URLs and store them in the state and replace them with identifiers.
    2. After model callback: modifies the model response to restore URLs from the identifiers stored in the state.

    This allows the agent to inject links into the output of
    the agent after the model has generated its response.

    If `keep_identifiers` is set to True:
        - Make sure to use the `replace_identifiers_with_urls` method to restore URLs in the model output.
    """

    keep_identifiers: bool = False

    def __init__(self, *args, **kwargs):
        """
        Args:
            keep_identifiers (bool, optional): If True, the agent will keep the identifiers in the output.
                If False, it will replace the identifiers with the actual URLs. Defaults to False.
        """
        super().__init__(*args, **kwargs)
        self.after_tool_callback = LinkInjectorAgent._after_tool_callback_modifier
        self.after_model_callback = self._after_model_callback_modifier_base

    @staticmethod
    def _after_tool_callback_modifier(
        tool: BaseTool,
        tool_context: ToolContext,
        tool_response: Dict,
        *args,
        **kwargs,
    ) -> Optional[Dict]:
        """
        Masks all of the URLs in the tool response and stores them in the state.
        """
        tool_name = tool.name

        if isinstance(tool_response, dict):
            if "result" in tool_response:
                tool_response = tool_response["result"]

        # extract all urls from the tool response
        log(f"EXTRACTING URLs FROM TOOL RESPONSE of '{tool_name}' TOOL")
        modified_data = LinkInjectorAgent.replace_urls_with_identifiers(tool_response)
        links_map = modified_data["map"]
        data = modified_data["data"]

        if not links_map:
            log("URLs NOT FOUND IN TOOL RESPONSE")
            return None
        else:
            log(f"URLs FOUND IN TOOL RESPONSE: {links_map}")
            log(f"Modified data: {data}")
            if "links_map" in tool_context.state:
                log("Links map already exists in state, merging with new links map.")
                existing_map = tool_context.state["links_map"]
                existing_map.update(links_map)
                tool_context.state["links_map"] = existing_map
            else:
                tool_context.state["links_map"] = links_map
            return data

    def _after_model_callback_modifier_base(self, *args, **kwargs):
        """
        If `keep_identifiers` is True, skip the links injection.
        Otherwise, call the `LinkInjectorAgent._after_model_callback_modifier`
        """
        if self.keep_identifiers:
            log("keep_identifiers is True, skipping links injection.")
            return None

        return self._after_model_callback_modifier(*args, **kwargs)

    @staticmethod
    def _after_model_callback_modifier(
        callback_context: CallbackContext, llm_response: LlmResponse
    ) -> Optional[LlmResponse]:
        """
        Injects links into the output of the agent, using the links map stored in the state.
        """
        log("AFTER MODEL CALLBACK MODIFIER CALLED")

        links_map = callback_context.state.get("links_map", {})
        if not links_map:
            log("NO LINKS MAP FOUND IN STATE")
            return None

        original_text = ""

        # [TAKEN FROM ADK DOCUMENTATION]
        if llm_response.content and llm_response.content.parts:
            # Assuming simple text response for this example
            if llm_response.content.parts[0].text:
                original_text = llm_response.content.parts[0].text
            elif llm_response.content.parts[0].function_call:
                log(
                    f"Inspected response: Contains function call '{llm_response.content.parts[0].function_call.name}'. No text modification."
                )
                return None  # Don't modify tool calls in this example
            else:
                log("Inspected response: No text content found.")
                return None
        elif llm_response.error_message:
            log(
                f"Inspected response: Contains error '{llm_response.error_message}'. No modification."
            )
            return None
        else:
            log("Inspected response: Empty LlmResponse.")
            return None  # Nothing to modify

        log(f"Original text: {original_text}")

        # Restore URLs in the model output
        model_output = original_text
        modified_text = LinkInjectorAgent.replace_identifiers_with_urls(
            text=model_output, links_map=links_map, state=None
        )

        log("LINKS INJECTED INTO MODEL OUTPUT")

        # Update the model output with restored URLs
        modified_parts = [copy.deepcopy(part) for part in llm_response.content.parts]
        modified_parts[0].text = modified_text  # Update the text in the copied part

        log(f"Modified text: {modified_text}")

        new_response = LlmResponse(
            content=types.Content(role="model", parts=modified_parts),
            # Copy other relevant fields if necessary, e.g., grounding_metadata
            grounding_metadata=llm_response.grounding_metadata,
        )
        return new_response

    @staticmethod
    def replace_identifiers_with_urls(
        text: str, state: Optional[Dict], links_map: Dict[str, str] = None
    ) -> str:
        """
        Replace identifiers in the text with actual URLs from the links map. Either one of `links_map` or `state` should be provided.

        Args:
            text (str): The text containing identifiers to be replaced.
            state (Optional[Dict], optional): Optional state dictionary. Defaults to None.
            links_map (Dict[str, str]): A dictionary mapping identifiers to URLs.

        """

        if not links_map:
            # try to extract from state
            if state is None:
                raise ValueError("Either links_map or state must be provided.")
            links_map = state.get("links_map", {})

        if not links_map:
            log("No links map found, returning original text.")
            return text

        modified_text = restore_urls_from_placeholders(text, links_map)
        return modified_text

    @staticmethod
    def replace_urls_with_identifiers(text: Any) -> str:
        """
        Replace URLs in the text with identifiers stored in the state.
        Make sure to save the "map" of identifiers-to-URLs in the state manually.

        Args:
            text (str): The text containing URLs to be replaced.

        Returns:
            dict: {"data": Any, "map": Dict[str, str]}
        """
        return extract_and_replace_urls(text)

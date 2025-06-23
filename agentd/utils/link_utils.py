import re
import uuid
from typing import Any, Dict, List, Union

import requests

# A reasonably comprehensive regex for common URL formats.
# It captures http/https, optional www, domain, path, query parameters, and fragments.
URL_REGEX = r"https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)"


def extract_all_urls(data: Union[str, Dict[str, Any], List[Any]]) -> List[str]:
    """
    Recursively extracts all URLs from a string, dictionary, or list.

    Args:
        data: The input data (string, dictionary, or list) to search for URLs.

    Returns:
        A list of all unique URLs found in the data.
    """
    found_urls = []

    if isinstance(data, str):
        found_urls.extend(re.findall(URL_REGEX, data))
    elif isinstance(data, dict):
        for value in data.values():
            found_urls.extend(extract_all_urls(value))
    elif isinstance(data, list):
        for item in data:
            found_urls.extend(extract_all_urls(item))

    return list(set(found_urls))


def _generate_placeholder_map(urls: List[str]) -> Dict[str, str]:
    """
    Generates a mapping from original URLs to 'link-a', 'link-b', etc.
    Ensures consistent mapping for unique URLs.
    """
    placeholder_map = {}

    def generate_link_id(i: int) -> str:
        """
        Generates a placeholder ID in the format: <uuid-part>-<index>
        Example: 'a1b2-3'

        - Uses first 4 hex chars of UUID (16^4 = ~65k combinations).
        - Appends a index for added more uniqueness.
        - Kept short to minimize confusion for the LLM.

        It is important to not generate longer ids since this will be relayed  back to the LLM Model.

        - This simple approach works for most cases.
        - For stronger uniqueness, use longer UUID parts or add part of the timestamp.
        - Or if you want more readablity, you use "[url-domain]" as a prefix after "link".
        """

        trunc_len = 4
        a = str(uuid.uuid4())[:trunc_len]
        return f"{a}-{i}"

    for i, url in enumerate(
        sorted(urls)
    ):  # Sorting ensures consistent 'a', 'b' assignment
        placeholder_map[url] = f"<generated-link-identifier-{generate_link_id(i)}>"
    return placeholder_map


def _replace_urls_with_placeholders(
    data: Union[str, Dict[str, Any], List[Any]], url_placeholder_map: Dict[str, str]
) -> Union[str, Dict[str, Any], List[Any]]:
    """
    Recursively replaces original URLs within a string, dictionary, or list
    with their corresponding placeholders based on the provided map.

    Args:
        data: The input data (string, dictionary, or list) where URLs need to be replaced.
        url_placeholder_map: A dictionary where keys are original URLs and values are their
                             desired placeholder strings (e.g., {"http://example.com": "link-a"}).

    Returns:
        The modified data structure with URLs replaced by placeholders.
        Returns other data types (int, bool, None) as-is.
    """
    if isinstance(data, str):
        modified_string = data
        # Sort URLs by length in descending order to avoid partial replacements
        # (e.g., if "http://example.com/path" and "http://example.com" are both in map)
        sorted_urls_to_replace = sorted(
            url_placeholder_map.keys(), key=len, reverse=True
        )

        for original_url in sorted_urls_to_replace:
            placeholder = url_placeholder_map[original_url]
            modified_string = modified_string.replace(original_url, placeholder)
        return modified_string
    elif isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            new_dict[key] = _replace_urls_with_placeholders(value, url_placeholder_map)
        return new_dict
    elif isinstance(data, list):
        new_list = []
        for item in data:
            new_list.append(_replace_urls_with_placeholders(item, url_placeholder_map))
        return new_list

    # for other types (int, float, bool, None), return them as-is
    return data


def _restore_urls_from_placeholders(
    data: Union[str, Dict[str, Any], List[Any]], url_placeholder_map: Dict[str, str]
) -> Union[str, Dict[str, Any], List[Any]]:
    """
    Recursively restores original URLs within a string, dictionary, or list
    by replacing placeholders (e.g., "link-a") with their corresponding original URLs.

    Args:
        data: The input data (string, dictionary, or list) with placeholders to be restored.
        url_placeholder_map: The original dictionary where keys are original URLs and values are their
                             placeholder strings (e.g., {"http://example.com": "link-a"}).
                             This map will be inverted internally.

    Returns:
        The modified data structure with placeholders restored to original URLs.
        Returns other data types (int, bool, None) as-is.
    """
    # 1. Invert the map: placeholder -> original_url
    placeholder_to_url_map = {v: k for k, v in url_placeholder_map.items()}

    if isinstance(data, str):
        modified_string = data
        # Sort placeholders by length in descending order to avoid partial replacements
        # (e.g., if "link-abc" and "link-a" existed, replace "link-abc" first)
        sorted_placeholders_to_restore = sorted(
            placeholder_to_url_map.keys(), key=len, reverse=True
        )

        for placeholder in sorted_placeholders_to_restore:
            original_url = placeholder_to_url_map[placeholder]
            modified_string = modified_string.replace(placeholder, original_url)
        return modified_string
    elif isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            new_dict[key] = _restore_urls_from_placeholders(
                value, url_placeholder_map
            )  # Recursive call
        return new_dict
    elif isinstance(data, list):
        new_list = []
        for item in data:
            new_list.append(
                _restore_urls_from_placeholders(item, url_placeholder_map)
            )  # Recursive call
        return new_list
    else:
        # For other types (int, float, bool, None), return them as-is
        return data


def extract_and_replace_urls(
    data: Union[str, Dict[str, Any], List[Any]],
) -> Dict[str, Any]:
    """
    Extracts URLs from the input data and replaces them with placeholders.
    """
    urls = extract_all_urls(data)
    placeholder_map = _generate_placeholder_map(urls)
    if not placeholder_map:
        return {
            "data": data,
            "map": {},
        }

    modified_data = _replace_urls_with_placeholders(data, placeholder_map)
    return {
        "data": modified_data,
        "map": placeholder_map,
    }


def restore_urls_from_placeholders(
    data: Union[str, Dict[str, Any], List[Any]],
    url_placeholder_map: Dict[str, str],
) -> Union[str, Dict[str, Any], List[Any]]:
    """
    Restores URLs in the input data from their placeholders.

    Args:
        data: The input data (string, dictionary, or list) with placeholders to be restored.
        url_placeholder_map: A dictionary where keys are original URLs and values are their
                             placeholder strings (e.g., {"http://example.com": "link-a"}).

    Returns:
        The modified data structure with placeholders restored to original URLs.
    """
    if not url_placeholder_map:
        return data
    return _restore_urls_from_placeholders(data, url_placeholder_map)


def resolve_redirect(url):
    """Returns the final URL after following redirects."""
    try:
        response = requests.head(url, allow_redirects=True)
        return response.url
    except requests.RequestException as e:
        print(f"Error resolving URL {url}: {e}")
        return None

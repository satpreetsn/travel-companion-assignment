import json
import re
from typing import Any

from context.manager import TravelContext
from generation.llm import get_llm


class MCPToolSelector:
    """
    Uses the LLM to determine whether the user's request requires
    an MCP tool and, if so, which tool and arguments should be used.
    """

    def __init__(self):
        self.llm = get_llm()

    def select_tool(
        self,
        user_message: str,
        travel_context: TravelContext,
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Select an MCP tool based on the user's request.

        Returns:

        {
            "use_mcp": true,
            "tool_name": "get_weather",
            "arguments": {
                "destination": "Singapore"
            }
        }

        or:

        {
            "use_mcp": false,
            "tool_name": null,
            "arguments": {}
        }
        """

        tools_description = self._format_tools(tools)

        prompt = f"""
You are the MCP tool-selection component of a travel assistant.

Your ONLY job is to determine whether the user's latest message
requires one of the available MCP tools.

Do NOT answer the user's question.

Do NOT invent tools.

Do NOT invent arguments.

Use the travel context to resolve references such as:

- there
- here
- that city
- this place
- the destination

CURRENT TRAVEL CONTEXT
----------------------
{travel_context.to_prompt()}


USER MESSAGE
------------
{user_message}


AVAILABLE MCP TOOLS
-------------------
{tools_description}


Return ONLY valid JSON using exactly this structure:

{{
    "use_mcp": false,
    "tool_name": null,
    "arguments": {{}},
    "confidence": 0.0
}}


Rules:

1. Set "use_mcp" to true only when the user's request
   requires one of the available MCP tools.

2. If no MCP tool is required:

{{
    "use_mcp": false,
    "tool_name": null,
    "arguments": {{}},
    "confidence": 0.95
}}

3. If an MCP tool is required, "tool_name" MUST exactly match
   one of the available tool names.

4. "arguments" MUST contain only arguments defined by the
   selected tool's input schema.

5. Use the travel context when resolving missing information.

6. Do not invent information that is not available from:
   - the user message
   - the travel context

7. If a required argument cannot be determined, do not guess it.
   In that case, set "use_mcp" to false.

8. confidence must be between 0 and 1.

Examples:

User:
"What's the weather there?"

Context:
destination: Singapore

Return:

{{
    "use_mcp": true,
    "tool_name": "get_weather",
    "arguments": {{
        "destination": "Singapore"
    }},
    "confidence": 0.98
}}


User:
"How much is 10000 INR in Singapore dollars?"

Return:

{{
    "use_mcp": true,
    "tool_name": "get_currency_exchange_rate",
    "arguments": {{
        "from_currency": "INR",
        "to_currency": "SGD",
        "amount": 10000
    }},
    "confidence": 0.99
}}


User:
"Find flights from Delhi to Singapore on October 10."

Return:

{{
    "use_mcp": true,
    "tool_name": "get_flight_info",
    "arguments": {{
        "origin": "Delhi",
        "destination": "Singapore",
        "travel_date": "2026-10-10"
    }},
    "confidence": 0.99
}}


User:
"What are the best attractions in Singapore?"

Return:

{{
    "use_mcp": false,
    "tool_name": null,
    "arguments": {{}},
    "confidence": 0.98
}}
"""

        response = self.llm.invoke(prompt)

        content = response.content.strip()

        content = re.sub(
            r"^```(?:json)?\s*",
            "",
            content,
            flags=re.IGNORECASE,
        )

        content = re.sub(
            r"\s*```$",
            "",
            content,
        )

        try:
            result = json.loads(content)

        except json.JSONDecodeError:

            match = re.search(
                r"\{.*\}",
                content,
                re.DOTALL,
            )

            if not match:
                raise ValueError(
                    "Could not parse MCP tool-selection response:\n"
                    f"{content}"
                )

            result = json.loads(match.group(0))

        return self._validate_result(
            result=result,
            tools=tools,
        )

    @staticmethod
    def _format_tools(
        tools: list[dict[str, Any]],
    ) -> str:
        """
        Convert MCP tool definitions into a compact prompt.
        """

        if not tools:
            return "No MCP tools are currently available."

        formatted = []

        for tool in tools:

            formatted.append(
                f"""
Tool name:
{tool["name"]}

Description:
{tool.get("description", "")}

Input schema:
{json.dumps(tool.get("input_schema", {}), indent=2)}
"""
            )

        return "\n".join(formatted)

    @staticmethod
    def _validate_result(
        result: dict[str, Any],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Validate the LLM's tool-selection response.
        """

        use_mcp = result.get(
            "use_mcp",
            False,
        )

        if not isinstance(use_mcp, bool):
            use_mcp = False

        tool_name = result.get("tool_name")

        arguments = result.get(
            "arguments",
            {},
        )

        if not isinstance(arguments, dict):
            arguments = {}

        available_tool_names = {
            tool["name"]
            for tool in tools
        }

        if not use_mcp:
            return {
                "use_mcp": False,
                "tool_name": None,
                "arguments": {},
                "confidence": MCPToolSelector._confidence(
                    result
                ),
            }

        if tool_name not in available_tool_names:
            return {
                "use_mcp": False,
                "tool_name": None,
                "arguments": {},
                "confidence": 0.0,
            }

        return {
            "use_mcp": True,
            "tool_name": tool_name,
            "arguments": arguments,
            "confidence": MCPToolSelector._confidence(
                result
            ),
        }

    @staticmethod
    def _confidence(
        result: dict[str, Any],
    ) -> float:

        try:
            confidence = float(
                result.get(
                    "confidence",
                    0.0,
                )
            )

        except (TypeError, ValueError):
            confidence = 0.0

        return max(
            0.0,
            min(1.0, confidence),
        )
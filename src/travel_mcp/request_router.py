import json
import re
from typing import Any

from context.manager import TravelContext
from generation.llm import get_llm


class RequestRouter:
    """
    Determines which information sources are required
    to answer the user's request.

    Possible routes:

    - rag
    - mcp
    - both
    """

    def __init__(self):

        self.llm = get_llm()

    def route(
        self,
        user_message: str,
        travel_context: TravelContext,
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:

        tools_description = self._format_tools(
            tools
        )

        prompt = f"""
You are the request-routing component of a travel assistant.

Your ONLY job is to determine which information source is
required to answer the user's latest message.

Available information sources:

1. RAG
   - Contains travel knowledge from the local knowledge base.
   - Useful for destinations, attractions, transportation,
     travel guidance, itineraries, cultural information,
     and other relatively static travel information.

2. MCP
   - Provides information through external tools.
   - Useful for current or dynamic information such as:
     weather, currency conversion, and flight information.

3. BOTH
   - Use when the user's question requires information from
     both the knowledge base and an MCP tool.

Do NOT answer the user's question.

Do NOT select a specific MCP tool here.
The MCP tool selector will do that separately.

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
    "route": "rag",
    "confidence": 0.0,
    "reason": ""
}}


"route" must be exactly one of:

"rag"
"mcp"
"both"


Examples:

User:
"What are the best attractions in Singapore?"

Return:

{{
    "route": "rag",
    "confidence": 0.98,
    "reason": "The question asks about destination attractions."
}}


User:
"What's the weather there?"

Context:
destination: Singapore

Return:

{{
    "route": "mcp",
    "confidence": 0.98,
    "reason": "Current weather should come from an MCP tool."
}}


User:
"How much is 10000 INR in Singapore dollars?"

Return:

{{
    "route": "mcp",
    "confidence": 0.99,
    "reason": "Currency conversion requires an MCP tool."
}}


User:
"Find flights from Delhi to Singapore."

Return:

{{
    "route": "mcp",
    "confidence": 0.99,
    "reason": "Flight information requires an MCP tool."
}}


User:
"What should I do in Singapore tomorrow and what's
the weather like?"

Return:

{{
    "route": "both",
    "confidence": 0.98,
    "reason": "The request needs travel recommendations and current weather."
}}


Rules:

1. Select "rag" when the local knowledge base is sufficient.

2. Select "mcp" when the request requires information
   available through an MCP tool.

3. Select "both" when both sources are needed.

4. Do not assume that every travel question requires MCP.

5. Do not assume that every travel question requires RAG.

6. Do not select a specific MCP tool.

7. Do not invent information.

8. confidence must be between 0 and 1.

Return ONLY JSON.
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
                    "Could not parse request-router response:\n"
                    f"{content}"
                )

            result = json.loads(
                match.group(0)
            )

        return self._validate_result(
            result
        )

    @staticmethod
    def _format_tools(
        tools: list[dict[str, Any]],
    ) -> str:

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
{json.dumps(
    tool.get("input_schema", {}),
    indent=2,
)}
"""
            )

        return "\n".join(formatted)

    @staticmethod
    def _validate_result(
        result: dict[str, Any],
    ) -> dict[str, Any]:

        valid_routes = {
            "rag",
            "mcp",
            "both",
        }

        route = result.get(
            "route",
            "rag",
        )

        if route not in valid_routes:
            route = "rag"

        try:

            confidence = float(
                result.get(
                    "confidence",
                    0.0,
                )
            )

        except (TypeError, ValueError):

            confidence = 0.0

        confidence = max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        )

        return {
            "route": route,
            "confidence": confidence,
            "reason": result.get(
                "reason",
                "",
            ),
        }
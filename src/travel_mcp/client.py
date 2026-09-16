import sys
import json
from pathlib import Path
from typing import Any

from mcp import Client, StdioServerParameters
from mcp.types import TextContent


class MCPClient:
    """
    Generic client for the Travel Companion MCP server.

    The client discovers available tools from the MCP server.

    It does not contain knowledge of specific tools such as:
    - weather
    - currency
    - flights
    """

    def __init__(self):

        project_root = Path(__file__).resolve().parents[2]

        server_path = (
            project_root
            / "src"
            / "travel_mcp"
            / "server.py"
        )

        self.server = StdioServerParameters(
            command=sys.executable,
            args=[
                "-u",
                str(server_path),
            ],
        )

    async def get_tools(self) -> list[dict[str, Any]]:
        """
        Discover tools exposed by the MCP server.
        """

        async with Client(self.server) as client:

            result = await client.list_tools()

            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                }
                for tool in result.tools
            ]

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """
        Invoke an MCP tool by name.

        Handles both structured and unstructured MCP results.
        """

        async with Client(self.server) as client:

            result = await client.call_tool(
                tool_name,
                arguments,
            )

            # -----------------------------------------------------
            # Tool returned an error
            # -----------------------------------------------------

            if result.is_error:

                error_messages = []

                for content in result.content:

                    if isinstance(content, TextContent):
                        error_messages.append(
                            content.text
                        )

                return {
                    "status": "error",
                    "tool": tool_name,
                    "message": "\n".join(
                        error_messages
                    ),
                }

            # -----------------------------------------------------
            # Structured result
            # -----------------------------------------------------

            if result.structured_content is not None:
                return result.structured_content

            # -----------------------------------------------------
            # Unstructured result
            # -----------------------------------------------------

            text_parts = []

            for content in result.content:

                if isinstance(content, TextContent):
                    text_parts.append(
                        content.text
                    )

            if not text_parts:
                return {
                    "status": "success",
                    "tool": tool_name,
                    "result": None,
                }

            text = "\n".join(text_parts)

            # -----------------------------------------------------
            # Try JSON conversion
            # -----------------------------------------------------

            try:

                return json.loads(text)

            except json.JSONDecodeError:

                return {
                    "status": "success",
                    "tool": tool_name,
                    "result": text,
                }
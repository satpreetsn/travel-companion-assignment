from context.manager import TravelContext
from travel_mcp.client import MCPClient
from travel_mcp.tool_selector import MCPToolSelector


def main():

    # ---------------------------------------------------------
    # Travel context
    # ---------------------------------------------------------

    travel_context = TravelContext(
        destination="Singapore",
        country="Singapore",
        duration_days=4,
    )

    # ---------------------------------------------------------
    # MCP client
    # ---------------------------------------------------------

    mcp_client = MCPClient()

    # MCP calls are async, while our current application
    # pipeline is synchronous.
    import asyncio

    tools = asyncio.run(
        mcp_client.get_tools()
    )

    # ---------------------------------------------------------
    # Tool selector
    # ---------------------------------------------------------

    selector = MCPToolSelector()

    user_message = (
        "What's the weather there?"
    )

    selection = selector.select_tool(
        user_message=user_message,
        travel_context=travel_context,
        tools=tools,
    )

    print("\nUSER MESSAGE")
    print("=" * 70)
    print(user_message)

    print("\nTRAVEL CONTEXT")
    print("=" * 70)
    print(travel_context.to_dict())

    print("\nMCP TOOL SELECTION")
    print("=" * 70)
    print(selection)


if __name__ == "__main__":
    main()
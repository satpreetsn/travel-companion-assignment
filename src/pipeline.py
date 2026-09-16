import asyncio

from context.manager import (
    TravelContext,
    extract_context,
    contextualize_query,
)

from generation.answer import generate_answer

from retrieval.retriever import Retriever

from travel_mcp.client import MCPClient
from travel_mcp.tool_selector import MCPToolSelector
from travel_mcp.request_router import RequestRouter


class TravelCompanionPipeline:

    def __init__(self):

        self.context = TravelContext()

        self.retriever = Retriever()

        self.mcp_client = MCPClient()

        self.mcp_tool_selector = MCPToolSelector()

        self.request_router = RequestRouter()

    async def process(
        self,
        user_message: str,
        top_k: int = 5,
    ) -> dict:

        print("\n" + "=" * 70)
        print("USER MESSAGE")
        print("=" * 70)
        print(user_message)

        # ---------------------------------------------------------
        # 1. Extract context
        # ---------------------------------------------------------

        extracted_context = extract_context(
            user_message=user_message,
            travel_context=self.context,
        )

        print("\nEXTRACTED CONTEXT")
        print("-" * 70)
        print(extracted_context)

        # ---------------------------------------------------------
        # 2. Update travel context
        # ---------------------------------------------------------

        self.context.update(
            extracted_context
        )

        print("\nCURRENT TRAVEL CONTEXT")
        print("-" * 70)
        print(self.context.to_dict())

        # ---------------------------------------------------------
        # 3. Contextualize query
        # ---------------------------------------------------------

        standalone_query = contextualize_query(
            user_message=user_message,
            travel_context=self.context,
        )

        print("\nSTANDALONE QUERY")
        print("-" * 70)
        print(standalone_query)

        # ---------------------------------------------------------
        # 4. Discover MCP tools
        # ---------------------------------------------------------

        tools = await self.mcp_client.get_tools()

        print("\nAVAILABLE MCP TOOLS")
        print("-" * 70)

        for tool in tools:

            print(
                f"- {tool['name']}: "
                f"{tool.get('description', '')}"
            )

        # ---------------------------------------------------------
        # 5. Determine request route
        # ---------------------------------------------------------

        route = self.request_router.route(
            user_message=user_message,
            travel_context=self.context,
            tools=tools,
        )

        print("\nREQUEST ROUTE")
        print("-" * 70)
        print(route)

        # ---------------------------------------------------------
        # 6. MCP processing
        # ---------------------------------------------------------

        mcp_selection = {
            "use_mcp": False,
            "tool_name": None,
            "arguments": {},
            "confidence": 0.0,
        }

        mcp_result = None

        if route["route"] in {
            "mcp",
            "both",
        }:

            # -----------------------------------------------------
            # Select MCP tool
            # -----------------------------------------------------

            mcp_selection = (
                self.mcp_tool_selector.select_tool(
                    user_message=user_message,
                    travel_context=self.context,
                    tools=tools,
                )
            )

            print("\nMCP TOOL SELECTION")
            print("-" * 70)
            print(mcp_selection)

            # -----------------------------------------------------
            # Execute MCP tool
            # -----------------------------------------------------

            if mcp_selection["use_mcp"]:

                tool_name = (
                    mcp_selection["tool_name"]
                )

                arguments = (
                    mcp_selection["arguments"]
                )

                print("\nMCP TOOL EXECUTION")
                print("-" * 70)
                print(
                    f"Tool: {tool_name}"
                )
                print(
                    f"Arguments: {arguments}"
                )

                mcp_result = (
                    await self.mcp_client.call_tool(
                        tool_name=tool_name,
                        arguments=arguments,
                    )
                )

                print("\nMCP TOOL RESULT")
                print("-" * 70)
                print(mcp_result)

            else:

                print("\nMCP TOOL EXECUTION")
                print("-" * 70)
                print(
                    "MCP was requested by the router, "
                    "but no suitable MCP tool was selected."
                )

        else:

            print("\nMCP TOOL EXECUTION")
            print("-" * 70)
            print("Skipped because route does not require MCP.")

        # ---------------------------------------------------------
        # 7. RAG retrieval
        # ---------------------------------------------------------

        results = []

        if route["route"] in {
            "rag",
            "both",
        }:

            results = self.retriever.retrieve(
                query=standalone_query,
                top_k=top_k,
                destination=self.context.destination,
            )

            print("\nRETRIEVED DOCUMENTS")
            print("-" * 70)
            print(
                f"Number of results: {len(results)}"
            )

            for index, result in enumerate(
                results,
                start=1,
            ):

                print(
                    "\n" + "." * 70
                )

                print(
                    f"RESULT {index}"
                )

                print(
                    "." * 70
                )

                print(
                    f"Source: {result['source']}"
                )

                print(
                    f"Page: {result['page']}"
                )

                print(
                    f"Destination: "
                    f"{result['destination']}"
                )

                print(
                    f"Distance: "
                    f"{result['distance']}"
                )

                print("\nTEXT:")

                print(
                    result["text"]
                )

        else:

            print("\nRETRIEVED DOCUMENTS")
            print("-" * 70)
            print(
                "Skipped because route does not require RAG."
            )

        # ---------------------------------------------------------
        # 8. Generate final answer
        # ---------------------------------------------------------

        answer = generate_answer(
            user_message=user_message,
            travel_context=self.context,
            retrieved_documents=results,
            mcp_result=mcp_result,
        )

        print("\nFINAL ANSWER")
        print("=" * 70)
        print(answer)

        # ---------------------------------------------------------
        # 9. Return complete result
        # ---------------------------------------------------------

        return {
            "user_message": user_message,
            "extracted_context": extracted_context,
            "context": self.context.to_dict(),
            "standalone_query": standalone_query,
            "route": route,
            "mcp_selection": mcp_selection,
            "mcp_result": mcp_result,
            "results": results,
            "answer": answer,
        }


async def main():

    pipeline = TravelCompanionPipeline()

    print("\nTravel Companion")
    print("Type 'exit' or 'quit' to stop.")

    while True:

        user_message = input(
            "\nYou: "
        ).strip()

        if not user_message:
            continue

        if user_message.lower() in {
            "exit",
            "quit",
        }:
            break

        await pipeline.process(
            user_message=user_message,
            top_k=5,
        )


if __name__ == "__main__":
    asyncio.run(main())
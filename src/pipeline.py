import logging

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


logger = logging.getLogger(__name__)


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

        logger.info("\n" + "=" * 70)
        logger.info("USER MESSAGE")
        logger.info("=" * 70)
        logger.info(user_message)

        # ---------------------------------------------------------
        # 1. Extract context
        # ---------------------------------------------------------

        extracted_context = extract_context(
            user_message=user_message,
            travel_context=self.context,
        )

        logger.info("\nEXTRACTED CONTEXT")
        logger.info("-" * 70)
        logger.info(extracted_context)

        # ---------------------------------------------------------
        # 2. Update travel context
        # ---------------------------------------------------------

        self.context.update(
            extracted_context
        )

        logger.info("\nCURRENT TRAVEL CONTEXT")
        logger.info("-" * 70)
        logger.info(self.context.to_dict())

        # ---------------------------------------------------------
        # 3. Contextualize query
        # ---------------------------------------------------------

        standalone_query = contextualize_query(
            user_message=user_message,
            travel_context=self.context,
        )

        logger.info("\nSTANDALONE QUERY")
        logger.info("-" * 70)
        logger.info(standalone_query)

        # ---------------------------------------------------------
        # 4. Discover MCP tools
        # ---------------------------------------------------------

        tools = await self.mcp_client.get_tools()

        logger.info("\nAVAILABLE MCP TOOLS")
        logger.info("-" * 70)

        for tool in tools:

            logger.info(
                "- %s: %s",
                tool["name"],
                tool.get("description", ""),
            )

        # ---------------------------------------------------------
        # 5. Determine request route
        # ---------------------------------------------------------

        route = self.request_router.route(
            user_message=user_message,
            travel_context=self.context,
            tools=tools,
        )

        logger.info("\nREQUEST ROUTE")
        logger.info("-" * 70)
        logger.info(route)

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

            logger.info("\nMCP TOOL SELECTION")
            logger.info("-" * 70)
            logger.info(mcp_selection)

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

                logger.info("\nMCP TOOL EXECUTION")
                logger.info("-" * 70)

                logger.info(
                    "Tool: %s",
                    tool_name,
                )

                logger.info(
                    "Arguments: %s",
                    arguments,
                )

                mcp_result = (
                    await self.mcp_client.call_tool(
                        tool_name=tool_name,
                        arguments=arguments,
                    )
                )

                logger.info("\nMCP TOOL RESULT")
                logger.info("-" * 70)
                logger.info(mcp_result)

            else:

                logger.info("\nMCP TOOL EXECUTION")
                logger.info("-" * 70)
                logger.info(
                    "MCP was requested by the router, "
                    "but no suitable MCP tool was selected."
                )

        else:

            logger.info("\nMCP TOOL EXECUTION")
            logger.info("-" * 70)
            logger.info(
                "Skipped because route does not require MCP."
            )

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

            logger.info("\nRETRIEVED DOCUMENTS")
            logger.info("-" * 70)

            logger.info(
                "Number of results: %d",
                len(results),
            )

            for index, result in enumerate(
                results,
                start=1,
            ):

                logger.info(
                    "\n%s",
                    "." * 70,
                )

                logger.info(
                    "RESULT %d",
                    index,
                )

                logger.info(
                    "%s",
                    "." * 70,
                )

                logger.info(
                    "Source: %s",
                    result["source"],
                )

                logger.info(
                    "Page: %s",
                    result["page"],
                )

                logger.info(
                    "Destination: %s",
                    result["destination"],
                )

                logger.info(
                    "Distance: %s",
                    result["distance"],
                )

                logger.info("\nTEXT:")

                logger.info(
                    result["text"]
                )

        else:

            logger.info("\nRETRIEVED DOCUMENTS")
            logger.info("-" * 70)
            logger.info(
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
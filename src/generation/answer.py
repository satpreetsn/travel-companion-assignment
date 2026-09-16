from typing import Any

from context.manager import TravelContext
from generation.llm import get_llm


def _format_documents(
    retrieved_documents: list[dict[str, Any]],
) -> str:
    """
    Format retrieved RAG documents for the LLM prompt.
    """

    if not retrieved_documents:
        return "No relevant documents were retrieved."

    formatted_documents = []

    for index, document in enumerate(
        retrieved_documents,
        start=1,
    ):
        formatted_documents.append(
            f"""
Document {index}

Source: {document.get("source", "Unknown")}
Page: {document.get("page", "Unknown")}
Destination: {document.get("destination", "Unknown")}

Content:
{document.get("text", "")}
"""
        )

    return "\n".join(formatted_documents)


def _format_mcp_result(
    mcp_result: Any,
) -> str:
    """
    Format the MCP result for the answer-generation prompt.
    """

    if mcp_result is None:
        return "No MCP tool was used."

    return str(mcp_result)


def generate_answer(
    user_message: str,
    travel_context: TravelContext,
    retrieved_documents: list[dict[str, Any]],
    mcp_result: Any = None,
) -> str:
    """
    Generate the final answer using:

    - user message
    - travel context
    - retrieved RAG documents
    - MCP tool result

    This function does not modify TravelContext.
    """

    llm = get_llm()

    documents = _format_documents(
        retrieved_documents
    )

    formatted_mcp_result = _format_mcp_result(
        mcp_result
    )

    prompt = f"""
You are a helpful and conversational travel assistant.

Answer the user's question using the available information.

TRAVEL CONTEXT
--------------
{travel_context.to_prompt()}


USER QUESTION
-------------
{user_message}


MCP TOOL RESULT
---------------
{formatted_mcp_result}


RETRIEVED KNOWLEDGE-BASE DOCUMENTS
-----------------------------------
{documents}


INSTRUCTIONS
------------

1. Answer the user's question directly.

2. When an MCP tool result is available, treat it as the
   primary source for information provided by that tool.

3. Use the retrieved knowledge-base documents for travel
   information contained in the knowledge base.

4. Use the travel context to understand conversational
   references such as:
   - there
   - here
   - that place
   - the destination
   - during the trip

5. Do not invent facts that are not supported by:
   - the MCP result
   - retrieved documents
   - travel context

6. If an MCP result is available and contains the requested
   information, use it in the answer.

7. If the MCP result reports an error or unavailable data,
   clearly explain that the requested current information
   could not be obtained.

8. If the knowledge-base documents do not contain enough
   information for a knowledge-base question, clearly say
   that the available knowledge base does not provide enough
   information.

9. Do not mention internal implementation details such as:
   - MCP
   - embeddings
   - ChromaDB
   - vector database
   - retrieval
   - context extraction
   - prompt
   - LLM

10. Give a natural and useful answer rather than simply
    repeating the raw tool result.

11. Use bullet points when they make the answer easier
    to read.

12. Return ONLY the final answer to the user.
"""

    response = llm.invoke(prompt)

    answer = response.content.strip()

    if not answer:
        raise ValueError(
            "Answer generation returned an empty response."
        )

    return answer
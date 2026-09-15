from context.manager import (
    TravelContext,
    extract_context,
    contextualize_query,
)


context = TravelContext()


queries = [
    "I am planning a 4 day trip to Singapore.",
    "What should I see there?",
    "Actually, let's go to Bali instead.",
    "What are the best beaches there?",
]


for query in queries:

    print("\nQUERY:")
    print(query)

    extracted = extract_context(
        query,
        context,
    )

    print("\nEXTRACTED:")
    print(extracted)

    context.update(extracted)

    print("\nCONTEXT:")
    print(context.to_dict())

    standalone_query = contextualize_query(
        query,
        context,
    )

    print("\nSTANDALONE QUERY:")
    print(standalone_query)
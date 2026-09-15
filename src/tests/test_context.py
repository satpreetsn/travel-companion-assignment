from context.manager import (
    TravelContext,
    extract_context,
)


def main():

    context = TravelContext()

    # ---------------------------------------------------------
    # First query
    # ---------------------------------------------------------

    query = "I am planning a 4 day trip to Singapore."

    result = extract_context(
        user_message=query,
        travel_context=context,
    )

    print("\nQUERY:")
    print(query)

    print("\nEXTRACTED:")
    print(result)

    context.update(result)

    print("\nCONTEXT:")
    print(context.to_dict())

    # ---------------------------------------------------------
    # Follow-up
    # ---------------------------------------------------------

    query = "What should I see there?"

    result = extract_context(
        user_message=query,
        travel_context=context,
    )

    print("\nQUERY:")
    print(query)

    print("\nEXTRACTED:")
    print(result)

    context.update(result)

    print("\nCONTEXT:")
    print(context.to_dict())

    # ---------------------------------------------------------
    # Destination change
    # ---------------------------------------------------------

    query = "Actually, let's go to Bali instead."

    result = extract_context(
        user_message=query,
        travel_context=context,
    )

    print("\nQUERY:")
    print(query)

    print("\nEXTRACTED:")
    print(result)

    context.update(result)

    print("\nCONTEXT:")
    print(context.to_dict())


if __name__ == "__main__":
    main()
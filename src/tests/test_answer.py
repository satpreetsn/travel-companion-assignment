from context.manager import TravelContext
from generation.answer import generate_answer


context = TravelContext(
    destination="Singapore",
    country="Singapore",
    duration_days=4,
)

documents = [
    {
        "text": """
        Singapore has many attractions including Marina Bay Sands,
        Gardens by the Bay, Sentosa Island, and the Singapore Zoo.
        """,
        "source": "Singapore Tourism Guide.pdf",
        "page": 10,
        "destination": "Singapore",
        "distance": 0.25,
    },
    {
        "text": """
        Gardens by the Bay is a major attraction in Singapore
        featuring large Supertree structures and conservatories.
        """,
        "source": "Singapore Travel Guide.pdf",
        "page": 18,
        "destination": "Singapore",
        "distance": 0.31,
    },
]


answer = generate_answer(
    user_message="What should I see there?",
    travel_context=context,
    retrieved_documents=documents,
)

print("\nFINAL ANSWER")
print("=" * 60)
print(answer)
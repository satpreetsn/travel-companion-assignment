from dataclasses import dataclass, field
from typing import Any
import json
import re

from generation.llm import get_llm


@dataclass
class TravelContext:

    destination: str | None = None
    country: str | None = None

    start_date: str | None = None
    end_date: str | None = None
    duration_days: int | None = None

    travelers: int | None = None
    budget: str | None = None

    interests: list[str] = field(default_factory=list)
    preferences: list[str] = field(default_factory=list)

    def update(self, new_context: dict[str, Any]) -> None:

        if not new_context:
            return

        destination_action = new_context.get(
            "destination_action",
            "none",
        )

        new_destination = new_context.get("destination")
        new_country = new_context.get("country")

        # ---------------------------------------------------------
        # Destination
        # ---------------------------------------------------------

        if destination_action in {"new", "change"}:

            if new_destination:
                self.destination = new_destination

            if new_country:
                self.country = new_country

        elif destination_action == "same":

            if not self.destination and new_destination:
                self.destination = new_destination

            if not self.country and new_country:
                self.country = new_country

        # ---------------------------------------------------------
        # Other scalar fields
        # ---------------------------------------------------------

        scalar_fields = [
            "start_date",
            "end_date",
            "duration_days",
            "travelers",
            "budget",
        ]

        for field_name in scalar_fields:

            value = new_context.get(field_name)

            if value is not None and value != "":
                setattr(self, field_name, value)

        # ---------------------------------------------------------
        # List fields
        # ---------------------------------------------------------

        for field_name in [
            "interests",
            "preferences",
        ]:

            values = new_context.get(field_name)

            if not values:
                continue

            if isinstance(values, str):
                values = [values]

            current_values = getattr(
                self,
                field_name,
            )

            for value in values:

                if value and value not in current_values:
                    current_values.append(value)

    def to_dict(self) -> dict[str, Any]:

        return {
            "destination": self.destination,
            "country": self.country,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "duration_days": self.duration_days,
            "travelers": self.travelers,
            "budget": self.budget,
            "interests": self.interests,
            "preferences": self.preferences,
        }

    def to_prompt(self) -> str:

        context = self.to_dict()

        populated = {
            key: value
            for key, value in context.items()
            if value not in (None, "", [], {})
        }

        if not populated:
            return "No travel context is currently known."

        return "\n".join(
            f"{key}: {value}"
            for key, value in populated.items()
        )


def extract_context(
    user_message: str,
    travel_context: TravelContext,
) -> dict[str, Any]:
    """
    Extract travel context from the latest user message.

    Does NOT modify TravelContext.
    """

    llm = get_llm()

    prompt = f"""
You are the context extraction component of a travel assistant.

Your ONLY job is to extract travel context from the user's latest message.

Do NOT answer the user's question.

Determine whether the user:

1. introduces a new destination
2. changes the existing destination
3. continues talking about the existing destination
4. provides no destination information

Current travel context:

{travel_context.to_prompt()}

Latest user message:

{user_message}


Return ONLY valid JSON using exactly this structure:

{{
    "destination": null,
    "country": null,
    "destination_action": "none",

    "start_date": null,
    "end_date": null,
    "duration_days": null,

    "travelers": null,
    "budget": null,

    "interests": [],
    "preferences": [],

    "confidence": 0.0
}}


destination_action must be one of:

"new"
- The user introduces a destination and no destination
  was previously known.

"change"
- The user explicitly changes the existing destination.

"same"
- The user continues talking about the existing destination.
- This includes references such as:
  "there", "here", "that city", "the place", etc.

"none"
- No destination can be determined.

Examples:

Existing destination:
Singapore

User:
"What should I see there?"

Return:

{{
    "destination": "Singapore",
    "country": "Singapore",
    "destination_action": "same",
    "confidence": 0.95
}}

User:
"Actually, let's go to Bali instead."

Return:

{{
    "destination": "Bali",
    "country": "Indonesia",
    "destination_action": "change",
    "confidence": 0.98
}}

User:
"I am planning a 4 day trip to Singapore."

Return:

{{
    "destination": "Singapore",
    "country": "Singapore",
    "destination_action": "new",
    "duration_days": 4,
    "confidence": 0.98
}}

Rules:

- Never invent a destination.
- Do not infer a destination without evidence.
- Use the existing context to resolve references such as "there".
- confidence must be between 0 and 1.
"""

    response = llm.invoke(prompt)

    content = response.content.strip()

    # Remove markdown fences if Ollama returns them.
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
                f"Could not parse context extraction response:\n"
                f"{content}"
            )

        result = json.loads(match.group(0))

    # ---------------------------------------------------------
    # Validate destination action
    # ---------------------------------------------------------

    valid_actions = {
        "new",
        "change",
        "same",
        "none",
    }

    action = result.get(
        "destination_action",
        "none",
    )

    if action not in valid_actions:
        action = "none"

    result["destination_action"] = action

    # ---------------------------------------------------------
    # Validate confidence
    # ---------------------------------------------------------

    try:
        confidence = float(
            result.get("confidence", 0.0)
        )
    except (TypeError, ValueError):
        confidence = 0.0

    result["confidence"] = max(
        0.0,
        min(1.0, confidence),
    )

    return result

def contextualize_query(
    user_message: str,
    travel_context: TravelContext,
) -> str:
    """
    Convert the user's latest message into a standalone query
    using the current travel context.

    The function does not modify TravelContext.
    """

    llm = get_llm()

    prompt = f"""
        You are the query contextualization component of a travel assistant.

        Your task is to rewrite the user's latest message into a
        standalone search query that can be sent to a travel knowledge
        base.

        Use the existing travel context to resolve ambiguous references
        such as:

        - there
        - here
        - that city
        - this place
        - the destination
        - nearby
        - during the trip

        Do NOT answer the user's question.

        Do NOT add information that is not present in either:
        1. the user's message
        2. the existing travel context

        Preserve the user's original intent.

        Current travel context:

        {travel_context.to_prompt()}

        Latest user message:

        {user_message}

        Return ONLY the standalone query.

        Examples:

        Context:
        destination: Singapore
        country: Singapore
        duration_days: 4

        User:
        "What should I see there?"

        Output:
        What are the best places and attractions to see in Singapore
        during a 4-day trip?

        ---

        Context:
        destination: Singapore
        country: Singapore

        User:
        "How do I get around?"

        Output:
        How can I get around Singapore?

        ---

        Context:
        destination: Bali
        country: Indonesia
        duration_days: 4

        User:
        "What about beaches?"

        Output:
        What are the best beaches in Bali for a 4-day trip?

        ---

        Context:
        No travel context is currently known.

        User:
        "What are the best beaches?"

        Output:
        What are the best beaches?

        Rules:

        - Return only the rewritten query.
        - Do not provide an answer.
        - Do not explain your reasoning.
        - Do not introduce a destination that isn't in the context
        or user's message.
        - Keep the original intent of the user's question.
        """

    response = llm.invoke(prompt)
    query = response.content.strip()

    # Remove markdown formatting if the model adds it.
    query = re.sub(
        r"^```(?:text)?\s*",
        "",
        query,
        flags=re.IGNORECASE,
    )

    query = re.sub(
        r"\s*```$",
        "",
        query,
    )

    return query.strip()
import asyncio
import logging

from pipeline import TravelCompanionPipeline


logger = logging.getLogger(__name__)


class TerminalUI:
    """
    Cross-platform terminal interface for Travel Companion.

    The terminal UI is responsible only for:
    - user interaction
    - displaying the final assistant response
    - conversation commands

    Backend diagnostics are handled through logging.
    """

    def __init__(self):
        self.pipeline = TravelCompanionPipeline()

    def display_welcome(self):
        print()
        print("=" * 70)
        print("                    TRAVEL COMPANION")
        print("=" * 70)
        print()
        print("Your local AI travel assistant")
        print()
        print("Commands:")
        print("  clear         Start a new conversation")
        print("  exit          Exit the application")
        print()

    def display_answer(self, answer: str):
        print()
        print("Assistant")
        print("-" * 70)
        print(answer)
        print()

    def clear_conversation(self):
        self.pipeline = TravelCompanionPipeline()

        print()
        print("Conversation cleared.")
        print("Travel context has been reset.")
        print()

    async def run(self):

        self.display_welcome()

        while True:

            try:
                user_message = input("You: ").strip()

            except (KeyboardInterrupt, EOFError):

                print()
                print("Goodbye!")
                break

            if not user_message:
                continue

            command = user_message.lower()

            if command in {"exit", "quit"}:

                print()
                print("Goodbye!")
                break

            if command == "clear":

                self.clear_conversation()
                continue

            try:

                result = await self.pipeline.process(
                    user_message=user_message,
                    top_k=5,
                )

                self.display_answer(
                    result["answer"]
                )

            except Exception:

                logger.exception(
                    "Error while processing user request"
                )

                print()
                print("Assistant")
                print("-" * 70)
                print(
                    "Sorry, I encountered an error "
                    "while processing your request."
                )
                print()


async def main():
    ui = TerminalUI()
    await ui.run()


if __name__ == "__main__":
    asyncio.run(main())
import logging

from config import setup_logging
from Orchestrator import Orchestrator

logger = logging.getLogger("main")


def main():
    setup_logging()
    orchestrator = Orchestrator()
    print("Bangkok Public Transport Assistant")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        logger.info('User input: "%s"', user_input)
        response = orchestrator.handle(user_input)
        logger.info("Assistant response delivered (%d chars)", len(response))
        print(f"\nAssistant:\n{response}\n")


if __name__ == "__main__":
    main()

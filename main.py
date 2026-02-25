from Orchestrator import Orchestrator


def main():
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

        response = orchestrator.handle(user_input)
        print(f"\nAssistant:\n{response}\n")


if __name__ == "__main__":
    main()

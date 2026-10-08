from rag_chain import answer_question


def main():
    print("MediKnow AI")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Ask MediKnow: ")

        if query.lower() == "exit":
            print("Goodbye!")
            break

        answer = answer_question(query)

        print("\nAnswer:")
        print(answer)
        print()


if __name__ == "__main__":
    main()
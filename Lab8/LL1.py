from task1_make_ll1_grammar import validate_and_report_ll1_grammar
from task5_ll1_parser import LL1Parser


def main():
    try:
        validate_and_report_ll1_grammar()
        parser = LL1Parser()
    except Exception as error:
        print(f"Setup failed: {error}")
        return

    print("\nEnter input string:")
    user_input = input("> ").strip()

    trace_choice = input("Show Algorithm 4.34 trace? (y/n): ").strip().lower()
    trace = trace_choice == "y"

    accepted, derivation, error_message = parser.parse_string(user_input, trace=trace)

    if accepted:
        print("\nValid")
    else:
        print("\nInvalid")
        print(f"Reason: {error_message}")

    print("\nLeftmost derivation productions used:")
    if not derivation:
        print("(none)")
    else:
        for lhs, rhs in derivation:
            print(f"{lhs} -> {' '.join(rhs)}")


if __name__ == "__main__":
    main()

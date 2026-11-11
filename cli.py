"""Command-line demo (works in Google Colab or any terminal without Streamlit).

    python cli.py                      # interactive menu
    python cli.py pin 1234             # one-shot check
    python cli.py email a@b.co
    python cli.py password Secure@123
"""
import sys

from automata import build_email_dfa, build_password_dfa, build_pin_dfa

MACHINES = {"password": build_password_dfa(), "email": build_email_dfa(), "pin": build_pin_dfa()}


def check(kind, text):
    dfa = MACHINES[kind]
    result = dfa.run(text)
    print(f"\n{dfa.name}   input = {text!r}")
    for s in result.steps:
        print(f"  step {s.index:>2}: δ({s.source}, {s.symbol}) = {s.target}    [read {s.char!r}]")
    verdict = "ACCEPTED" if result.accepted else "REJECTED"
    print(f"  final state: {result.final_state}  →  {verdict}\n")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] in MACHINES:
        check(sys.argv[1], sys.argv[2])
    else:
        while True:
            kind = input("Validator [password / email / pin / quit]: ").strip().lower()
            if kind in ("quit", "q", ""):
                break
            if kind not in MACHINES:
                print("Unknown validator.")
                continue
            check(kind, input("String to check: "))

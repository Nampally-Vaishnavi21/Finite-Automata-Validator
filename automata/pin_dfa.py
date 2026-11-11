"""ATM PIN format validator.

Language:  L_pin = { w ∈ {0,…,9}* : |w| = 4 or |w| = 6 }
Regular expression:  D^4 + D^6     where D = (0+1+…+9)

The DFA simply COUNTS digits.  Counting up to a fixed number (6) needs only a
fixed number of states, which is why a finite automaton is enough here.
"""
from .dfa import DFA

SYMBOLS = ["digit", "other"]


def classify(ch):
    # str.isdigit() is True for some non-ASCII digits too, so test the range directly.
    return "digit" if "0" <= ch <= "9" else "other"


def build_pin_dfa():
    states = ["q0", "q1", "q2", "q3", "q4", "q5", "q6", "qd"]
    delta = {}
    # Reading a digit moves one step along the counting chain q0 → q1 → … → q6.
    for i in range(6):
        delta[(f"q{i}", "digit")] = f"q{i + 1}"
    # A 7th digit, or any non-digit anywhere, is filled in automatically as → qd.
    state_info = {
        "q0": "Start. No digit read yet.",
        "q1": "Exactly 1 digit read.",
        "q2": "Exactly 2 digits read.",
        "q3": "Exactly 3 digits read.",
        "q4": "Exactly 4 digits read - a valid 4-digit PIN (accepting).",
        "q5": "Exactly 5 digits read - not a valid length.",
        "q6": "Exactly 6 digits read - a valid 6-digit PIN (accepting).",
        "qd": "Trap state: a non-digit was read or there are more than 6 digits.",
    }
    symbol_info = {
        "digit": "0 1 2 3 4 5 6 7 8 9",
        "other": "any other character (letters, spaces, symbols)",
    }
    return DFA("ATM PIN DFA", states, SYMBOLS, delta, "q0", {"q4", "q6"},
               classify, "qd", state_info, symbol_info)


INFO = {
    "title": "ATM PIN Verification",
    "problem": "An ATM keypad must check that the entered PIN has a legal format "
               "before it is sent to the bank for verification. A legal PIN is made "
               "only of digits and is exactly 4 or exactly 6 digits long.",
    "alphabet": "Σ = {0, 1, …, 9} ∪ {other}, where `other` stands for every non-digit "
                "character. The language itself uses only digits; `other` is included so "
                "that δ is total and wrong characters are rejected explicitly.",
    "language": "L_pin = { w ∈ {0,…,9}* : |w| = 4 or |w| = 6 }",
    "regex": "D⁴ + D⁶,  where D = (0 + 1 + … + 9)",
    "rules": [
        "Only the digits 0-9 are allowed.",
        "Length must be exactly 4 or exactly 6.",
        "Lengths 0-3, 5 and 7 or more are rejected.",
        "Letters, spaces and special characters are rejected.",
    ],
    "assumptions": [
        "Leading zeros are allowed (0042 is a legal PIN format).",
        "The automaton checks FORMAT only. It does not know the customer's real PIN.",
    ],
    "semantic": "Whether the PIN is the correct PIN for the inserted card, how many wrong "
                "attempts have been made, and whether the PIN is a weak choice such as 1234 "
                "are business rules. They need the bank's database and counters that persist "
                "between attempts - information that is not in the input string, so no finite "
                "automaton over the PIN alone can decide them.",
    "start_final": "q0 is the start state (nothing read). q4 and q6 are final because the "
                   "machine is in q4 exactly when 4 digits have been read and in q6 exactly when "
                   "6 digits have been read. q5 is NOT final, which is what rejects 5-digit PINs.",
}

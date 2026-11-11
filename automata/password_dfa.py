"""Password format validator.

Language (default minimum length n = 8):
    L_pwd = { w ∈ Σ* : |w| ≥ 8, w has an uppercase letter, a lowercase letter,
                        a digit and a special character }

L_pwd is the INTERSECTION of five simple regular languages:
    L_U (contains uppercase)   L_L (contains lowercase)   L_D (contains digit)
    L_S (contains special)     L_len (length ≥ 8)

Each of them has a tiny DFA.  Regular languages are closed under intersection,
and the proof is the PRODUCT CONSTRUCTION: run all five DFAs at the same time
and accept only if all five accept.  A state of the product DFA is therefore a
tuple (u, l, d, s, k):  four yes/no flags and a length counter that stops at 8.
"""
import string
from .dfa import DFA

SYMBOLS = ["upper", "lower", "digit", "special", "other"]
SPECIALS = string.punctuation          # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
FLAG_ORDER = ["upper", "lower", "digit", "special"]
FLAG_LETTER = {"upper": "U", "lower": "L", "digit": "D", "special": "S"}
TRAP = "qd"


def classify(ch):
    if "A" <= ch <= "Z":
        return "upper"
    if "a" <= ch <= "z":
        return "lower"
    if "0" <= ch <= "9":
        return "digit"
    if ch in SPECIALS:
        return "special"
    return "other"                      # space, tab, non-ASCII … not allowed


def state_name(flags, count, min_len):
    """Readable name of a product state, e.g. 'UL--|5' or 'ULDS|8+'."""
    mask = "".join(FLAG_LETTER[f] if on else "-" for f, on in zip(FLAG_ORDER, flags))
    return f"{mask}|{count}{'+' if count == min_len else ''}"


def build_password_dfa(min_len=8):
    """Build the product DFA by exploring only the states reachable from the start."""
    start = ((False, False, False, False), 0)
    names = {start: state_name(*start, min_len)}
    delta = {}
    todo = [start]
    while todo:
        flags, count = todo.pop()
        for sym in FLAG_ORDER:
            # Component moves: the flag of the symbol just read switches ON (and
            # stays on), and the length counter goes up until it reaches min_len.
            new_flags = tuple(on or (f == sym) for f, on in zip(FLAG_ORDER, flags))
            new_state = (new_flags, min(count + 1, min_len))
            if new_state not in names:
                names[new_state] = state_name(*new_state, min_len)
                todo.append(new_state)
            delta[(names[(flags, count)], sym)] = names[new_state]

    ordered = sorted(names, key=lambda s: (s[1], sum(s[0]), [not x for x in s[0]]))
    states = [names[s] for s in ordered] + [TRAP]
    final = names[((True, True, True, True), min_len)]

    state_info = {TRAP: "Trap state: a character outside the alphabet (e.g. a space) was read."}
    for (flags, count), name in names.items():
        seen = [f for f, on in zip(FLAG_ORDER, flags) if on] or ["nothing"]
        length = f"at least {min_len}" if count == min_len else str(count)
        state_info[name] = f"Seen so far: {', '.join(seen)}; characters read: {length}."
    symbol_info = {
        "upper": "A-Z", "lower": "a-z", "digit": "0-9",
        "special": "any of " + SPECIALS,
        "other": "anything else (space, tab, non-ASCII characters)",
    }
    return DFA("Password DFA (product)", states, SYMBOLS, delta, names[start], {final},
               classify, TRAP, state_info, symbol_info)


def conditions(text, min_len=8):
    """Which of the five conditions hold - read off the product state, not re-computed."""
    dfa = build_password_dfa(min_len)
    result = dfa.run(text)
    state = result.final_state
    if state == TRAP:
        mask, count_reached = "----", False
    else:
        mask, count = state.split("|")
        count_reached = count.endswith("+")
    report = [
        (f"At least {min_len} characters", count_reached),
        ("An uppercase letter (A-Z)", "U" in mask),
        ("A lowercase letter (a-z)", "L" in mask),
        ("A digit (0-9)", "D" in mask),
        ("A special character", "S" in mask),
    ]
    return result, report, state == TRAP


# ---------------------------------------------------------------- diagrams
_DOT_HEAD = (
    'digraph G {{ rankdir=LR; bgcolor="transparent"; pad=0.2; label="{title}"; labelloc=t; '
    'fontname="Helvetica"; fontsize=12; '
    'node [fontname="Helvetica", fontsize=11, style=filled, fillcolor="#F4F7FB", color="#1F3A5F"]; '
    'edge [fontname="Helvetica", fontsize=10, color="#5B6B7F", arrowsize=0.7]; '
    's [shape=point, width=0.12];'
)


def contains_dot(kind):
    """2-state DFA for 'the string contains at least one <kind> character'."""
    others = ", ".join(s for s in FLAG_ORDER if s != kind)
    return (_DOT_HEAD.format(title=f"contains {kind}") +
            f' no [label="no", shape=circle]; yes [label="yes", shape=doublecircle]; s -> no;'
            f' no -> no [label="{others}"]; no -> yes [label="{kind}"];'
            f' yes -> yes [label="any"]; }}')


def length_dot(min_len=8):
    """Counter DFA for 'the string has at least min_len characters'."""
    parts = [_DOT_HEAD.format(title=f"length ≥ {min_len}"), "s -> 0;"]
    for i in range(min_len):
        parts.append(f'{i} [shape=circle]; {i} -> {i + 1} [label="any"];')
    parts.append(f'{min_len} [label="{min_len}+", shape=doublecircle]; '
                 f'{min_len} -> {min_len} [label="any"]; }}')
    return " ".join(parts)


INFO = {
    "title": "Password Verification",
    "problem": "A sign-up form must check that a new password follows the organisation's "
               "format policy before it is stored. The policy asks for a minimum length and a "
               "mix of character types.",
    "alphabet": "Σ = U ∪ L ∪ D ∪ S, where U = {A-Z}, L = {a-z}, D = {0-9} and S = the 32 ASCII "
                "punctuation characters. Any other character (space, tab, non-ASCII) is classed "
                "as `other` and rejected.",
    "language": "L_pwd = { w ∈ Σ* : |w| ≥ 8 and w contains at least one symbol from each of U, L, D, S }",
    "regex": "L_pwd = L_U ∩ L_L ∩ L_D ∩ L_S ∩ L_len,  e.g. L_U = Σ* U Σ*  and  L_len = Σ⁸ Σ*",
    "rules": [
        "Minimum length: 8 characters.",
        "At least one uppercase letter.",
        "At least one lowercase letter.",
        "At least one digit.",
        "At least one special character (ASCII punctuation).",
        "Spaces and non-ASCII characters are not allowed.",
    ],
    "assumptions": [
        "There is no maximum length (a maximum would only add more counter states).",
        "The order of the characters does not matter.",
        "The automaton checks the FORMAT policy only.",
    ],
    "semantic": "Checking that a typed password MATCHES the stored one, that it is not in a "
                "list of leaked passwords, not equal to the username and not a reused old "
                "password are business rules. They need hashing and database lookups, so they "
                "are handled by extra processing after the automaton.",
    "start_final": "The start state is ----|0 (no class seen, zero characters read). The only "
                   "final state is ULDS|8+: all four flags are on and at least 8 characters "
                   "have been read. Every other state is missing at least one condition.",
}

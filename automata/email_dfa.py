"""Email format validator (simplified grammar, NOT full RFC 5322).

Simplified syntax accepted by this project
    email  = local "@" domain
    local  = word ( sep word )*            sep is one of  .  _  -
    domain = label ( "." label )* "." tld
    label  = word ( "-" word )*
    tld    = letter letter+                (letters only, at least 2)
    word   = (letter | digit)+

Because every rule above only needs to remember "what kind of character came
last" and "which part of the address am I in", a finite number of states is
enough - the language is regular.
"""
from .dfa import DFA

SYMBOLS = ["letter", "digit", "dot", "hyphen", "underscore", "at", "other"]


def classify(ch):
    if "a" <= ch <= "z" or "A" <= ch <= "Z":
        return "letter"
    if "0" <= ch <= "9":
        return "digit"
    return {".": "dot", "-": "hyphen", "_": "underscore", "@": "at"}.get(ch, "other")


def build_email_dfa():
    states = ["q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "qd"]
    d = {}
    # ---- local part --------------------------------------------------------
    d[("q0", "letter")] = d[("q0", "digit")] = "q1"      # must start with letter/digit
    d[("q1", "letter")] = d[("q1", "digit")] = "q1"      # keep reading the word
    d[("q1", "dot")] = d[("q1", "hyphen")] = d[("q1", "underscore")] = "q2"   # one separator
    d[("q1", "at")] = "q3"                               # local part finished
    d[("q2", "letter")] = d[("q2", "digit")] = "q1"      # separator must be followed by letter/digit
    # ---- domain, before the first dot --------------------------------------
    d[("q3", "letter")] = d[("q3", "digit")] = "q4"      # domain must start with letter/digit
    d[("q4", "letter")] = d[("q4", "digit")] = "q4"
    d[("q4", "hyphen")] = "q5"                           # hyphen inside a label
    d[("q4", "dot")] = "q6"                              # first dot of the domain
    d[("q5", "letter")] = d[("q5", "digit")] = "q4"      # hyphen must be followed by letter/digit
    # ---- domain, after a dot (this label might be the extension) -----------
    d[("q6", "letter")] = "q7"                           # 1st letter of a possible extension
    d[("q6", "digit")] = "q9"                            # label with a digit: cannot be the extension
    d[("q7", "letter")] = "q8"                           # 2nd letter: now a valid extension
    d[("q8", "letter")] = "q8"                           # longer extension (com, info, …)
    for q in ("q7", "q8"):
        d[(q, "digit")] = "q9"                           # a digit spoils the extension
        d[(q, "hyphen")] = "q10"
        d[(q, "dot")] = "q6"                             # it was a sub-domain; start a new label
    d[("q9", "letter")] = d[("q9", "digit")] = "q9"
    d[("q9", "hyphen")] = "q10"
    d[("q9", "dot")] = "q6"
    d[("q10", "letter")] = d[("q10", "digit")] = "q9"    # hyphen must be followed by letter/digit

    state_info = {
        "q0": "Start. Nothing read yet.",
        "q1": "Inside the local part; last character was a letter/digit.",
        "q2": "Inside the local part; last character was a separator (. _ -). A letter/digit must follow.",
        "q3": "Just read '@'. The domain must begin with a letter/digit.",
        "q4": "Inside the first domain label (no dot seen yet); last character was a letter/digit.",
        "q5": "Inside the first domain label; last character was a hyphen.",
        "q6": "Just read a dot in the domain. A new label must begin.",
        "q7": "Label after a dot with exactly ONE letter so far (too short to be an extension).",
        "q8": "Label after a dot made of 2 or more letters only - a valid extension (accepting).",
        "q9": "Label after a dot that contains a digit or hyphen - valid as a sub-domain, not as an extension.",
        "q10": "Label after a dot; last character was a hyphen.",
        "qd": "Trap state: the syntax rules have been broken.",
    }
    symbol_info = {
        "letter": "a-z, A-Z",
        "digit": "0-9",
        "dot": ".",
        "hyphen": "-",
        "underscore": "_",
        "at": "@",
        "other": "any other character (space, #, !, …)",
    }
    return DFA("Email DFA", states, SYMBOLS, d, "q0", {"q8"},
               classify, "qd", state_info, symbol_info)


# The same language written as a regular expression.  It is used only by the
# unit tests to cross-check the DFA against an independent definition.
EQUIVALENT_REGEX = (
    r"[A-Za-z0-9]+([._-][A-Za-z0-9]+)*"            # local part
    r"@"
    r"[A-Za-z0-9]+(-[A-Za-z0-9]+)*"                # first label
    r"(\.[A-Za-z0-9]+(-[A-Za-z0-9]+)*)*"           # optional further labels
    r"\.[A-Za-z]{2,}"                              # extension
)

INFO = {
    "title": "Email Format Validator",
    "problem": "A registration form must reject text that is obviously not an email "
               "address (missing @, missing extension, double dots, …) before any further "
               "processing. We validate a clearly defined, simplified email syntax.",
    "alphabet": "Σ = {a-z, A-Z, 0-9, '.', '-', '_', '@'} ∪ {other}. Characters are grouped "
                "into the classes letter, digit, dot, hyphen, underscore, at, other.",
    "language": "L_email = { u@v.t : u is a local part, v is one or more dot-separated "
                "labels, t is 2 or more letters } as defined by the grammar below.",
    "regex": "W (S W)* @ W (- W)* ( . W (- W)* )* . A A⁺    with  W = (letter+digit)⁺,  "
             "S = ( . + _ + - ),  A = letter",
    "rules": [
        "Local part starts and ends with a letter or digit.",
        "Inside the local part the separators . _ - are allowed, but never two in a row.",
        "Exactly one @ symbol.",
        "Domain is made of labels separated by single dots; a label starts and ends "
        "with a letter/digit and may contain single hyphens.",
        "The domain has at least one dot.",
        "The extension (last label) has only letters and at least 2 of them.",
    ],
    "assumptions": [
        "This is a deliberately simplified syntax. It is NOT a complete RFC 5322 validator.",
        "Not supported: quoted local parts, the + tag, comments, IP-address domains, "
        "internationalised (non-ASCII) addresses and length limits.",
        "Upper- and lower-case letters are treated the same way.",
    ],
    "semantic": "The DFA cannot tell whether the domain really exists, whether the mailbox "
                "exists, or whether the person typing owns it. Those need a DNS lookup and a "
                "confirmation email - processing outside the string, beyond any automaton.",
    "start_final": "q0 is the start state. q8 is the only final state: the machine is in q8 "
                   "exactly when everything before was legal AND the current label after the "
                   "last dot consists of 2 or more letters, i.e. the string ends in a valid extension.",
    "grammar": [
        "email  → local @ domain",
        "local  → word | word sep local",
        "domain → label . tld | label . domain",
        "label  → word | word - label",
        "tld    → letter letter | letter tld",
        "word   → alnum | alnum word",
        "sep    → . | _ | -",
    ],
}

"""Generic Deterministic Finite Automaton (DFA).

A DFA is the 5-tuple  M = (Q, Σ, δ, q0, F):
    Q  - finite set of states
    Σ  - input alphabet
    δ  - transition function  δ : Q × Σ → Q
    q0 - start state
    F  - set of accepting (final) states

Real keyboards have ~95 printable characters, so drawing one arrow per character
is unreadable.  We therefore group characters into *symbol classes*
(e.g. every digit 0-9 behaves the same and is called `digit`).  The `classify`
function maps a raw character to its class, and δ is defined on classes.
This is only a notational shortcut - the machine is still an ordinary DFA.
"""
from dataclasses import dataclass


@dataclass
class Step:
    """One move of the automaton:  δ(source, symbol) = target."""
    index: int      # position of the character in the input (1-based)
    char: str       # the raw character that was read
    symbol: str     # the symbol class the character belongs to
    source: str     # state before reading
    target: str     # state after reading


@dataclass
class RunResult:
    accepted: bool
    final_state: str
    steps: list     # list[Step]

    @property
    def path(self):
        """Sequence of visited states, starting with the start state."""
        if not self.steps:
            return [self.final_state]
        return [self.steps[0].source] + [s.target for s in self.steps]


class DFA:
    def __init__(self, name, states, symbols, delta, start, finals,
                 classify, trap, state_info=None, symbol_info=None):
        self.name = name
        self.states = list(states)          # Q (ordered for display)
        self.symbols = list(symbols)        # Σ as symbol classes
        self.start = start                  # q0
        self.finals = set(finals)           # F
        self.classify = classify            # char -> symbol class
        self.trap = trap                    # dead / trap state
        self.state_info = state_info or {}  # state -> meaning (for viva/docs)
        self.symbol_info = symbol_info or {}

        # Make δ TOTAL: every (state, symbol) pair that the designer left out
        # goes to the trap state.  A DFA must have exactly one move per pair.
        self.delta = {}
        for q in self.states:
            for a in self.symbols:
                self.delta[(q, a)] = delta.get((q, a), trap)
        self._check()

    def _check(self):
        """Sanity checks so that a wrong table is caught immediately."""
        assert self.start in self.states, "start state must be in Q"
        assert self.finals <= set(self.states), "F must be a subset of Q"
        assert self.trap in self.states, "trap state must be in Q"
        for (q, a), target in self.delta.items():
            assert target in self.states, f"δ({q},{a}) leaves Q"

    # ---------------------------------------------------------------- running
    def run(self, text):
        """Feed `text` to the DFA one character at a time and record each move."""
        state = self.start
        steps = []
        for i, ch in enumerate(text, start=1):
            symbol = self.classify(ch)
            target = self.delta[(state, symbol)]
            steps.append(Step(i, ch, symbol, state, target))
            state = target
        return RunResult(state in self.finals, state, steps)

    def accepts(self, text):
        return self.run(text).accepted

    # ---------------------------------------------------------------- display
    def transition_table(self, include_trap=True):
        """Rows of the transition table: one row per state, one column per symbol."""
        rows = []
        for q in self.states:
            if q == self.trap and not include_trap:
                continue
            label = q
            if q == self.start:
                label = "→ " + label
            if q in self.finals:
                label = "* " + label
            row = {"State": label}
            for a in self.symbols:
                row[a] = self.delta[(q, a)]
            rows.append(row)
        return rows

    def to_dot(self, path=None, show_trap=False, rankdir="LR"):
        """Graphviz DOT source of the state diagram.

        path      - optional list of visited states; those states/edges are highlighted
        show_trap - draw the trap state and all arrows into it (usually clutter)
        """
        path = path or []
        visited = set(path)
        used_edges = set(zip(path, path[1:]))
        current = path[-1] if path else None

        lines = [
            "digraph DFA {",
            f"  rankdir={rankdir}; bgcolor=\"transparent\"; pad=0.2; nodesep=0.45; ranksep=0.55;",
            '  node [fontname="Helvetica", fontsize=12, style=filled, fillcolor="#F4F7FB", color="#1F3A5F", penwidth=1.3];',
            '  edge [fontname="Helvetica", fontsize=10, color="#5B6B7F", arrowsize=0.7];',
            '  __start [shape=point, width=0.12, color="#1F3A5F"];',
        ]
        # The trap state is hidden unless asked for - or unless this run fell into it.
        trap_visible = show_trap or self.trap in visited
        for q in self.states:
            if q == self.trap and not trap_visible:
                continue
            shape = "doublecircle" if q in self.finals else "circle"
            fill = "#F4F7FB"
            if q == self.trap:
                fill = "#FBE9E7"
            if q in visited:
                fill = "#FFE9A8"
            if q == current:
                fill = "#B7E4C7" if q in self.finals else "#F5B7B1"
            lines.append(f'  "{q}" [shape={shape}, fillcolor="{fill}"];')
        lines.append(f'  __start -> "{self.start}";')

        # Merge parallel arrows (same source and target) into one labelled arrow.
        merged = {}
        for (q, a), target in self.delta.items():
            merged.setdefault((q, target), []).append(a)
        for (q, target), labels in merged.items():
            used = (q, target) in used_edges
            if self.trap in (q, target) and not show_trap:
                if not used:
                    continue                 # hide unused arrows into the trap state
                labels = ["any"] if q == self.trap else ["illegal symbol"]
            style = ' color="#D4860B", penwidth=2.2, fontcolor="#8A5300"' if used else ""
            lines.append(f'  "{q}" -> "{target}" [label="{", ".join(labels)}"{style}];')
        lines.append("}")
        return "\n".join(lines)

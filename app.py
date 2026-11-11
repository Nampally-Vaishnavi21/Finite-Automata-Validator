"""Finite Automata for Real-Time Validation - Streamlit interface.

Run with:   streamlit run app.py

All automata logic lives in the `automata` package; this file only draws the UI.
"""
import html

import pandas as pd
import streamlit as st

from automata import build_email_dfa, build_password_dfa, build_pin_dfa
from automata import email_dfa, password_dfa, pin_dfa
from automata.test_cases import EMAIL_CASES, PASSWORD_CASES, PIN_CASES

st.set_page_config(page_title="Finite Automata Validators", page_icon="🔁", layout="wide")

# ------------------------------------------------------------------ styling
st.markdown("""
<style>
.block-container {padding-top: 2.2rem; max-width: 1200px;}
h1, h2, h3 {color: #1F3A5F; letter-spacing: -0.01em;}
.banner {padding: 14px 18px; border-radius: 10px; font-weight: 700; font-size: 1.15rem;
         margin: 6px 0 14px 0; border-left: 8px solid;}
.banner small {display: block; font-weight: 400; font-size: 0.9rem; margin-top: 2px;}
.accept {background: #E8F6EE; color: #14532D; border-color: #2E9E5B;}
.reject {background: #FDECEA; color: #7F1D1D; border-color: #D64545;}
.idle   {background: #F4F7FB; color: #40516A; border-color: #9FB0C6;}
.card {background: #F4F7FB; border: 1px solid #DCE4EE; border-radius: 10px; padding: 16px 18px; height: 100%;}
.card h4 {margin: 0 0 6px 0; color: #1F3A5F;}
.chips {line-height: 2.3; overflow-wrap: anywhere;}
.chip {display: inline-block; padding: 2px 10px; border-radius: 14px; background: #FFE9A8;
       border: 1px solid #D4B24C; font-family: monospace; font-size: 0.9rem;}
.chip.ok {background: #B7E4C7; border-color: #2E9E5B;}
.chip.bad {background: #F5B7B1; border-color: #D64545;}
.arrow {color: #5B6B7F; font-family: monospace; font-size: 0.85rem; padding: 0 4px;}
.cond {padding: 6px 12px; border-radius: 8px; margin-bottom: 6px; font-size: 0.95rem;}
.cond.ok {background: #E8F6EE; color: #14532D;}
.cond.no {background: #FDECEA; color: #7F1D1D;}
.formal {background: #F4F7FB; border-left: 4px solid #1F3A5F; padding: 10px 14px;
         border-radius: 6px; font-family: "Cambria Math", Georgia, serif; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)


# Building the DFAs once and caching them keeps the app fast.
@st.cache_resource
def load_automata():
    return build_password_dfa(), build_email_dfa(), build_pin_dfa()


PWD, EMAIL, PIN = load_automata()


# ------------------------------------------------------------------ helpers
def _stretch(widget, *args, **kwargs):
    """Draw a widget at full width on both new and old Streamlit versions."""
    try:
        return widget(*args, width="stretch", **kwargs)
    except TypeError:                       # older Streamlit: no `width` argument
        return widget(*args, use_container_width=True, **kwargs)


def table(data, **kwargs):
    return _stretch(st.dataframe, data, **kwargs)


def graph(dot):
    return _stretch(st.graphviz_chart, dot)


def banner(result, text):
    """Big ACCEPTED / REJECTED box."""
    if text == "":
        st.markdown('<div class="banner idle">Waiting for input<small>Type a string above. '
                    'The empty string ε is rejected by this automaton.</small></div>',
                    unsafe_allow_html=True)
    elif result.accepted:
        st.markdown(f'<div class="banner accept">ACCEPTED<small>The automaton stopped in final '
                    f'state <b>{result.final_state}</b>.</small></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="banner reject">REJECTED<small>The automaton stopped in '
                    f'non-final state <b>{result.final_state}</b>.</small></div>',
                    unsafe_allow_html=True)


def path_chips(result):
    """The run as a row of state 'chips':  q0 —a→ q1 —b→ q2 …"""
    parts = [f'<span class="chip">{html.escape(result.path[0])}</span>']
    for i, step in enumerate(result.steps):
        last = i == len(result.steps) - 1
        cls = "chip " + (("ok" if result.accepted else "bad") if last else "")
        shown = "␣" if step.char == " " else step.char
        parts.append(f'<span class="arrow">—{html.escape(shown)}→</span>'
                     f'<span class="{cls}">{html.escape(step.target)}</span>')
    st.markdown('<div class="chips">' + "".join(parts) + "</div>", unsafe_allow_html=True)


def trace_table(result):
    rows = [{"Step": s.index, "Character": s.char, "Symbol class": s.symbol,
             "Current state": s.source, "Next state": s.target,
             "Move": f"δ({s.source}, {s.symbol}) = {s.target}"} for s in result.steps]
    table(pd.DataFrame(rows), hide_index=True)


def explain_rejection(dfa, result):
    """Plain-language reason, read from the trace."""
    for s in result.steps:
        if s.target == dfa.trap:
            shown = "space" if s.char == " " else f"'{s.char}'"
            return (f"Character {s.index} ({shown}, class `{s.symbol}`) has no legal move from "
                    f"state {s.source}, so the automaton entered the trap state.")
    return f"The input ended in {result.final_state}: {dfa.state_info[result.final_state]}"


def formal_model(info, dfa, extra=None):
    st.markdown("**Problem statement**")
    st.write(info["problem"])
    st.markdown("**Input alphabet**")
    st.markdown(f'<div class="formal">{html.escape(info["alphabet"])}</div>', unsafe_allow_html=True)
    st.markdown("**Language**")
    st.markdown(f'<div class="formal">{html.escape(info["language"])}<br>'
                f'<i>Regular expression:</i> {html.escape(info["regex"])}</div>',
                unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown("**Validation rules**")
        for rule in info["rules"]:
            st.markdown(f"- {rule}")
    with right:
        st.markdown("**Assumptions**")
        for item in info["assumptions"]:
            st.markdown(f"- {item}")
    if extra:
        extra()
    st.markdown("**DFA as a 5-tuple**")
    st.markdown(f'<div class="formal">M = (Q, Σ, δ, q0, F)<br>|Q| = {len(dfa.states)} states, '
                f'Σ = {{{", ".join(dfa.symbols)}}}, q0 = {dfa.start}, '
                f'F = {{{", ".join(sorted(dfa.finals))}}}, δ = the transition table.</div>',
                unsafe_allow_html=True)
    st.markdown("**Initial and final states**")
    st.write(info["start_final"])
    st.markdown("**Syntax vs. business rules**")
    st.info(info["semantic"])


def symbol_legend(dfa):
    table(pd.DataFrame([{"Symbol class": k, "Characters": v}
                               for k, v in dfa.symbol_info.items()]),
                 hide_index=True)


def state_meanings(dfa):
    table(pd.DataFrame([{"State": q, "Meaning": dfa.state_info.get(q, "")}
                               for q in dfa.states]),
                 hide_index=True)


def test_case_tab(dfa, cases):
    rows = []
    for text, expected, reason in cases:
        actual = dfa.accepts(text)          # run the real automaton, live
        rows.append({"Input": text if text else "ε (empty)",
                     "Expected": "ACCEPT" if expected else "REJECT",
                     "Automaton result": "ACCEPT" if actual else "REJECT",
                     "Final state": dfa.run(text).final_state,
                     "Match": "✔" if actual == expected else "✘",
                     "Why": reason})
    passed = sum(r["Match"] == "✔" for r in rows)
    accepted = sum(c[1] for c in cases)
    a, b, c = st.columns(3)
    a.metric("Accepted strings", accepted)
    b.metric("Rejected strings", len(cases) - accepted)
    c.metric("Automaton agrees with expected", f"{passed} / {len(rows)}")
    table(pd.DataFrame(rows), hide_index=True)
    st.caption("These results are computed by the DFA each time the page loads; they are not stored text.")


def sample_picker(cases, key):
    """Dropdown that copies a prepared test string into the input box."""
    options = ["— type your own —"] + [f"{t or 'ε (empty)'}   [{'accept' if e else 'reject'}]" for t, e, _ in cases]
    choice = st.selectbox("Load a sample string", options, key=key + "_sample")
    if choice == options[0]:
        return None
    return cases[options.index(choice) - 1][0]


# ------------------------------------------------------------------ pages
def page_overview():
    st.title("Finite Automata for Real-Time Validation")
    st.caption("21CSC301T Formal Language and Automata · Assignment 2 · Designing Automata for Real-Time Applications")
    st.write("Three everyday input checks, each modelled as a deterministic finite automaton "
             "and executed character by character. Choose a validator from the sidebar.")
    cols = st.columns(3)
    cards = [
        ("Password Verification", "Length ≥ 8 with uppercase, lowercase, digit and special character.",
         f"{len(PWD.states)} states (product of five small DFAs)"),
        ("Email Format Validator", "Simplified local@domain.extension syntax.",
         f"{len(EMAIL.states)} states"),
        ("ATM PIN Verification", "Exactly 4 or exactly 6 digits.", f"{len(PIN.states)} states"),
    ]
    for col, (title, text, size) in zip(cols, cards):
        col.markdown(f'<div class="card"><h4>{title}</h4>{text}<br><br><b>{size}</b></div>',
                     unsafe_allow_html=True)
    st.subheader("How every validator works")
    st.markdown('<div class="formal">A DFA is M = (Q, Σ, δ, q0, F). Starting in q0, it reads one '
                'input symbol at a time and moves to δ(state, symbol). The string is accepted '
                'if and only if the state reached after the last symbol belongs to F.</div>',
                unsafe_allow_html=True)
    st.markdown("Each validator page has five tabs: **Validator** (try a string and watch the run), "
                "**Formal model**, **State diagram**, **Transition table** and **Test cases**.")


def page_password():
    st.title("Password Verification")
    tabs = st.tabs(["Validator", "Formal model", "State diagram", "Transition table", "Test cases"])
    with tabs[0]:
        sample = sample_picker(PASSWORD_CASES, "pwd")
        text = st.text_input("Password to check", value=sample if sample is not None else "",
                             help="Shown in plain text because this is a demonstration, not a login form.")
        result, report, illegal = password_dfa.conditions(text)
        left, right = st.columns([3, 2])
        with left:
            banner(result, text)
            if text and not result.accepted:
                st.write(explain_rejection(PWD, result))
            if text:
                st.markdown("**Run through the product DFA**")
                st.caption("State name = flags seen (U, L, D, S) | characters counted. "
                           "Example: `UL--|5` means uppercase and lowercase seen, 5 characters read.")
                path_chips(result)
        with right:
            st.markdown("**Conditions**")
            if illegal:
                st.markdown('<div class="cond no">✘ Contains a character outside the alphabet '
                            '(space or non-ASCII)</div>', unsafe_allow_html=True)
            for label, ok in report:
                st.markdown(f'<div class="cond {"ok" if ok else "no"}">{"✔" if ok else "✘"} '
                            f'{label}{"" if ok else " — missing"}</div>', unsafe_allow_html=True)
            st.caption("The ticks are read from the DFA state reached, not computed separately.")
        if text:
            with st.expander("Step-by-step transitions"):
                trace_table(result)
    with tabs[1]:
        formal_model(password_dfa.INFO, PWD)
    with tabs[2]:
        st.markdown("**Five component DFAs** - one per rule")
        cols = st.columns(4)
        for col, kind in zip(cols, password_dfa.FLAG_ORDER):
            with col:
                graph(password_dfa.contains_dot(kind))
        graph(password_dfa.length_dot())
        st.markdown(
            "**Product construction.** The password DFA runs all five machines together. "
            "Its state is the tuple of the five component states, written `ULDS|k`. A move "
            "updates every component at once, and the only final state is `ULDS|8+`, where "
            "all five components accept. Of the 2×2×2×2×9 = 144 possible tuples, "
            f"{len(PWD.states) - 1} are reachable; with the trap state the DFA has "
            f"{len(PWD.states)} states.")
        with st.expander(f"Show the complete product DFA ({len(PWD.states)} states)"):
            graph(PWD.to_dot(rankdir="TB"))
        st.markdown("**Symbol classes**")
        symbol_legend(PWD)
    with tabs[3]:
        st.caption("→ marks the start state, * marks the final state. Every `other` symbol leads to the trap state qd.")
        table(pd.DataFrame(PWD.transition_table()), hide_index=True, height=420)
        with st.expander("Meaning of every state"):
            state_meanings(PWD)
    with tabs[4]:
        test_case_tab(PWD, PASSWORD_CASES)


def simple_page(title, dfa, info, cases, key, label, extra=None):
    """Shared layout for the Email and PIN validators (their DFAs are small enough to draw fully)."""
    st.title(title)
    tabs = st.tabs(["Validator", "Formal model", "State diagram", "Transition table", "Test cases"])
    with tabs[0]:
        sample = sample_picker(cases, key)
        text = st.text_input(label, value=sample if sample is not None else "")
        result = dfa.run(text)
        banner(result, text)
        if text:
            if not result.accepted:
                st.write(explain_rejection(dfa, result))
            st.markdown("**States visited**")
            path_chips(result)
            st.markdown("**Path on the state diagram**")
            graph(dfa.to_dot(path=result.path))
            st.caption("Yellow = visited, green = stopped in a final state, red = stopped in a non-final state.")
            with st.expander("Step-by-step transitions", expanded=True):
                trace_table(result)
    with tabs[1]:
        formal_model(info, dfa, extra)
    with tabs[2]:
        show = st.toggle("Show the trap state and all arrows into it", key=key + "_trap")
        graph(dfa.to_dot(show_trap=show))
        if not show:
            st.caption("Convention: every transition that is not drawn goes to the trap state qd.")
        st.markdown("**Meaning of every state**")
        state_meanings(dfa)
        st.markdown("**Symbol classes**")
        symbol_legend(dfa)
    with tabs[3]:
        st.caption("→ marks the start state, * marks final states.")
        table(pd.DataFrame(dfa.transition_table()), hide_index=True)
    with tabs[4]:
        test_case_tab(dfa, cases)


def email_grammar():
    st.markdown("**Simplified grammar**")
    st.code("\n".join(email_dfa.INFO["grammar"]), language=None)
    st.caption("This grammar is right-linear in effect (it describes a regular language), "
               "which is why a DFA can recognise it.")


def page_limits():
    st.title("Limitations of Finite Automata")
    st.write("A finite automaton has a fixed number of states and no other memory. "
             "That is enough for format checks, and not enough for the following.")
    table(pd.DataFrame([
        {"Limitation": "No unbounded counting",
         "Example": "{ aⁿbⁿ : n ≥ 0 }, balanced brackets",
         "What is needed": "A stack (pushdown automaton)"},
        {"Limitation": "No comparison of distant parts of the input",
         "Example": "\"Confirm password\" must equal \"password\"; { ww }",
         "What is needed": "Memory of the earlier text (Turing machine / program)"},
        {"Limitation": "No knowledge outside the input string",
         "Example": "Is this the correct PIN for this card? Does this mailbox exist?",
         "What is needed": "Database or network lookup"},
        {"Limitation": "No memory between runs",
         "Example": "Block the card after 3 wrong PIN attempts",
         "What is needed": "A stored counter in the application"},
        {"Limitation": "State explosion",
         "Example": "Password DFA: 5 simple rules already need 105 states",
         "What is needed": "Keep the component DFAs separate, or use an NFA / regular expression"},
    ]), hide_index=True)

    st.subheader("Syntax validation versus business rules")
    table(pd.DataFrame([
        {"Application": "Password", "Checked by the automaton (syntax)": "Length and character classes",
         "Needs additional processing (semantics)": "Matching the stored hash, breached-password lists, password history"},
        {"Application": "Email", "Checked by the automaton (syntax)": "Shape local@domain.extension",
         "Needs additional processing (semantics)": "Domain exists (DNS), mailbox exists, user owns it (confirmation mail)"},
        {"Application": "ATM PIN", "Checked by the automaton (syntax)": "4 or 6 digits only",
         "Needs additional processing (semantics)": "Correct PIN for the card, attempt limit, account status"},
    ]), hide_index=True)

    st.subheader("When is a finite automaton sufficient?")
    left, right = st.columns(2)
    left.success("**Sufficient** when the decision depends only on a bounded amount of information "
                 "about the characters read so far: which character classes appeared, a count up "
                 "to a fixed limit, or which part of a fixed pattern we are in.")
    right.warning("**Not sufficient** when the decision needs unbounded counting, nesting, "
                  "comparison with earlier input, or any data that is not in the string itself.")

    st.subheader("Design comparison")
    table(pd.DataFrame([
        {"Design": "One product DFA", "States for the password rule": "105",
         "Advantage": "Single deterministic pass, one final state",
         "Drawback": "Too large to draw; grows as rules are added"},
        {"Design": "Five separate DFAs (run in parallel)", "States for the password rule": "2+2+2+2+9 = 17",
         "Advantage": "Each one is easy to draw and explain",
         "Drawback": "Needs the 'all must accept' step outside the automata"},
        {"Design": "NFA", "States for the password rule": "Often fewer than the DFA",
         "Advantage": "Compact for 'contains' patterns such as Σ*UΣ*",
         "Drawback": "Intersection is still required; simulation tracks a set of states"},
    ]), hide_index=True)
    st.caption("DFAs and NFAs recognise exactly the same class of languages (the regular languages); "
               "the choice affects size and convenience, not power.")


# ------------------------------------------------------------------ navigation
PAGES = {
    "Overview": page_overview,
    "Password Verification": page_password,
    "Email Format Validator": lambda: simple_page(
        "Email Format Validator", EMAIL, email_dfa.INFO, EMAIL_CASES, "email",
        "Email address to check", email_grammar),
    "ATM PIN Verification": lambda: simple_page(
        "ATM PIN Verification", PIN, pin_dfa.INFO, PIN_CASES, "pin", "PIN to check"),
    "Limitations": page_limits,
}

with st.sidebar:
    st.markdown("### Finite Automata\nAssignment 2")
    page = st.radio("Section", list(PAGES), label_visibility="collapsed")
    st.divider()
    st.caption("This tool validates input FORMAT only. It never stores what you type and does "
               "not authenticate anyone.")

PAGES[page]()

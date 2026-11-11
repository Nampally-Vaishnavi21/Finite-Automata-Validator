"""Unit tests.  Run with:  pytest -v"""
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from automata import build_email_dfa, build_password_dfa, build_pin_dfa
from automata.email_dfa import EQUIVALENT_REGEX
from automata.password_dfa import SPECIALS, conditions
from automata.test_cases import EMAIL_CASES, PASSWORD_CASES, PIN_CASES

PWD, EMAIL, PIN = build_password_dfa(), build_email_dfa(), build_pin_dfa()


@pytest.mark.parametrize("text,expected,reason", PASSWORD_CASES)
def test_password_cases(text, expected, reason):
    assert PWD.accepts(text) == expected, reason


@pytest.mark.parametrize("text,expected,reason", EMAIL_CASES)
def test_email_cases(text, expected, reason):
    assert EMAIL.accepts(text) == expected, reason


@pytest.mark.parametrize("text,expected,reason", PIN_CASES)
def test_pin_cases(text, expected, reason):
    assert PIN.accepts(text) == expected, reason


@pytest.mark.parametrize("cases", [PASSWORD_CASES, EMAIL_CASES, PIN_CASES])
def test_at_least_five_accepted_and_five_rejected(cases):
    assert sum(1 for c in cases if c[1]) >= 5
    assert sum(1 for c in cases if not c[1]) >= 5


@pytest.mark.parametrize("dfa", [PWD, EMAIL, PIN])
def test_delta_is_total_and_trap_is_absorbing(dfa):
    for q in dfa.states:
        for a in dfa.symbols:
            assert dfa.delta[(q, a)] in dfa.states
    for a in dfa.symbols:
        assert dfa.delta[(dfa.trap, a)] == dfa.trap
    assert dfa.trap not in dfa.finals


def test_password_product_has_105_states():
    # Reachable product states: 1 (start) + 4·8 + 6·7 + 4·6 + 1·5 = 104, plus the trap state.
    # (A state with k flags on needs at least k characters, and any character turns a flag on.)
    assert len(PWD.states) == 105
    assert len(PWD.finals) == 1


def test_password_dfa_matches_direct_definition():
    """Fuzz test: the DFA must agree with the plain-English definition of L_pwd."""
    rng = random.Random(1)
    pool = "ABCxyz019!@#_ " + "é"
    for _ in range(5000):
        w = "".join(rng.choice(pool) for _ in range(rng.randint(0, 12)))
        legal = all(c.isascii() and (c.isalnum() or c in SPECIALS) for c in w)
        expected = (legal and len(w) >= 8 and any(c.isupper() for c in w)
                    and any(c.islower() for c in w) and any(c.isdigit() for c in w)
                    and any(c in SPECIALS for c in w))
        assert PWD.accepts(w) == expected, w


def test_password_condition_report():
    _, report, illegal = conditions("password123!")
    assert not illegal
    assert [ok for _, ok in report] == [True, False, True, True, True]


def test_email_dfa_matches_regular_expression():
    """Fuzz test: DFA and the equivalent regular expression define the same language."""
    rng = random.Random(2)
    pattern = re.compile(EQUIVALENT_REGEX)
    pool = "ab1.-_@c9 #"
    agree_accept = 0
    for _ in range(100000):
        w = "".join(rng.choice(pool) for _ in range(rng.randint(0, 11)))
        expected = pattern.fullmatch(w) is not None
        assert EMAIL.accepts(w) == expected, w
        agree_accept += expected
    assert agree_accept > 0      # the fuzz set really contains accepted strings


def test_pin_dfa_matches_direct_definition():
    rng = random.Random(3)
    for _ in range(5000):
        w = "".join(rng.choice("0123456789a #") for _ in range(rng.randint(0, 8)))
        assert PIN.accepts(w) == (w.isascii() and w.isdigit() and len(w) in (4, 6)), w


def test_trace_is_consistent():
    result = EMAIL.run("a@b.co")
    assert result.path == ["q0", "q1", "q3", "q4", "q6", "q7", "q8"]
    assert result.accepted

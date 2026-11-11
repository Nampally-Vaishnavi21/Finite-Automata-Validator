# FLA Assignment 2 – Finite Automata for Real-Time Validation

**Course:** 21CSC301T – Formal Language and Automata (AY 2026–2027, Semester V)
**Programme:** B.Tech. CSE (Artificial Intelligence and Machine Learning), SRM IST Tiruchirappalli
**Student:** `<Name>` · `<Register Number>`
**Repository:** `<paste GitHub URL after creating the repository>`

An interactive application that models three everyday input checks as deterministic
finite automata and runs them character by character.

| Validator | Language | DFA size |
|---|---|---|
| Password | length ≥ 8 with uppercase, lowercase, digit, special character | 105 states (product of 5 small DFAs) |
| Email | simplified `local@domain.extension` syntax (not full RFC 5322) | 12 states |
| ATM PIN | exactly 4 or exactly 6 digits | 8 states |

## Features

- ACCEPTED / REJECTED result with the reason read from the automaton's run
- Step-by-step transition trace `δ(q, a) = q'` and highlighted path on the state diagram
- Password checklist showing which conditions are satisfied or missing
- Formal model for each validator: Σ, L, rules, assumptions, 5-tuple, start/final states
- Transition tables generated from the same DFA objects that execute
- 13–16 test strings per validator (≥ 5 accepted, ≥ 5 rejected), executed live
- Limitations page: syntax vs business rules, when an FA is sufficient, design comparison

## Project structure

```
app.py                     Streamlit interface
cli.py                     Terminal / Colab demo
automata/
  dfa.py                   Generic DFA class (run, trace, table, diagram)
  password_dfa.py          Product-construction password DFA
  email_dfa.py             Email DFA + equivalent regular expression
  pin_dfa.py               PIN DFA
  test_cases.py            Accepted / rejected strings
tests/test_automata.py     54 unit tests (incl. fuzz tests against independent definitions)
scripts/build_assets.py    Regenerates diagrams/ and docs/transition_tables.md
docs/DESIGN_NOTE.md        Design note (main written submission)
docs/transition_tables.md  All transition tables
docs/test_results.txt      pytest output
diagrams/                  State diagrams (.dot and .png)
screenshots/               Demonstration screenshots
```

## Installation and execution

Requires Python 3.11 or newer.

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

The app opens at http://localhost:8501.

**Without Streamlit / in Google Colab**

```bash
python cli.py pin 1234
python cli.py email student@srmist.edu.in
python cli.py password Secure@123
```

**Run the tests**

```bash
pytest -v
```

**Regenerate diagrams and tables** (PNG output needs Graphviz installed; optional)

```bash
python scripts/build_assets.py
```

## 5-minute demonstration plan

1. **Overview** – state the DFA definition (30 s).
2. **ATM PIN** – enter `1234`, `12345`, `12a4`; show the counting chain and why q5 is not final (1 min).
3. **Email** – enter `student@srmist.edu.in` then `user..name@gmail.com`; show the highlighted path, the grammar and the "not RFC" assumption (1.5 min).
4. **Password** – enter `password123` then `Secure@123`; show the checklist and explain the product construction on the State diagram tab (1.5 min).
5. **Limitations** – syntax vs business rules table (30 s).

## Limitations

Finite automata validate format only. They cannot count without bound, compare two
parts of the input, or consult a database, so real authentication (password matching,
email ownership, PIN verification against a bank account) needs additional processing.
See `docs/DESIGN_NOTE.md` §6–7.

## Publishing to GitHub

Create an empty repository named `FLA-Assignment-2-Finite-Automata` on github.com
(no README, no .gitignore), then:

```bash
git init
git add .
git commit -m "FLA Assignment 2: finite automata validators"
git branch -M main
git remote add origin https://github.com/<your-username>/FLA-Assignment-2-Finite-Automata.git
git push -u origin main
```

## References

Hopcroft, Motwani and Ullman, *Introduction to Automata Theory, Languages, and Computation*, 3rd ed.;
Sipser, *Introduction to the Theory of Computation*, 3rd ed.; RFC 5322. Full list in the design note.

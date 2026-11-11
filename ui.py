"""Look-and-feel helpers for the Streamlit interface (styling only, no logic)."""
import html

import streamlit as st

CSS = """
<style>
.block-container {padding-top: 2.4rem; padding-bottom: 3rem; max-width: 1180px;}
section[data-testid="stSidebar"] {border-right: 1px solid #DCE3EA;}
.app-header {border-left: 5px solid #0F766E; padding: .15rem 0 .15rem 1rem; margin-bottom: 1.3rem;}
.app-header .kicker {font-size: .74rem; letter-spacing: .14em; text-transform: uppercase;
  color: #5B6B7C; font-weight: 700;}
.app-header .title {font-size: 1.85rem; font-weight: 700; color: #12263A; line-height: 1.2;
  margin: .15rem 0;}
.app-header .sub {color: #4A5A6A; font-size: .98rem;}
.verdict {border-radius: 10px; padding: .85rem 1.1rem; margin: .5rem 0 1rem; border: 1px solid;
  display: flex; gap: .9rem; align-items: baseline; flex-wrap: wrap;}
.verdict .tag {font-weight: 800; letter-spacing: .1em; font-size: 1.02rem; white-space: nowrap;}
.verdict .msg {font-size: .93rem;}
.verdict.ok {background: #ECFDF5; border-color: #6EE7B7; color: #065F46;}
.verdict.bad {background: #FEF2F2; border-color: #FCA5A5; color: #991B1B;}
.verdict.unk {background: #FFFBEB; border-color: #FCD34D; color: #92400E;}
.chips {display: flex; flex-wrap: wrap; gap: .45rem; margin: .2rem 0 1rem;}
.chip {border-radius: 999px; padding: .22rem .75rem; font-size: .84rem; border: 1px solid;
  font-weight: 600;}
.chip.ok {background: #ECFDF5; border-color: #6EE7B7; color: #065F46;}
.chip.bad {background: #FEF2F2; border-color: #FCA5A5; color: #991B1B;}
.tape {display: flex; flex-wrap: wrap; gap: 4px; margin: .3rem 0 1rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;}
.tape .cell {min-width: 2.3rem; text-align: center; padding: .28rem .4rem; background: #FFFFFF;
  border: 1px solid #CBD5E1; border-radius: 6px; font-size: .98rem; color: #12263A;}
.tape .cell small {display: block; font-size: .64rem; color: #64748B; margin-top: 1px;}
.tape .cell.bad {border-color: #FCA5A5; background: #FEF2F2;}
.tape .cell.good {border-color: #6EE7B7; background: #ECFDF5;}
.tape .cell.now {border-color: #0F766E; box-shadow: 0 0 0 2px #99F6E4;}
.stack {display: inline-flex; flex-direction: column; gap: 3px; min-width: 5.5rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;}
.stack .item {text-align: center; padding: .3rem .6rem; border: 1px solid #94A3B8;
  border-radius: 6px; background: #FFFFFF; color: #12263A;}
.stack .item.top {border-color: #0F766E; background: #F0FDFA; font-weight: 700;}
.stack .cap {font-size: .7rem; color: #64748B; text-align: center;}
.note {color: #5B6B7C; font-size: .86rem;}
</style>
"""


def setup(page_title: str) -> None:
    st.set_page_config(page_title=page_title, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)


def header(kicker: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="app-header"><div class="kicker">{html.escape(kicker)}</div>'
        f'<div class="title">{html.escape(title)}</div>'
        f'<div class="sub">{html.escape(subtitle)}</div></div>',
        unsafe_allow_html=True,
    )


def verdict(kind: str, tag: str, message: str) -> None:
    """kind is 'ok' (green), 'bad' (red) or 'unk' (amber)."""
    st.markdown(
        f'<div class="verdict {kind}"><span class="tag">{html.escape(tag)}</span>'
        f'<span class="msg">{html.escape(message)}</span></div>',
        unsafe_allow_html=True,
    )


def chips(items) -> None:
    """items: iterable of (label, satisfied)."""
    parts = [
        f'<span class="chip {"ok" if ok else "bad"}">{"✓" if ok else "✗"} {html.escape(label)}</span>'
        for label, ok in items
    ]
    st.markdown(f'<div class="chips">{"".join(parts)}</div>', unsafe_allow_html=True)


def tape(cells) -> None:
    """cells: iterable of (symbol, caption, css_class)."""
    parts = []
    for symbol, caption, css in cells:
        shown = "␣" if symbol == " " else symbol
        parts.append(f'<div class="cell {css}">{html.escape(shown)}'
                     f'<small>{html.escape(caption)}</small></div>')
    st.markdown(f'<div class="tape">{"".join(parts)}</div>', unsafe_allow_html=True)


def stack(symbols, caption: str = "") -> None:
    """Draw a stack; symbols[0] is the top."""
    parts = ['<div class="cap">top</div>']
    for i, sym in enumerate(symbols):
        parts.append(f'<div class="item {"top" if i == 0 else ""}">{html.escape(sym)}</div>')
    if caption:
        parts.append(f'<div class="cap">{html.escape(caption)}</div>')
    st.markdown(f'<div class="stack">{"".join(parts)}</div>', unsafe_allow_html=True)


def note(text: str) -> None:
    st.markdown(f'<div class="note">{html.escape(text)}</div>', unsafe_allow_html=True)

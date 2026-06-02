import streamlit as st
from database import init_db, get_summary, get_events, get_trades

init_db()

st.set_page_config(page_title="Trading Journal", layout="wide")
st.title("Trading Journal")
st.caption("A local journal for connecting market events to trade ideas.")

summary = get_summary()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Market Events", summary["total_events"])
col2.metric("Total Trades", summary["total_trades"])
col3.metric("Open Trades", summary["open_trades"])
col4.metric("Closed P&L", f"{summary['closed_pnl']:+.2f}")

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Recent Market Events")
    events = get_events()[:5]
    if events:
        for e in events:
            st.markdown(f"**{e['date']}** — {e['event_title']}  \n"
                        f"`{e['category']}` · {e['asset_class']} · Importance: {e['importance']}/5")
            st.caption(e["my_interpretation"] or "")
            st.divider()
    else:
        st.info("No events logged yet. Go to the News page to add one.")

with col_right:
    st.subheader("Recent Trades")
    trades = get_trades()[:5]
    if trades:
        for t in trades:
            pnl_str = f"P&L: {t['pnl']:+.2f}" if t["pnl"] is not None else ""
            st.markdown(f"**{t['date']}** — {t['asset']} {t['direction']}  \n"
                        f"`{t['status']}` · {t['asset_class']} · Confidence: {t['confidence']}/5  \n"
                        + (f"_{pnl_str}_" if pnl_str else ""))
            st.caption(t["thesis"] or "")
            st.divider()
    else:
        st.info("No trades logged yet. Go to the Trades page to add one.")

st.sidebar.page_link("app.py", label="Dashboard")
st.sidebar.page_link("pages/news.py", label="News & Market Events")
st.sidebar.page_link("pages/trades.py", label="Trades & Trade Ideas")
st.sidebar.page_link("pages/learning.py", label="Learning Notes")

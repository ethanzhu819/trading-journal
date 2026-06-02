import streamlit as st
from database import add_trade, get_trades, update_trade, delete_trade, get_events

st.set_page_config(page_title="Trades & Trade Ideas", layout="wide")
st.title("Trades & Trade Ideas")

ASSET_CLASSES = ["Equities", "Crypto", "FX", "Fixed Income", "Commodities", "Other"]
DIRECTIONS = ["Long", "Short"]
HORIZONS = ["Intraday", "Swing", "Position", "Long-term"]
STATUSES = ["Open", "Closed", "Paper"]


def event_options():
    events = get_events()
    options = {0: "None"}
    options.update({e["id"]: f"{e['date']} — {e['event_title']}" for e in events})
    return options


# ── Add Trade ─────────────────────────────────────────────────────────────────

with st.expander("Add New Trade / Trade Idea", expanded=False):
    with st.form("add_trade_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        date = col1.date_input("Date")
        asset = col2.text_input("Asset *")
        asset_class = col3.selectbox("Asset Class", ASSET_CLASSES)

        col4, col5, col6 = st.columns(3)
        direction = col4.selectbox("Direction", DIRECTIONS)
        time_horizon = col5.selectbox("Time Horizon", HORIZONS)
        status = col6.selectbox("Status", STATUSES)

        ev_opts = event_options()
        related_event_id = st.selectbox(
            "Related News Event",
            options=list(ev_opts.keys()),
            format_func=lambda x: ev_opts[x],
        )

        thesis = st.text_area("Thesis", height=80)
        catalyst = st.text_input("Catalyst")
        risk_factors = st.text_area("Risk Factors", height=60)

        col7, col8, col9, col10 = st.columns(4)
        entry = col7.number_input("Entry", value=0.0, format="%.4f")
        target = col8.number_input("Target", value=0.0, format="%.4f")
        stop = col9.number_input("Stop", value=0.0, format="%.4f")
        confidence = col10.slider("Confidence", 1, 5, 3)

        st.markdown("**Post-trade fields (fill after close)**")
        col11, col12 = st.columns(2)
        actual_exit = col11.number_input("Actual Exit", value=0.0, format="%.4f")
        pnl = col12.number_input("P&L", value=0.0, format="%.2f")
        post_trade_review = st.text_area("Post-trade Review", height=60)

        submitted = st.form_submit_button("Add Trade")
        if submitted:
            if not asset:
                st.error("Asset is required.")
            else:
                add_trade({
                    "date": str(date),
                    "related_event_id": related_event_id if related_event_id != 0 else None,
                    "asset": asset,
                    "asset_class": asset_class,
                    "direction": direction,
                    "time_horizon": time_horizon,
                    "thesis": thesis,
                    "catalyst": catalyst,
                    "entry": entry or None,
                    "target": target or None,
                    "stop": stop or None,
                    "confidence": confidence,
                    "risk_factors": risk_factors,
                    "status": status,
                    "actual_exit": actual_exit or None,
                    "pnl": pnl or None,
                    "post_trade_review": post_trade_review,
                })
                st.success("Trade added.")
                st.rerun()

# ── Filters ───────────────────────────────────────────────────────────────────

st.subheader("Trades Log")
with st.expander("Filters", expanded=False):
    fc1, fc2, fc3 = st.columns(3)
    f_status = fc1.selectbox("Status", ["All"] + STATUSES, key="f_status")
    f_asset_class = fc2.selectbox("Asset Class", ["All"] + ASSET_CLASSES, key="f_ac")
    f_direction = fc3.selectbox("Direction", ["All"] + DIRECTIONS, key="f_dir")

filters = {
    "status": f_status if f_status != "All" else None,
    "asset_class": f_asset_class if f_asset_class != "All" else None,
    "direction": f_direction if f_direction != "All" else None,
}

trades = get_trades(filters)

if not trades:
    st.info("No trades found.")
else:
    for t in trades:
        pnl_str = f"  |  P&L: {t['pnl']:+.2f}" if t["pnl"] is not None else ""
        label = f"{t['date']} | {t['asset']} {t['direction']} [{t['status']}]{pnl_str}"
        with st.expander(label):
            col_a, col_b, col_c = st.columns(3)
            col_a.markdown(f"**Asset Class:** {t['asset_class']}")
            col_b.markdown(f"**Time Horizon:** {t['time_horizon']}")
            col_c.markdown(f"**Confidence:** {t['confidence']}/5")

            if t["related_event_title"]:
                st.markdown(f"**Related Event:** {t['related_event_title']}")

            st.markdown(f"**Thesis:** {t['thesis'] or '—'}")
            st.markdown(f"**Catalyst:** {t['catalyst'] or '—'}")
            st.markdown(f"**Risk Factors:** {t['risk_factors'] or '—'}")

            col_e, col_f, col_g = st.columns(3)
            col_e.markdown(f"**Entry:** {t['entry']}")
            col_f.markdown(f"**Target:** {t['target']}")
            col_g.markdown(f"**Stop:** {t['stop']}")

            if t["status"] == "Closed":
                col_h, col_i = st.columns(2)
                col_h.markdown(f"**Actual Exit:** {t['actual_exit']}")
                col_i.markdown(f"**P&L:** {t['pnl']:+.2f}" if t["pnl"] is not None else "")
                st.markdown(f"**Post-trade Review:** {t['post_trade_review'] or '—'}")

            edit_key = f"edit_trade_{t['id']}"
            if st.button("Edit", key=f"btn_edit_t_{t['id']}"):
                st.session_state[edit_key] = True

            if st.session_state.get(edit_key):
                ev_opts = event_options()
                with st.form(f"edit_trade_form_{t['id']}"):
                    tc1, tc2, tc3 = st.columns(3)
                    new_date = tc1.date_input("Date", value=t["date"], key=f"td_{t['id']}")
                    new_asset = tc2.text_input("Asset", value=t["asset"], key=f"ta_{t['id']}")
                    new_ac = tc3.selectbox("Asset Class", ASSET_CLASSES,
                                           index=ASSET_CLASSES.index(t["asset_class"]) if t["asset_class"] in ASSET_CLASSES else 0,
                                           key=f"tac_{t['id']}")
                    tc4, tc5, tc6 = st.columns(3)
                    new_dir = tc4.selectbox("Direction", DIRECTIONS,
                                            index=DIRECTIONS.index(t["direction"]) if t["direction"] in DIRECTIONS else 0,
                                            key=f"tdir_{t['id']}")
                    new_hor = tc5.selectbox("Time Horizon", HORIZONS,
                                            index=HORIZONS.index(t["time_horizon"]) if t["time_horizon"] in HORIZONS else 0,
                                            key=f"thor_{t['id']}")
                    new_status = tc6.selectbox("Status", STATUSES,
                                               index=STATUSES.index(t["status"]) if t["status"] in STATUSES else 0,
                                               key=f"tst_{t['id']}")
                    cur_ev = t["related_event_id"] if t["related_event_id"] and t["related_event_id"] in ev_opts else 0
                    new_ev = st.selectbox("Related Event", list(ev_opts.keys()),
                                          index=list(ev_opts.keys()).index(cur_ev),
                                          format_func=lambda x: ev_opts[x],
                                          key=f"tev_{t['id']}")
                    new_thesis = st.text_area("Thesis", value=t["thesis"] or "", key=f"tth_{t['id']}")
                    new_cat = st.text_input("Catalyst", value=t["catalyst"] or "", key=f"tcat_{t['id']}")
                    new_rf = st.text_area("Risk Factors", value=t["risk_factors"] or "", key=f"trf_{t['id']}")
                    tc7, tc8, tc9, tc10 = st.columns(4)
                    new_entry = tc7.number_input("Entry", value=float(t["entry"] or 0), format="%.4f", key=f"ten_{t['id']}")
                    new_target = tc8.number_input("Target", value=float(t["target"] or 0), format="%.4f", key=f"ttg_{t['id']}")
                    new_stop = tc9.number_input("Stop", value=float(t["stop"] or 0), format="%.4f", key=f"tsp_{t['id']}")
                    new_conf = tc10.slider("Confidence", 1, 5, t["confidence"] or 3, key=f"tcf_{t['id']}")
                    tc11, tc12 = st.columns(2)
                    new_exit = tc11.number_input("Actual Exit", value=float(t["actual_exit"] or 0), format="%.4f", key=f"tex_{t['id']}")
                    new_pnl = tc12.number_input("P&L", value=float(t["pnl"] or 0), format="%.2f", key=f"tpnl_{t['id']}")
                    new_review = st.text_area("Post-trade Review", value=t["post_trade_review"] or "", key=f"trev_{t['id']}")

                    if st.form_submit_button("Save"):
                        update_trade(t["id"], {
                            "date": str(new_date), "asset": new_asset,
                            "asset_class": new_ac, "direction": new_dir,
                            "time_horizon": new_hor, "status": new_status,
                            "related_event_id": new_ev if new_ev != 0 else None,
                            "thesis": new_thesis, "catalyst": new_cat,
                            "risk_factors": new_rf,
                            "entry": new_entry or None, "target": new_target or None,
                            "stop": new_stop or None, "confidence": new_conf,
                            "actual_exit": new_exit or None,
                            "pnl": new_pnl or None, "post_trade_review": new_review,
                        })
                        st.session_state[edit_key] = False
                        st.rerun()

            if st.button("Delete", key=f"btn_del_t_{t['id']}"):
                delete_trade(t["id"])
                st.rerun()

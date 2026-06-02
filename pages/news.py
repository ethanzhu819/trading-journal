import streamlit as st
from database import add_event, get_events, update_event, delete_event

st.set_page_config(page_title="News & Market Events", layout="wide")
st.title("News & Market Events")

CATEGORIES = ["Fed", "Earnings", "Macro", "Geopolitical", "Sector", "Other"]
ASSET_CLASSES = ["Equities", "Crypto", "FX", "Fixed Income", "Commodities", "Other"]

# ── Add Event ─────────────────────────────────────────────────────────────────

with st.expander("Add New Event", expanded=False):
    with st.form("add_event_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date = col1.date_input("Date")
        category = col2.selectbox("Category", CATEGORIES)
        event_title = st.text_input("Event Title *")
        col3, col4 = st.columns(2)
        asset_class = col3.selectbox("Asset Class", ASSET_CLASSES)
        importance = col4.slider("Importance", 1, 5, 3)
        source_notes = st.text_input("Source / Notes")
        market_reaction = st.text_area("Market Reaction", height=80)
        my_interpretation = st.text_area("My Interpretation", height=80)
        tags = st.text_input("Tags (comma-separated)")

        submitted = st.form_submit_button("Add Event")
        if submitted:
            if not event_title:
                st.error("Event Title is required.")
            else:
                add_event({
                    "date": str(date),
                    "category": category,
                    "event_title": event_title,
                    "source_notes": source_notes,
                    "asset_class": asset_class,
                    "market_reaction": market_reaction,
                    "my_interpretation": my_interpretation,
                    "importance": importance,
                    "tags": tags,
                })
                st.success("Event added.")
                st.rerun()

# ── Filters ───────────────────────────────────────────────────────────────────

st.subheader("Events Log")
with st.expander("Filters", expanded=False):
    fc1, fc2, fc3, fc4 = st.columns(4)
    f_category = fc1.selectbox("Category", ["All"] + CATEGORIES, key="f_cat")
    f_asset = fc2.selectbox("Asset Class", ["All"] + ASSET_CLASSES, key="f_asset")
    f_from = fc3.date_input("From", value=None, key="f_from")
    f_to = fc4.date_input("To", value=None, key="f_to")

filters = {
    "category": f_category if f_category != "All" else None,
    "asset_class": f_asset if f_asset != "All" else None,
    "date_from": str(f_from) if f_from else None,
    "date_to": str(f_to) if f_to else None,
}

events = get_events(filters)

if not events:
    st.info("No events found.")
else:
    for e in events:
        with st.expander(f"{e['date']} | {e['event_title']} [{e['category']}]"):
            col_a, col_b = st.columns(2)
            col_a.markdown(f"**Asset Class:** {e['asset_class']}")
            col_b.markdown(f"**Importance:** {e['importance']}/5")
            st.markdown(f"**Source/Notes:** {e['source_notes'] or '—'}")
            st.markdown(f"**Market Reaction:** {e['market_reaction'] or '—'}")
            st.markdown(f"**My Interpretation:** {e['my_interpretation'] or '—'}")
            st.markdown(f"**Tags:** {e['tags'] or '—'}")

            edit_key = f"edit_{e['id']}"
            if st.button("Edit", key=f"btn_edit_{e['id']}"):
                st.session_state[edit_key] = True

            if st.session_state.get(edit_key):
                with st.form(f"edit_form_{e['id']}"):
                    ec1, ec2 = st.columns(2)
                    new_date = ec1.date_input("Date", value=e["date"], key=f"ed_{e['id']}")
                    new_cat = ec2.selectbox("Category", CATEGORIES,
                                            index=CATEGORIES.index(e["category"]) if e["category"] in CATEGORIES else 0,
                                            key=f"ec_{e['id']}")
                    new_title = st.text_input("Event Title", value=e["event_title"], key=f"et_{e['id']}")
                    new_ac = st.selectbox("Asset Class", ASSET_CLASSES,
                                          index=ASSET_CLASSES.index(e["asset_class"]) if e["asset_class"] in ASSET_CLASSES else 0,
                                          key=f"eac_{e['id']}")
                    new_imp = st.slider("Importance", 1, 5, e["importance"] or 3, key=f"ei_{e['id']}")
                    new_src = st.text_input("Source/Notes", value=e["source_notes"] or "", key=f"es_{e['id']}")
                    new_mr = st.text_area("Market Reaction", value=e["market_reaction"] or "", key=f"emr_{e['id']}")
                    new_interp = st.text_area("My Interpretation", value=e["my_interpretation"] or "", key=f"emi_{e['id']}")
                    new_tags = st.text_input("Tags", value=e["tags"] or "", key=f"etg_{e['id']}")
                    save = st.form_submit_button("Save")
                    if save:
                        update_event(e["id"], {
                            "date": str(new_date), "category": new_cat,
                            "event_title": new_title, "source_notes": new_src,
                            "asset_class": new_ac, "market_reaction": new_mr,
                            "my_interpretation": new_interp, "importance": new_imp,
                            "tags": new_tags,
                        })
                        st.session_state[edit_key] = False
                        st.rerun()

            if st.button("Delete", key=f"btn_del_{e['id']}"):
                delete_event(e["id"])
                st.rerun()

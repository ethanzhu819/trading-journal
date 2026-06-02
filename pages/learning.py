import datetime
import io
import streamlit as st
from pathlib import Path
from streamlit_paste_button import paste_image_button
from database import (
    add_note, get_notes, update_note, delete_note,
    add_image, get_images_for_note, delete_image,
    get_events, get_trades,
)

st.set_page_config(page_title="Learning Notes", layout="wide")
st.title("Learning Notes")

CATEGORIES = [
    "Macro", "Sectors", "Companies", "Options/Volatility",
    "Risk Management", "Trading Psychology", "Python/Data", "Other",
]

UPLOAD_DIR = Path(__file__).parent.parent / "uploads" / "learning"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

if "add_note_pending_images" not in st.session_state:
    st.session_state["add_note_pending_images"] = []
if "add_note_paste_counter" not in st.session_state:
    st.session_state["add_note_paste_counter"] = 0


def event_options():
    events = get_events()
    opts = {0: "None"}
    opts.update({e["id"]: f"{e['date']} — {e['event_title']}" for e in events})
    return opts


def trade_options():
    trades = get_trades()
    opts = {0: "None"}
    opts.update({t["id"]: f"{t['date']} — {t['asset']} {t['direction']}" for t in trades})
    return opts


def save_uploaded_file(uploaded_file) -> str:
    dest = UPLOAD_DIR / uploaded_file.name
    suffix = 1
    while dest.exists():
        dest = UPLOAD_DIR / f"{Path(uploaded_file.name).stem}_{suffix}{Path(uploaded_file.name).suffix}"
        suffix += 1
    dest.write_bytes(uploaded_file.read())
    return str(dest)


def save_pasted_image(image_data) -> str:
    buf = io.BytesIO()
    image_data.save(buf, format="PNG")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    dest = UPLOAD_DIR / f"pasted_{timestamp}.png"
    dest.write_bytes(buf.getvalue())
    return str(dest)


# ── Add Note ──────────────────────────────────────────────────────────────────

with st.expander("Add New Learning Note", expanded=False):
    with st.form("add_note_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date = col1.date_input("Date")
        category = col2.selectbox("Category", CATEGORIES)
        title = st.text_input("Title *")
        subcategory = st.text_input("Subcategory")
        content = st.text_area("Content", height=200)
        tags = st.text_input("Tags (comma-separated)")

        col3, col4 = st.columns(2)
        ev_opts = event_options()
        tr_opts = trade_options()
        related_event_id = col3.selectbox(
            "Related News Event", list(ev_opts.keys()), format_func=lambda x: ev_opts[x]
        )
        related_trade_id = col4.selectbox(
            "Related Trade", list(tr_opts.keys()), format_func=lambda x: tr_opts[x]
        )

        uploaded_files = st.file_uploader(
            "Attach Images", type=["png", "jpg", "jpeg", "gif", "webp"],
            accept_multiple_files=True
        )
        captions_input = st.text_input("Image Captions (comma-separated, one per image)")

        submitted = st.form_submit_button("Add Note")
        if submitted:
            if not title:
                st.error("Title is required.")
            else:
                note_id = add_note({
                    "date": str(date),
                    "title": title,
                    "category": category,
                    "subcategory": subcategory,
                    "content": content,
                    "tags": tags,
                    "related_event_id": related_event_id if related_event_id != 0 else None,
                    "related_trade_id": related_trade_id if related_trade_id != 0 else None,
                })
                captions = [c.strip() for c in captions_input.split(",")] if captions_input else []
                for i, f in enumerate(uploaded_files):
                    path = save_uploaded_file(f)
                    add_image(note_id, path, captions[i] if i < len(captions) else "")
                for img in st.session_state["add_note_pending_images"]:
                    add_image(note_id, img["path"], img["caption"])
                st.session_state["add_note_pending_images"] = []
                st.session_state["add_note_paste_counter"] += 1
                st.success("Note added.")
                st.rerun()

    # Paste button lives outside the form so it can work
    add_counter = st.session_state["add_note_paste_counter"]
    paste_col, cap_col = st.columns([1, 2])
    with paste_col:
        add_paste_result = paste_image_button(
            "Paste Image from Clipboard", key=f"add_note_paste_{add_counter}"
        )
    add_paste_caption = cap_col.text_input("Caption for pasted image", key=f"add_paste_cap_{add_counter}")

    if add_paste_result.image_data is not None:
        path = save_pasted_image(add_paste_result.image_data)
        st.session_state["add_note_pending_images"].append({"path": path, "caption": add_paste_caption})
        st.session_state["add_note_paste_counter"] += 1
        st.rerun()

    pending = st.session_state["add_note_pending_images"]
    if pending:
        st.markdown(f"**{len(pending)} pasted image(s) queued**")
        pcols = st.columns(min(len(pending), 3))
        for i, img in enumerate(pending):
            with pcols[i % 3]:
                st.image(img["path"], caption=img["caption"] or "", use_container_width=True)
        if st.button("Clear pasted images"):
            for img in pending:
                Path(img["path"]).unlink(missing_ok=True)
            st.session_state["add_note_pending_images"] = []
            st.session_state["add_note_paste_counter"] += 1
            st.rerun()

# ── Filters ───────────────────────────────────────────────────────────────────

st.subheader("Notes")
with st.expander("Filters", expanded=False):
    fc1, fc2, fc3 = st.columns(3)
    f_cat = fc1.selectbox("Category", ["All"] + CATEGORIES, key="f_cat")
    f_sub = fc2.text_input("Subcategory contains", key="f_sub")
    f_tags = fc3.text_input("Tag contains", key="f_tags")

filters = {
    "category": f_cat if f_cat != "All" else None,
    "subcategory": f_sub or None,
    "tags": f_tags or None,
}

notes = get_notes(filters)

if not notes:
    st.info("No notes found.")
else:
    ev_opts = event_options()
    tr_opts = trade_options()

    for n in notes:
        label = f"{n['date']} | {n['title']} [{n['category']}]"
        with st.expander(label):
            col_a, col_b = st.columns(2)
            col_a.markdown(f"**Category:** {n['category']}")
            col_b.markdown(f"**Subcategory:** {n['subcategory'] or '—'}")
            st.markdown(f"**Tags:** {n['tags'] or '—'}")

            if n["related_event_id"] and n["related_event_id"] in ev_opts:
                st.markdown(f"**Related Event:** {ev_opts[n['related_event_id']]}")
            if n["related_trade_id"] and n["related_trade_id"] in tr_opts:
                st.markdown(f"**Related Trade:** {tr_opts[n['related_trade_id']]}")

            st.markdown("**Content:**")
            st.markdown(n["content"] or "—")

            images = get_images_for_note(n["id"])
            if images:
                st.markdown("**Images:**")
                img_cols = st.columns(min(len(images), 3))
                for i, img in enumerate(images):
                    img_path = Path(img["image_path"])
                    if img_path.exists():
                        with img_cols[i % 3]:
                            st.image(str(img_path), caption=img["caption"] or "", use_container_width=True)
                            if st.button("Remove image", key=f"del_img_{img['id']}"):
                                delete_image(img["id"])
                                img_path.unlink(missing_ok=True)
                                st.rerun()

            paste_counter_key = f"paste_counter_{n['id']}"
            if paste_counter_key not in st.session_state:
                st.session_state[paste_counter_key] = 0
            counter = st.session_state[paste_counter_key]

            paste_col, cap_col = st.columns([1, 2])
            with paste_col:
                paste_result = paste_image_button(
                    "Paste Image from Clipboard", key=f"paste_{n['id']}_{counter}"
                )
            paste_caption = cap_col.text_input(
                "Caption for pasted image", key=f"paste_cap_{n['id']}_{counter}"
            )
            if paste_result.image_data is not None:
                path = save_pasted_image(paste_result.image_data)
                add_image(n["id"], path, paste_caption)
                st.session_state[paste_counter_key] += 1
                st.rerun()

            st.caption(f"Created: {n['created_at']}  |  Updated: {n['updated_at']}")

            edit_key = f"edit_note_{n['id']}"
            if st.button("Edit", key=f"btn_edit_n_{n['id']}"):
                st.session_state[edit_key] = True

            if st.session_state.get(edit_key):
                with st.form(f"edit_note_form_{n['id']}"):
                    ec1, ec2 = st.columns(2)
                    new_date = ec1.date_input("Date", value=n["date"], key=f"nd_{n['id']}")
                    new_cat = ec2.selectbox(
                        "Category", CATEGORIES,
                        index=CATEGORIES.index(n["category"]) if n["category"] in CATEGORIES else 0,
                        key=f"nc_{n['id']}"
                    )
                    new_title = st.text_input("Title", value=n["title"], key=f"nt_{n['id']}")
                    new_sub = st.text_input("Subcategory", value=n["subcategory"] or "", key=f"ns_{n['id']}")
                    new_content = st.text_area("Content", value=n["content"] or "", height=200, key=f"nco_{n['id']}")
                    new_tags = st.text_input("Tags", value=n["tags"] or "", key=f"ntg_{n['id']}")

                    ev_list = list(ev_opts.keys())
                    cur_ev = n["related_event_id"] if n["related_event_id"] in ev_opts else 0
                    tr_list = list(tr_opts.keys())
                    cur_tr = n["related_trade_id"] if n["related_trade_id"] in tr_opts else 0

                    new_ev = st.selectbox(
                        "Related Event", ev_list,
                        index=ev_list.index(cur_ev),
                        format_func=lambda x: ev_opts[x],
                        key=f"nev_{n['id']}"
                    )
                    new_tr = st.selectbox(
                        "Related Trade", tr_list,
                        index=tr_list.index(cur_tr),
                        format_func=lambda x: tr_opts[x],
                        key=f"ntr_{n['id']}"
                    )

                    new_files = st.file_uploader(
                        "Add More Images", type=["png", "jpg", "jpeg", "gif", "webp"],
                        accept_multiple_files=True, key=f"nf_{n['id']}"
                    )
                    new_captions = st.text_input("New Image Captions (comma-separated)", key=f"nfc_{n['id']}")

                    if st.form_submit_button("Save"):
                        update_note(n["id"], {
                            "date": str(new_date), "title": new_title,
                            "category": new_cat, "subcategory": new_sub,
                            "content": new_content, "tags": new_tags,
                            "related_event_id": new_ev if new_ev != 0 else None,
                            "related_trade_id": new_tr if new_tr != 0 else None,
                        })
                        caps = [c.strip() for c in new_captions.split(",")] if new_captions else []
                        for i, f in enumerate(new_files):
                            path = save_uploaded_file(f)
                            add_image(n["id"], path, caps[i] if i < len(caps) else "")
                        st.session_state[edit_key] = False
                        st.rerun()

            if st.button("Delete Note", key=f"btn_del_n_{n['id']}"):
                for img in get_images_for_note(n["id"]):
                    Path(img["image_path"]).unlink(missing_ok=True)
                delete_note(n["id"])
                st.rerun()

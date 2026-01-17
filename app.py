import streamlit as st
import pandas as pd
from storage import CourseStorage
from mapping_engine import MappingEngine

# CONFIG
st.set_page_config(page_title="ModMatch: SEP Planner", layout="wide")

st.markdown("""
    <style>
    div.stButton > button { width: 100%; height: 3em; font-weight: bold; }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# INITIALISATION
@st.cache_resource
def init_backend():
    storage = CourseStorage()
    engine = MappingEngine()
    
    # Load default data from the /data folder automatically
    try:
        storage.import_source_data("data/home_modules.csv", "data/partner_modules.csv")
    except Exception as e:
        st.error(f"Initial data load failed: {e}")
        
    return storage, engine

if 'storage' not in st.session_state:
    storage, engine = init_backend()
    st.session_state.storage = storage
    st.session_state.engine = engine
else:
    storage = st.session_state.storage
    engine = st.session_state.engine

if 'preview' not in st.session_state:
    st.session_state.preview = []

st.title("ModMatch: SEP Planner")
st.write("Match NUS modules with Partner University courses using semantic similarity.")

st.header("Step 1: Select Modules for Comparison")
col1, col2 = st.columns(2)

with col1:
    st.subheader("NUS Modules")
    home_sel = st.dataframe(
        storage.get_nus_entries(), 
        on_select="rerun", 
        selection_mode="single-row", 
        hide_index=True,
        use_container_width=True
    )

with col2:
    st.subheader("Partner University Modules")
    partner_sel = st.dataframe(
        storage.get_partner_entries(), 
        on_select="rerun", 
        selection_mode="multi-row", 
        hide_index=True,
        use_container_width=True
    )

# Logic to generate the preview list
if st.button("Generate Comparison Preview", type="primary"):
    h_rows = home_sel.selection.rows
    p_rows = partner_sel.selection.rows

    if h_rows and p_rows:
        # Get data from storage using selection indices
        data_bundle = storage.get_course_pairs(h_rows[0], p_rows)
        
        # call engine to generate 1-to-1 Mapping objects
        st.session_state.preview = engine.get_preview_pairings(
            data_bundle['nus_course'].iloc[0], 
            data_bundle['partner_courses']
        )
        st.success(f"Calculated {len(st.session_state.preview)} similarity scores!")
    else:
        st.warning("Please select 1 NUS module and at least 1 Partner course.")

st.divider()

# PREVIEW AND SELECT
if st.session_state.preview:
    st.header("Step 2: Review & Finalize Mappings")
    st.write("Select the pairings you want to save to your final plan.")
    
    # Prepare data for the preview dataframe
    preview_df = pd.DataFrame([{
        "NUS Code": m.home_row['nus_code'],
        "Partner": m.partner_row['pu'],
        "Partner Code": m.partner_row['pu_code'],
        "Match Score": f"{m.similarity_score:.1%}"
    } for m in st.session_state.preview])
    
    review_sel = st.dataframe(
        preview_df, 
        on_select="rerun", 
        selection_mode="multi-row", 
        hide_index=True,
        use_container_width=True
    )

    if st.button("Confirm Selections & Add to Plan"):
        selected_preview_indices = review_sel.selection.rows
        
        if selected_preview_indices:
            # use engine to extract original indices from our Mapping objects
            final_payload = engine.finalize_selections(
                st.session_state.preview, 
                selected_preview_indices
            )
            
            # Pass directly to CourseStorage pairing logic
            storage.add_pairing(
                nus_index=final_payload["nus_index"],
                partner_index=final_payload["partner_indices"],
                score=final_payload["scores"]
            )
            
            # refresh preview
            st.session_state.preview = []
            st.success("Successfully added to your Final Plan!")
            st.rerun()
        else:
            st.info("Please select the rows you want to keep from the table above.")

# SHOW FINAL PLANNER
st.divider()
st.header("Exchange Plan")

pairings = storage.get_pairings()

if pairings.empty:
    st.info("No pairings saved yet. Complete Step 1 and 2 to see your plan here.")
else:
    # Display the final results from storage.pairings_df
    st.dataframe(pairings, use_container_width=True, hide_index=True)
    
    # Individual expansion for details
    for i, row in pairings.iterrows():
        # Get full details using helper from storage
        details = storage.get_course_details_for_pairing(i)
        
        with st.expander(f"Details: {row['nus_code']} ↔ {row['pu_code']} ({row['pu']})"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**NUS Module:** {details['nus_module']['nus_mod']}")
                st.caption(details['nus_module']['nus_desc'])
            with c2:
                st.write(f"**Partner Course:** {details['partner_course']['pu_mod']}")
                st.caption(details['partner_course']['pu_desc'])
            
            if st.button("Delete Mapping", key=f"del_{i}"):
                storage.remove_pairing(i)
                st.rerun()

    if st.button("Clear Entire Plan"):
        storage.clear_all()
        st.rerun()

# --- SIDEBAR FOR MANUAL IMPORT ---
with st.sidebar:
    st.header("Data Stuff")
    st.write("Upload your own module lists to override the defaults.")
    
    new_nus = st.file_uploader("Upload NUS Modules (CSV)", type="csv")
    new_pu = st.file_uploader("Upload Partner Modules (CSV)", type="csv")
    
    if st.button("Update Module Tables"):
        if new_nus or new_pu:
            try:
                storage.import_source_data(new_nus, new_pu)
                st.success("Tables updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please upload at least one file.")
            
    st.divider()
    st.caption("Required Headers:")
    st.caption("NUS: nus_code, nus_mod, nus_desc")
    st.caption("Partner: pu, pu_mod, pu_code, pu_desc")
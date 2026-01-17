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

# --- SHOW FINAL PLANNER ---
st.divider()
st.header("Exchange Plan")

pairings = storage.get_pairings()

if pairings.empty:
    st.info("No pairings saved yet. Complete Step 1 and 2 to see your plan here.")
else:
    # 1. Action Header
    col_h1, col_h2 = st.columns([0.8, 0.2])
    with col_h2:
        if st.button("🗑️ Clear All", use_container_width=True):
            storage.clear_all()
            st.rerun()

    # 2. Table Header
    # We create a simulated table header using columns
    st.markdown("""
        <div style='display: flex; font-weight: bold; border-bottom: 2px solid #ccc; padding-bottom: 5px; margin-bottom: 10px;'>
            <div style='flex: 2;'>NUS Module</div>
            <div style='flex: 2;'>Partner University</div>
            <div style='flex: 2;'>Partner Module</div>
            <div style='flex: 1;'>Match</div>
            <div style='flex: 0.5;'></div>
        </div>
    """, unsafe_allow_html=True)

    # 3. List of Pairings
    for i, row in pairings.iterrows():
        # Get full details for the expander content
        details = storage.get_course_details_for_pairing(i)
        
        # Create columns: 4 for data, 1 for the delete button
        c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1, 0.5])
        
        with c1:
            st.write(f"**{row['nus_code']}**")
        with c2:
            st.write(row['pu'])
        with c3:
            st.write(row['pu_code'])
        with c4:
            # Color the score based on strength
            score = row['score']
            color = "green" if score > 0.7 else "orange" if score > 0.4 else "red"
            st.markdown(f"<span style='color:{color}; font-weight:bold;'>{score:.1%}</span>", unsafe_allow_html=True)
        with c5:
            # Delete button at the end of the row
            if st.button("❌", key=f"del_{i}", help="Remove this pairing"):
                storage.remove_pairing(i)
                st.rerun()
        
        # 4. Integrated Dropdown for Details
        # This sits immediately under the row data
        with st.expander("View Descriptions"):
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.markdown(f"**{details['nus_module']['nus_mod']}**")
                st.caption(details['nus_module']['nus_desc'])
            with d_col2:
                st.markdown(f"**{details['partner_course']['pu_mod']}**")
                st.caption(details['partner_course']['pu_desc'])
        
        st.markdown("---") 

# --- SIDEBAR: DATA PERSISTENCE & INTEGRATION ---
with st.sidebar:
    st.header("📥 Bulk Import")
    st.write("Concatenate modules from an external CSV file into your app data.")
    
    # Text input for filepath as per your logic
    import_path = st.text_input("Source CSV Filepath", placeholder="C:/path/to/your_data.csv")
    target_list = st.selectbox("Import to:", ["Partner Modules", "NUS Modules"])
    
    if st.button("Import & Append"):
        if import_path:
            try:
                if target_list == "Partner Modules":
                    storage.import_external_pu(import_path)
                else:
                    storage.import_external_nus(import_path)
                st.success("Data concatenated and saved to internal storage!")
                st.rerun()
            except Exception as e:
                st.error(f"Import Error: {e}")
        else:
            st.warning("Please provide a valid filepath.")
            
    st.divider()
    
    st.header("Export Result")
    st.write("Save a copy of your Exchange Plan to a custom location.")
    
    export_path = st.text_input("Export Destination Path", placeholder="C:/path/to/export_plan.csv")
    
    if st.button("Export Exchange Plan"):
        if export_path:
            try:
                storage.export_exchange_plan(export_path)
                st.success(f"Plan successfully exported to {export_path}")
            except Exception as e:
                st.error(f"Export Error: {e}")
        else:
            st.warning("Please provide a destination filepath.")

    st.divider()
    st.caption("Internal data is saved automatically in the /data folder.")
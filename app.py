import streamlit as st
import pandas as pd
from module_repo import ModuleRepository
from mapping_engine import MappingEngine

# --- PAGE SETUP ---
st.set_page_config(page_title="ModMatch: SEP Planner", layout="wide")

st.markdown("""
    <style>
    div.stButton > button { width: 100%; height: 3em; font-weight: bold; }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_backend():
    repo = ModuleRepository("data/home_modules.csv", "data/partner_modules.csv")
    engine = MappingEngine()
    return repo, engine

repo, engine = init_backend()

# Initialize Session States
if 'planner' not in st.session_state:
    st.session_state.planner = []
if 'preview' not in st.session_state:
    st.session_state.preview = []

st.title("🔗 ModMatch: Multi-Step Planner")

# --- SECTION 1: SELECTION ---
st.header("Step 1: Select Modules for Comparison")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Home University (NUS)")
    home_sel = st.dataframe(
        repo.df_home, 
        on_select="rerun", 
        selection_mode="single-row", 
        hide_index=True,
        use_container_width=True
    )

with col2:
    st.subheader("✈️ Partner University")
    partner_sel = st.dataframe(
        repo.df_partner, 
        on_select="rerun", 
        selection_mode="multi-row", 
        hide_index=True,
        use_container_width=True
    )

if st.button("Generate Comparison Preview", type="primary"):
    h_idx = home_sel.selection.rows
    p_indices = partner_sel.selection.rows

    if h_idx and p_indices:
        # Extract the actual data rows from the indices
        h_row = repo.df_home.iloc[h_idx[0]]
        p_rows = repo.df_partner.iloc[p_indices]
        
        # Call abstracted logic to get preview objects
        st.session_state.preview = engine.get_preview_pairings(h_row, p_rows)
        st.success("Comparison complete! Review scores below.")
    else:
        st.warning("Please select 1 module from Home and at least 1 from Partner.")

st.divider()

# --- SECTION 2: PREVIEW & CONFIRMATION ---
if st.session_state.preview:
    st.header("Step 2: Review & Finalize Mappings")
    
    # Create a simple DataFrame for the preview table
    preview_data = [{
        "Home Code": m.home_row['code'],
        "Partner Code": m.partner_row['code'],
        "AI Similarity": f"{m.similarity_score:.1%}"
    } for m in st.session_state.preview]
    
    preview_df = pd.DataFrame(preview_data)
    
    # Show the preview table for the user to choose pairings
    review_sel = st.dataframe(
        preview_df, 
        on_select="rerun", 
        selection_mode="multi-row", 
        hide_index=True,
        use_container_width=True
    )

    if st.button("Confirm Selections & Add to Plan"):
        selected_review_indices = review_sel.selection.rows
        
        if selected_review_indices:
            # Call abstracted logic to finalize the data
            final_mappings = engine.finalize_selections(st.session_state.preview, selected_review_indices)
            
            # Add to permanent planner
            st.session_state.planner.extend(final_mappings)
            
            # Clear preview to reset the UI
            st.session_state.preview = []
            st.success(f"Added {len(final_mappings)} mappings to your plan!")
            st.rerun()
        else:
            st.info("Select the rows you wish to keep from the preview table above.")

# --- SECTION 3: THE FINAL PLANNER ---
st.divider()
st.header("📋 Final Exchange Planner")

if not st.session_state.planner:
    st.info("Your final planner is empty.")
else:
    for i, m in enumerate(st.session_state.planner):
        label = f"{m.home_row['code']} ↔ {m.partner_row['code']} | Match: {m.similarity_score:.1%}"
        with st.expander(label):
            st.write(f"**Home:** {m.home_row['name']}")
            st.write(f"**Partner:** {m.partner_row['name']}")
            if st.button("Remove Mapping", key=f"perm_del_{i}"):
                st.session_state.planner.pop(i)
                st.rerun()

    if st.button("Clear All Plan Data"):
        st.session_state.planner = []
        st.rerun()
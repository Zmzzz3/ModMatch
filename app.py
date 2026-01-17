import streamlit as st
from mapping_engine import MappingEngine, Mapping
from module import Module

st.set_page_config(page_title="ModMatch Planner", layout="wide")

st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 3.5em;
        font-size: 20px !important;
        font-weight: bold;
        margin-top: 15px;
    }
    
    div[data-testid="stNotification"] {
        min-width: 100% !important;
        font-size: 18px !important;
    }
    
    div[data-testid="stNotificationContent"] {
        white-space: nowrap;
    }

    .streamlit-expanderHeader {
        font-size: 18px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_engine():
    return MappingEngine()

engine = load_engine()

if 'planner' not in st.session_state:
    st.session_state.planner = []

st.title("ModMatch: SEP Module Planner")
st.write("Build your exchange study plan by comparing and saving module mappings.")

col1, col2 = st.columns(2)

with col1:
    st.header("Home Module")
    h_code = st.text_input("Module Code", placeholder="e.g. CS2040C", key="h_code")
    h_name = st.text_input("Module Name", placeholder="e.g. Data Structures", key="h_name")
    h_desc = st.text_area("Paste Description (Home)", height=200, key="h_desc")

with col2:
    st.header("Partner Module")
    p_code = st.text_input("Module Code", placeholder="e.g. IT1202", key="p_code")
    p_name = st.text_input("Module Name", placeholder="e.g. Intro to Algorithms", key="p_name")
    p_desc = st.text_area("Paste Description (Partner)", height=200, key="p_desc")

if st.button("Compare & Add to Planner", type="primary"):
    if h_desc.strip() and p_desc.strip():
        mod_home = Module("Home Uni", h_name, h_code, h_desc)
        mod_partner = Module("Partner Uni", p_name, p_code, p_desc)

        mapping = Mapping(mod_home, mod_partner)
        score = engine.check_and_score_mapping(mapping)
        
        st.session_state.planner.append(mapping)
        st.success(f"Successfully added {h_code} ↔ {p_code} to your planner!")
    else:
        st.error("Please provide descriptions for both modules to run the AI comparison.")

st.divider()
st.header("Your Exchange Plan")

if not st.session_state.planner:
    st.info("Your planner is currently empty. Add modules above to see them here.")
else:
    # Iterate through saved mappings
    for i, item in enumerate(st.session_state.planner):
        score_pct = item.similarity_score * 100
        label = f"{item.home_module.code} ↔ {item.partner_module.code} | Match: {score_pct:.1f}%"
        
        with st.expander(label):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Home ({item.home_module.code}):** {item.home_module.name}")
            with c2:
                st.write(f"**Partner ({item.partner_module.code}):** {item.partner_module.name}")
            
            # Semantic Feedback
            if item.similarity_score >= 0.8:
                st.success("Strong Semantic Match")
            elif item.similarity_score >= 0.6:
                st.warning("Moderate Match - Manual Check Advised")
            else:
                st.error("Low Match - Potentially Different Content")
            
            del_col, spacer = st.columns([1, 4])
            with del_col:
                if st.button("🗑️ Delete", key=f"delete_{i}"):
                    st.session_state.planner.pop(i)
                    st.rerun()

    st.write("---")
    if st.button("Clear All Mappings", type="secondary"):
        st.session_state.planner = []
        st.rerun()


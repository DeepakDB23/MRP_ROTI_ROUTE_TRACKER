# app.py

import streamlit as st
from config import PAGE_TITLE, PAGE_LAYOUT, TAB_TITLES  # Import configuration
# Import initialization (now includes GSheets load)
from utils import initialize_state
from admin_section import display_admin_section  # Import admin section display
from tabs import add_trip_tab, edit_trip_tab, view_records_tab  # Import tab modules

# --- Configuration ---
st.set_page_config(layout=PAGE_LAYOUT, page_title=PAGE_TITLE)

# --- Main App Layout ---

st.title(PAGE_TITLE)

# Initialize state and load data from Google Sheets
initialize_state()

# Display Admin Section in Sidebar
display_admin_section()

# Tab navigation
# Use a unique key for the radio button to prevent potential issues with reruns
chosen_tab = st.radio("Navigation", TAB_TITLES, index=TAB_TITLES.index(
    st.session_state.current_tab), horizontal=True, key="main_navigation_radio")

# Update session state for tab
st.session_state.current_tab = chosen_tab

# --- Tab Content ---

# Display content based on the chosen tab
if chosen_tab == "Add New Trip":
    add_trip_tab.display_add_trip_tab()
elif chosen_tab == "Edit Existing Trip":
    edit_trip_tab.display_edit_trip_tab()
elif chosen_tab == "View Records":
    view_records_tab.display_view_records_tab()

st.markdown("---")
st.markdown("Engineered by MRP Boyz, 👨‍💻 by DB23 ", unsafe_allow_html=True)

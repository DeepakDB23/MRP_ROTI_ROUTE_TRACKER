# tabs/add_trip_tab.py

import streamlit as st
from datetime import datetime
# Import necessary functions
from utils import get_all_stores, get_drivers_list, add_trip
from config import VEHICLE_OPTIONS  # Import vehicle options


def display_add_trip_tab():
    """Displays the UI and handles logic for the Add New Trip tab."""
    st.header("Add New Trip")
    all_stores = get_all_stores()
    drivers = get_drivers_list()

    with st.form("add_trip_form"):
        add_date = st.date_input("Date:", datetime.now())
        # Use vehicle options from config
        add_vehicle = st.selectbox("Vehicle:", VEHICLE_OPTIONS)
        add_start_km = st.number_input(
            "Start KM:", min_value=0, value=0, step=1)
        add_end_km = st.number_input("End KM:", min_value=0, value=0, step=1)
        # Use driver options from utils
        add_driver = st.selectbox("Driver Name:", options=drivers)
        # Use multiselect for route based on stores from utils
        add_route_list = st.multiselect(
            "Route (Select Stores):", options=all_stores)
        add_remarks = st.text_area("Remarks:")

        submitted = st.form_submit_button("Add Trip")
        if submitted:
            # Check if required fields are filled (Vehicle, Driver, and at least one store in Route)
            if add_vehicle and add_driver and add_route_list:
                if add_trip(add_date, add_vehicle, add_start_km, add_end_km, add_driver, add_route_list, add_remarks):
                    # Streamlit forms automatically clear on successful submission
                    pass
            else:
                st.error(
                    "Please fill in all required fields (Vehicle, Driver Name, and select at least one Store for Route).")

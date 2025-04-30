# admin_section.py

import streamlit as st
import pandas as pd
from config import VEHICLE_OPTIONS  # Import vehicle options


def display_admin_section():
    """Displays admin login and license plate update form in the sidebar."""
    st.sidebar.header("Admin")
    if not st.session_state.get('logged_in', False):
        # Login Form
        with st.sidebar.form("login_form"):
            username = st.text_input("Username", key="admin_user")
            password = st.text_input(
                "Password", type="password", key="admin_pass")
            login_button = st.form_submit_button("Login")

            if login_button:
                # Use st.secrets for secure storage of credentials
                # You need to create a .streamlit/secrets.toml file locally
                # and add secrets in Streamlit Cloud settings
                # [admin]
                # username = "your_admin_username"
                # password = "your_admin_password"
                admin_user = st.secrets.get("admin", {}).get("username")
                admin_pass = st.secrets.get("admin", {}).get("password")

                if not admin_user or not admin_pass:
                    st.error(
                        "Admin credentials not configured in Streamlit Secrets.")
                elif username == admin_user and password == admin_pass:
                    st.session_state.logged_in = True
                    st.rerun()  # Rerun to show admin options
                else:
                    st.error("Invalid credentials")

    if st.session_state.get('logged_in', False):
        st.sidebar.success("Admin Logged In")
        st.sidebar.subheader("Vehicle License Plates")

        # License Plate Update Form
        with st.sidebar.form("admin_form_update_plate"):
            # Use vehicle options from config, excluding the empty default
            vehicle_options_clean = [v for v in VEHICLE_OPTIONS if v]
            vehicle = st.selectbox(
                "Select Vehicle", vehicle_options_clean, key="admin_veh_select_plate")

            # Display current plate
            current_plate = "Not Set"
            df_vehicles_state = st.session_state.df_vehicles
            vehicle_row = df_vehicles_state[df_vehicles_state['Vehicle'] == vehicle]
            if not vehicle_row.empty:
                plate_val = vehicle_row['License Plate'].iloc[0]
                # Check for empty string or NaN before displaying
                current_plate = plate_val if plate_val and pd.notna(
                    plate_val) else "Not Set"

            st.info(f"Current Plate for Vehicle {vehicle}: {current_plate}")

            new_plate = st.text_input(
                "Enter New License Plate", key="admin_new_plate_input").strip()

            update_plate_button = st.form_submit_button("Update Plate")
            if update_plate_button:
                if new_plate:  # Only update if a new plate is entered
                    df_vehicles = st.session_state.df_vehicles.copy()
                    idx = df_vehicles.index[df_vehicles['Vehicle'] == vehicle].tolist(
                    )

                    if idx:  # Update existing entry
                        df_vehicles.loc[idx[0], 'License Plate'] = new_plate
                    else:  # Add new entry if vehicle doesn't exist
                        new_veh_df = pd.DataFrame([
                            {'Vehicle': vehicle, 'License Plate': new_plate}
                        ])
                        df_vehicles = pd.concat(
                            [df_vehicles, new_veh_df], ignore_index=True)

                    st.session_state.df_vehicles = df_vehicles
                    st.success(
                        f"Plate for Vehicle {vehicle} updated to {new_plate}!")
                    st.rerun()  # Rerun to show updated current plate info
                else:
                    st.warning("Please enter a new license plate value.")

        # Logout Button (outside the form)
        if st.sidebar.button("Logout", key="admin_logout_btn"):
            st.session_state.logged_in = False
            st.rerun()  # Rerun to show login form

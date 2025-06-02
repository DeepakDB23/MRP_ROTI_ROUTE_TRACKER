import streamlit as st
import pandas as pd
from datetime import datetime
from config import VEHICLE_OPTIONS, GSHEETS_VEHICLES_COLUMNS
from utils import save_vehicle_plates_to_gsheets, record_fleet_change_trip


def display_admin_section():
    """Displays admin login and license plate update form in the sidebar."""

    # Initialize all session state variables
    if "admin_new_plate_input" not in st.session_state:
        st.session_state.admin_new_plate_input = ""
    if "admin_comments_input" not in st.session_state:
        st.session_state.admin_comments_input = ""
    if "df_vehicles" not in st.session_state:
        st.session_state.df_vehicles = pd.DataFrame(
            columns=GSHEETS_VEHICLES_COLUMNS)

    st.sidebar.header("Admin")

    # Login Form
    if not st.session_state.get('logged_in', False):
        with st.sidebar.form("login_form"):
            username = st.text_input("Username", key="admin_user_input")
            password = st.text_input(
                "Password", type="password", key="admin_pass_input")
            login_button = st.form_submit_button("Login")

            if login_button:
                submitted_username = st.session_state.admin_user_input
                submitted_password = st.session_state.admin_pass_input

                admin_user_secret = st.secrets.get("admin", {}).get("username")
                admin_pass_secret = st.secrets.get("admin", {}).get("password")

                if not admin_user_secret or not admin_pass_secret:
                    st.error(
                        "Admin credentials not configured in Streamlit Secrets.")
                elif submitted_username == admin_user_secret and submitted_password == admin_pass_secret:
                    st.session_state.logged_in = True
                    st.session_state.admin_user_display_name = submitted_username
                    if 'admin_user_input' in st.session_state:
                        del st.session_state['admin_user_input']
                    if 'admin_pass_input' in st.session_state:
                        del st.session_state['admin_pass_input']
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    # Admin Interface when logged in
    if st.session_state.get('logged_in', False):
        st.header("Vehicle License Plate Management")

        # Display current vehicle data
        df_vehicles = st.session_state.df_vehicles
        if not df_vehicles.empty:
            st.dataframe(df_vehicles, hide_index=True)

        # Update Form
        with st.form("update_vehicle_form", clear_on_submit=True):
            selected_vehicle = st.selectbox(
                "Select Vehicle:",
                options=VEHICLE_OPTIONS,
                key="admin_vehicle_select"
            )

            # Get current plate for selected vehicle
            current_plate = ""
            if not df_vehicles.empty:
                vehicle_data = df_vehicles[df_vehicles['Vehicle']
                                           == selected_vehicle]
                if not vehicle_data.empty:
                    current_plate = vehicle_data.iloc[0]['License Plate']

            new_plate = st.text_input(
                "New License Plate:",
                value="",
                key="admin_new_plate_input"
            )

            comments = st.text_area(
                "Comments:",
                value="",
                key="admin_comments_input"
            )

            submit_button = st.form_submit_button("Update Vehicle")

            if submit_button:
                if selected_vehicle and new_plate:
                    # Check if plate actually changed
                    plate_changed = current_plate != new_plate

                    if plate_changed or comments:
                        # Update vehicle data
                        mask = df_vehicles['Vehicle'] == selected_vehicle
                        if mask.any():
                            df_vehicles.loc[mask, 'License Plate'] = new_plate
                            df_vehicles.loc[mask, 'Comments'] = comments
                        else:
                            new_row = pd.DataFrame([{
                                'Vehicle': selected_vehicle,
                                'License Plate': new_plate,
                                'Comments': comments
                            }])
                            df_vehicles = pd.concat(
                                [df_vehicles, new_row], ignore_index=True)

                        # Save changes
                        st.session_state.df_vehicles = df_vehicles
                        save_vehicle_plates_to_gsheets()

                        # Record fleet change if plate changed
                        if plate_changed:
                            admin_name = st.session_state.get(
                                "admin_user_display_name", "Admin")
                            record_fleet_change_trip(
                                selected_vehicle,
                                current_plate,
                                new_plate,
                                admin_name
                            )

                        st.success(f"Updated {selected_vehicle} successfully!")
                        st.rerun()
                    else:
                        st.warning("No changes detected.")
                else:
                    st.error("Please fill in all required fields.")

        # Logout button
        if st.sidebar.button("Logout", key="admin_logout_btn"):
            st.session_state.logged_in = False
            st.rerun()


if __name__ == "__main__":
    display_admin_section()

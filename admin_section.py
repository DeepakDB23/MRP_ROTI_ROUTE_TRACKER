# admin_section.py

import streamlit as st
import pandas as pd
from datetime import datetime  # Import datetime to get current time for comment
# Import vehicle options and vehicle columns
from config import VEHICLE_OPTIONS, GSHEETS_VEHICLES_COLUMNS
# Import save and new record function
from utils import save_vehicle_plates_to_gsheets, record_fleet_change_trip


def display_admin_section():
    """Displays admin login and license plate update form in the sidebar."""
    st.sidebar.header("Admin")
    if not st.session_state.get('logged_in', False):
        # Login Form
        # Use a unique key for the login form
        with st.sidebar.form("login_form"):
            # Changed key slightly
            username = st.text_input("Username", key="admin_user_input")
            password = st.text_input(
                "Password", type="password", key="admin_pass_input")  # Changed key slightly
            login_button = st.form_submit_button("Login")

            if login_button:
                # Read values from state using the keys
                submitted_username = st.session_state.admin_user_input
                submitted_password = st.session_state.admin_pass_input

                # Use st.secrets for secure storage of credentials
                admin_user_secret = st.secrets.get("admin", {}).get("username")
                admin_pass_secret = st.secrets.get("admin", {}).get("password")

                if not admin_user_secret or not admin_pass_secret:
                    st.error(
                        "Admin credentials not configured in Streamlit Secrets.")
                elif submitted_username == admin_user_secret and submitted_password == admin_pass_secret:
                    st.session_state.logged_in = True
                    # Store username for potential use in logging changes, but clear input fields
                    # Store for display/logging
                    st.session_state.admin_user_display_name = submitted_username
                    if 'admin_user_input' in st.session_state:
                        del st.session_state['admin_user_input']
                    if 'admin_pass_input' in st.session_state:
                        del st.session_state['admin_pass_input']
                    st.rerun()  # Rerun to show admin options
                else:
                    st.error("Invalid credentials")

    if st.session_state.get('logged_in', False):
        st.sidebar.success("Admin Logged In")
        st.sidebar.subheader("Vehicle License Plates")

        # --- Vehicle Selection (Moved Outside Form) ---
        # Use vehicle options from config, excluding the empty default
        vehicle_options_clean = [v for v in VEHICLE_OPTIONS if v]
        # This selectbox now triggers a rerun immediately when changed.
        selected_vehicle = st.sidebar.selectbox(
            "Select Vehicle",
            vehicle_options_clean,
            key="admin_veh_select_plate"  # Keep same key for state management
            # index=0 # No need for index if "" is removed
        )

        # --- Display Current Plate and Comments (Moved Outside Form) ---
        current_plate = "Not Set"
        current_comments = ""
        # Ensure df_vehicles exists in session state and is a DataFrame
        if 'df_vehicles' in st.session_state and isinstance(st.session_state.df_vehicles, pd.DataFrame):
            df_vehicles_state = st.session_state.df_vehicles
            # Filter for the selected vehicle (read from the selectbox state)
            vehicle_row = df_vehicles_state[df_vehicles_state['Vehicle']
                                            == selected_vehicle]

            # Safely check if vehicle_row is not empty and get values
            if not vehicle_row.empty:
                # Use .iloc[0] to get the scalar value from the Series, checking for existence and NaN
                plate_val = vehicle_row.get('License Plate')  # Get the Series
                if plate_val is not None and not plate_val.empty and pd.notna(plate_val.iloc[0]):
                    current_plate = plate_val.iloc[0]
                else:
                    current_plate = "Not Set"  # Default if column missing, empty, or NaN

                comments_val = vehicle_row.get('Comments')  # Get the Series
                if comments_val is not None and not comments_val.empty and pd.notna(comments_val.iloc[0]):
                    current_comments = comments_val.iloc[0]
                else:
                    current_comments = ""  # Default if column missing, empty, or NaN
        else:
            # Handle case where df might not be ready
            st.sidebar.warning("Vehicle data not loaded yet.")

        # Display the info outside the form, reflecting the current selection
        st.sidebar.info(
            f"Current Plate for Vehicle {selected_vehicle}: **{current_plate}**")
        if current_comments:
            st.sidebar.info(f"Current Comments: {current_comments}")
        # --- End Display Current Plate and Comments ---

        # --- License Plate Update Form (Starts Here) ---
        # The form now only contains the input fields and the submit button.
        with st.sidebar.form("admin_form_update_plate"):

            # Input for new plate remains inside
            new_plate_input = st.text_input(
                "Enter New License Plate",
                key="admin_new_plate_input"  # Keep key
            ).strip()

            # Comments text area remains inside, but value uses current_comments fetched outside
            new_comments_input = st.text_area(
                "Comments:",
                value=current_comments,  # Use value fetched outside form
                key="admin_comments_input"  # Keep key
            )

            update_plate_button = st.form_submit_button("Update Plate")
            if update_plate_button:
                # Only update if a new plate or comments are entered/changed
                # Read the submitted values from session state using their keys
                submitted_new_plate = st.session_state.admin_new_plate_input.strip()
                submitted_new_comments = st.session_state.admin_comments_input

                # Compare submitted values with the current values displayed when the form was rendered
                # Allow update even if only comments changed
                plate_changed = submitted_new_plate and submitted_new_plate != current_plate
                comments_changed = submitted_new_comments != current_comments

                if plate_changed or comments_changed:
                    # Ensure df_vehicles exists before trying to modify
                    if 'df_vehicles' in st.session_state and isinstance(st.session_state.df_vehicles, pd.DataFrame):
                        df_vehicles = st.session_state.df_vehicles.copy()
                        # Use selected_vehicle which was determined outside the form
                        idx = df_vehicles.index[df_vehicles['Vehicle']
                                                == selected_vehicle].tolist()

                        # Store old plate before updating df_vehicles
                        old_plate_for_record = current_plate

                        if idx:  # Update existing entry
                            # Update plate only if a new, different one was submitted
                            if plate_changed:
                                df_vehicles.loc[idx[0],
                                                'License Plate'] = submitted_new_plate
                            # Update comments if they changed
                            if comments_changed:
                                df_vehicles.loc[idx[0],
                                                'Comments'] = submitted_new_comments
                            # If only comments changed, plate remains the same
                            elif not plate_changed:
                                # Keep current plate for logging if only comments changed
                                submitted_new_plate = current_plate

                        # Add new entry if vehicle doesn't exist (shouldn't happen with selectbox)
                        else:
                            st.warning(
                                f"Vehicle {selected_vehicle} not found in existing data. Adding new entry.")
                            # Use submitted plate, default to current if empty but comments changed
                            plate_to_add = submitted_new_plate if submitted_new_plate else current_plate
                            new_veh_df = pd.DataFrame([
                                {'Vehicle': selected_vehicle, 'License Plate': plate_to_add,
                                 'Comments': submitted_new_comments}
                            ], columns=GSHEETS_VEHICLES_COLUMNS)  # Ensure columns match
                            df_vehicles = pd.concat(
                                [df_vehicles, new_veh_df], ignore_index=True)

                        st.session_state.df_vehicles = df_vehicles
                        save_vehicle_plates_to_gsheets()  # Save changes to Google Sheets

                        # --- Record Fleet Change as a Trip Entry ---
                        # Only record a fleet change trip if the plate actually changed and is not empty
                        if plate_changed:
                            admin_name = st.session_state.get(
                                "admin_user_display_name", "Admin")  # Use stored admin name
                            record_fleet_change_trip(
                                selected_vehicle, old_plate_for_record, submitted_new_plate, admin_name)
                        # --- End Record Fleet Change ---

                        st.success(
                            f"Data for Vehicle {selected_vehicle} updated!")
                        # Clear form fields after successful submission
                        st.session_state.admin_new_plate_input = ""
                        # Reset comments input field
                        st.session_state.admin_comments_input = ""  # Clear comments input
                        st.rerun()  # Rerun to show updated info and clear form state visually
                    else:
                        st.error(
                            "Vehicle data frame not found in session state. Cannot update.")

                else:
                    st.warning(
                        "No changes detected in License Plate or Comments.")

        # Logout Button (outside the form)
        if st.sidebar.button("Logout", key="admin_logout_btn"):
            st.session_state.logged_in = False
            # Clear admin-specific session state keys on logout
            keys_to_clear = ['admin_user_input', 'admin_pass_input', 'admin_user_display_name',
                             'admin_veh_select_plate', 'admin_new_plate_input', 'admin_comments_input']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()  # Rerun to show login form

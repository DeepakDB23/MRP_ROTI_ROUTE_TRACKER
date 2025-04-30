🚚 Boyz on Wheelz - Route Tracker™
A Streamlit application for tracking vehicle trip details, including mileage, routes, drivers, and administrative fleet changes. It provides a user-friendly interface for adding and editing trips, viewing records with filters, and downloading data in various CSV formats.

Features
Trip Tracking: Record date, vehicle, start/end KM, driver, route, and remarks.

Accumulated KM Calculation: Automatically calculates the distance covered for each trip.

Driver Selection: Prepopulated list of drivers for easy selection.

Store-Based Route Entry: Select stores visited on a route using a multiselect based on predefined regions/stores.

Edit Existing Trips: Select and modify existing trip records.

Delete Trips: Remove trip records (with confirmation).

View Records: Display trip records in a table format.

Filtering: Filter records by date range and vehicle.

Latest 10 Trips View: Displays only the 10 most recent trips in the main table view after filtering.

Admin Section: (Requires login)

Update vehicle license plates.

Download Options:

Download a CSV of all trip records (including admin fields).

Download a CSV of filtered trip records (based on current date range and vehicle filters).

Generate and download a CSV of store visit counts within a specified date range.

Data Persistence: Data is stored in Streamlit's session state (Note: This is not persistent across sessions or deployments restarting. For production, consider a database).

File Structure
The project is organized into the following modular structure:

.
├── .streamlit/
│   └── secrets.toml  (Optional: for local testing of admin secrets - DO NOT COMMIT SENSITIVE DATA)
├── app.py            (Main Streamlit application entry point)
├── config.py         (Configuration settings like titles, options, mappings)
├── utils.py          (Helper functions for data manipulation, fetching data, filtering)
├── admin_section.py  (Admin login and vehicle plate update logic)
├── tabs/             (Directory containing code for each application tab)
│   ├── __init__.py   (Makes 'tabs' a Python package)
│   ├── add_trip_tab.py (Code for the "Add New Trip" tab)
│   ├── edit_trip_tab.py (Code for the "Edit Existing Trip" tab)
│   └── view_records_tab.py (Code for the "View Records" tab, filters, downloads)
└── requirements.txt  (Lists required Python packages)

Setup and Installation
Clone the Repository:

git clone <your-repo-url>
cd <your-repo-name>

Create a Virtual Environment (Recommended):

python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

Install Dependencies:

pip install -r requirements.txt

Admin Secrets (Optional for local testing):

Create a folder named .streamlit in the root directory of your project.

Inside .streamlit, create a file named secrets.toml.

Add your desired admin username and password:

[admin]
username = "your_admin_username"
password = "your_admin_password"

Remember to add .streamlit/secrets.toml to your .gitignore file before committing to prevent exposing your secrets.

Running the App Locally
Ensure your virtual environment is activated.

Navigate to the root directory of your project in the terminal.

Run the Streamlit application:

streamlit run app.py

This will open the application in your default web browser.

Admin Credentials
For the admin section to work in deployment environments like Streamlit Cloud, you must configure your secrets directly in the platform's settings.

Streamlit Cloud: Go to your app settings -> "Secrets" and add your username and password using the format admin.username and admin.password.

Deployment to Streamlit Cloud
Ensure your code is pushed to a GitHub repository.

Go to Streamlit Cloud and log in.

Click "New app" -> "From existing repo".

Select your repository, branch (usually main), and set the "Main file path" to app.py.

In "Advanced settings", add your admin secrets as described above.

Click "Deploy!".

Streamlit Cloud will automatically build and deploy your application. Subsequent pushes to the selected branch will trigger automatic redeployments.

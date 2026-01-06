import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
from datetime import datetime

# --- CONFIGURATION: MULTIPLE SHEETS ---
# Add as many campaigns as you want here. 
# Format: "Name to display": "Google Sheet URL"
CAMPAIGNS = {
    "Saudi Warm Leads": "https://docs.google.com/spreadsheets/d/1xzC6ez5Ql7Jg6swMepdzvla_V5dTwaPj3rVSfLVegzs/edit?usp=sharing",
    "Connecticut Warm Leads": "https://docs.google.com/spreadsheets/d/1cf72xw1-Sfuc5qnl_sy1KdDEAGJjUw6W4yXrTBeR990/edit?usp=sharing",
    "New York FI Warm Leads": "https://docs.google.com/spreadsheets/d/1_8NjjRtmad9-XRcPUr6f2frLN_1li6DprEDgh4kfYwY/edit?gid=0#gid=0",
    "New York FO Warm Leads": "https://docs.google.com/spreadsheets/d/1kNpoiR8Yn1O5p83mA2-SitQG-LoMDScu5tKMV1hENnU/edit?gid=0#gid=0",
    "Mid-Atlantic Warm Leads": "https://docs.google.com/spreadsheets/d/1SkylieN8vvPKzSlrrG6w5i29Mz3gl-UCAT0OcztLjD8/edit?gid=0#gid=0",
    "California FI Warm Leads": "https://docs.google.com/spreadsheets/d/1hIbXoJNX_Vpc5Kc_xjCEpX0OlOvZ7gYpeTnhCzP51OY/edit?gid=0#gid=0",
    "California FO Warm Leads": "https://docs.google.com/spreadsheets/d/1ylWS5PLfl4QMSR-3U25lhxx_BTr4aRBaac5__CXPSUg/edit?gid=0#gid=0",
    "California HNWI Warm Leads": "https://docs.google.com/spreadsheets/d/1_iIWr60GZFsOStA9mKVyAv3vOTtomyyHYPBydwyykXM/edit?gid=0#gid=0",
    "Texas FI Warm Leads": "https://docs.google.com/spreadsheets/d/1yu6N8urMLhuNA53GiBWgOjvz4hBYjmzbE4l-d5f-XM8/edit?gid=0#gid=0",
    "Texas FO Warm Leads": "https://docs.google.com/spreadsheets/d/1z-ACJWGolIYh_msKdv_hPqlJKOKdLOxoeBT32Gn-HCM/edit?gid=0#gid=0",
    "Texas HNWI Warm Leads": "https://docs.google.com/spreadsheets/d/1EP44JZSWVVSzBxofKFEypTrtGEiCZQSvi_ITUps9dEA/edit?gid=0#gid=0",
    "Florida FI Warm Leads": "https://docs.google.com/spreadsheets/d/1LS_VJ_lgi8F2gXAOF0p4EboxbjsFlaZbrNnLAHMkiPQ/edit?gid=0#gid=0",
    "Florida FO Warm Leads": "https://docs.google.com/spreadsheets/d/1YD2QXm4AEWlvg-qBWW_4ZSlkK8Rbf5K4YCRUS1gPBUc/edit?gid=0#gid=0",
    "Florida HNWI Warm Leads": "https://docs.google.com/spreadsheets/d/1F3w5i25je2dGq8A7gfb04Lg1Bdcg0jG6kTrWhs6H4dI/edit?gid=0#gid=0",
}

# MVP Ventures Palette
PRIMARY_ORANGE = "#ED7824"
DARK_GRAY = "#6D6E71"
LIGHT_GRAY = "#F1F3F4"
BLACK_ORANGE = "#150B00"

st.set_page_config(page_title="LeadBox | Dashboard", page_icon="", layout="wide", initial_sidebar_state="collapsed")

# --- CSS STYLING ---
st.markdown(f"""
    <style>
    /* Hide the default Streamlit menu and footer for a cleaner look */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    .stApp {{ background-color: DARK_GRAY; }}
    
    /* Custom Button Styling */
    div.stButton > button {{
        background-color: {PRIMARY_ORANGE}; color: white; border: none; font-weight: bold;
    }}
    div.stButton > button:hover {{ background-color: {BLACK_ORANGE}; color: white; }}
    
    /* Text Styling */
    h1, h2, h3, h4 {{ color: {BLACK_ORANGE}; font-family: 'Helvetica', sans-serif; }}
    div[data-testid="stMetricValue"] {{ color: {PRIMARY_ORANGE}; }}
    
    /* Remove padding around top to make it look like a web app */
    .block-container {{ padding-top: 2rem; }}
    </style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    """Returns True if the user had the correct password."""
    if st.session_state.authenticated:
        return True

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔒 LeadBox Login")
        password = st.text_input("Enter Password", type="password")
        
        if st.button("Login"):
            if password == "MVP":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect Password. Please try again.")
    return False

if not check_password():
    st.stop()  # Stop execution if not logged in

# --- GOOGLE SHEETS CONNECTION ---
def get_google_sheet_data(sheet_url):
    """Connects to GSheets and returns the worksheet object and dataframe."""
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    if "ENTER_YOUR" in sheet_url:
        return None, None, "invalid_url"

    try:
        creds = Credentials.from_service_account_file("service_account.json", scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(sheet_url)
        worksheet = sheet.get_worksheet(0) # First tab
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        return worksheet, df, None
    except FileNotFoundError:
        return None, None, "missing_file"
    except Exception as e:
        return None, None, str(e)

# --- HEADER & SELECTION ---
col_header, col_select, col_refresh = st.columns([3, 2, 1])

with col_header:
    st.title("LeadBox | Project of MVP")

with col_select:
    # THE DROPDOWN MENU
    selected_campaign_name = st.selectbox(
        "Select Active Campaign:", 
        list(CAMPAIGNS.keys()), 
        index=None,
        placeholder="Choose a campaign..."
    )



st.markdown("---")

# --- MAIN APP LOGIC ---

if selected_campaign_name is None:
    st.info("Please select a campaign from the dropdown menu to view the dashboard.")
    st.stop() 

selected_url = CAMPAIGNS[selected_campaign_name]

# 1. Load Data
worksheet, df, error = get_google_sheet_data(selected_url)

if error == "missing_file":
    st.warning("⚠️ **Setup Required:** `service_account.json` not found.")
    st.info("Displaying Mock Data. Add your key to connect real data.")
    # Mock Data
    df = pd.DataFrame({
        "First Name": ["Alex", "Jordan", "Casey"], "Last Name": ["Smith", "Doe", "Jones"], 
        "Company": ["TechFlow", "Innovate", "SoftSys"], 
        "Website": ["www.techflow.com", "www.innovate.io", "www.softsys.net"],
        "Direct Phone Number": ["555-0101", "555-0102", "555-0103"],
        "Mobile Phone Number": ["555-9991", "555-9992", "555-9993"],
        "Email": ["alex@example.com", "jordan@example.com", "casey@example.com"],
        "Status": ["New", "New", "Attempted"],
        "Call Outcome": ["Not Called", "Not Called", "Left Voicemail"], "Notes": ["", "", "Call back later"],
        "Sales Rep": ["", "", ""],
        "Date Called": ["", "", ""]
    })
    worksheet = None 

elif error == "invalid_url":
    st.info("Select a valid campaign to load data. (You need to add the URL in the code).")
    st.stop()

elif error:
    st.error(f"Error connecting to Google Sheets: {error}")
    st.stop()

# 2. Data Prep (Ensure columns exist)
# UPDATED COLUMN LIST
required_cols = ["First Name", "Last Name", "Company", "Website", "Email", "Direct Phone Number", "Mobile Phone Number", "Call Outcome", "Notes", "Sales Rep", "Date Called"]
for col in required_cols:
    if col not in df.columns:
        df[col] = "" if col in ["Notes", "Call Outcome", "Sales Rep", "Date Called", "Website", "Mobile Phone Number"] else "Unknown"

# 3. SINGLE VIEW LAYOUT
col_sheet, col_action = st.columns([3, 1])

with col_sheet:
    st.subheader(f"{selected_campaign_name}")
    st.dataframe(df, use_container_width=True, height=600)

with col_action:
    st.subheader("📝 Log Interaction")
    
    # Sort leads alphabetically
    df_sorted = df.sort_values(by="First Name", ascending=True)
    
    # Select Lead
    lead_options = df_sorted.apply(lambda x: f"{x['First Name']} {x['Last Name']} ({x['Company']})", axis=1)
    selected_lead_str = st.selectbox("Select Lead to Update:", lead_options)
    
    if selected_lead_str:
        # Find row index
        row_idx = df_sorted[lead_options == selected_lead_str].index[0]
        lead = df.loc[row_idx]
        
        # Display Card
        website_link = lead['Website']
        if website_link and not website_link.startswith('http'):
            website_link = 'https://' + website_link

        st.markdown(f"""
        <div style="background-color:{LIGHT_GRAY}; padding:15px; border-radius:8px; border-left: 5px solid {PRIMARY_ORANGE}; color: black;">
            <h4 style="margin:0; color:{BLACK_ORANGE}">{lead['First Name']} {lead['Last Name']}</h4>
            <p style="margin-bottom:5px;"><b>{lead['Company']}</b></p>
            <p style="margin-bottom:5px; font-size:14px;">🌐 <a href="{website_link}" target="_blank">{lead['Website']}</a></p>
            <p style="margin-bottom:5px;">📧 <a href="mailto:{lead['Email']}">{lead['Email']}</a></p>
            <hr style="margin: 10px 0;">
            <p style="font-size:16px; margin-bottom:5px;">☎️ Direct: <b>{lead['Direct Phone Number']}</b></p>
            <p style="font-size:16px; margin-bottom:5px;">📱 Mobile: <b>{lead['Mobile Phone Number']}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        
        # Form
        with st.form("log_call"):
            new_outcome = st.selectbox("Call Outcome", 
                ["Not Called", "No Answer", "Left Voicemail", "Not Interested", "Interested", "Meeting Booked"],
                index=["Not Called", "No Answer", "Left Voicemail", "Not Interested", "Interested", "Meeting Booked"].index(lead["Call Outcome"]) if lead["Call Outcome"] in ["Not Called", "No Answer", "Left Voicemail", "Not Interested", "Interested", "Meeting Booked"] else 0
            )
            
            new_sales_rep = st.text_input("Sales Rep Name", value=str(lead.get("Sales Rep", "")))
            new_notes = st.text_area("Notes", value=str(lead["Notes"]))
            
            submitted = st.form_submit_button("Save Result")
            
            if submitted:
                if worksheet:
                    try:
                        # Determine which phone number to use as the Unique ID for searching the row
                        # We try Direct first, then Mobile
                        search_key = str(lead['Direct Phone Number'])
                        if not search_key or search_key == "Unknown":
                             search_key = str(lead['Mobile Phone Number'])

                        if not search_key or search_key == "Unknown":
                            st.error("Cannot save: Both Direct and Mobile phone numbers are missing for this lead. Cannot identify row.")
                        else:
                            # Search for the phone number
                            cell = worksheet.find(search_key)
                            
                            if cell:
                                headers = worksheet.row_values(1)
                                current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

                                try:
                                    outcome_col = headers.index("Call Outcome") + 1
                                    notes_col = headers.index("Notes") + 1
                                    rep_col = headers.index("Sales Rep") + 1
                                    date_col = headers.index("Date Called") + 1
                                    
                                    worksheet.update_cell(cell.row, outcome_col, new_outcome)
                                    worksheet.update_cell(cell.row, notes_col, new_notes)
                                    worksheet.update_cell(cell.row, rep_col, new_sales_rep)
                                    worksheet.update_cell(cell.row, date_col, current_time)
                                    
                                    st.success(f"Updated {lead['First Name']} in {selected_campaign_name}!")
                                    st.rerun()
                                except ValueError as e:
                                    st.error(f"Column missing in Sheet: {e}. Check headers.")
                            else:
                                st.error(f"Could not find row with phone number: {search_key}")
                    except Exception as e:
                        st.error(f"Update failed: {e}")
                else:
                    st.info("Updates are not saved in Demo Mode.")

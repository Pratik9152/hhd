import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Gratuity Tracker", layout="wide")

# --- CSS Animated Background ---
st.markdown("""
    <style>
    body {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: white;
    }
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .block-container {
        padding: 2rem;
    }
    .stButton>button, .stDownloadButton>button {
        background-color: #6a11cb;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
    }
    .stTextInput>div>div>input {
        background-color: #f0f0f0;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN SYSTEM ---
users = {"admin": "password123", "hr": "hr2024"}
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔐 Login to Gratuity Tracker")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")
    if login_btn:
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")
    st.stop()

# ✅ FIX: Prevent crashing immediately after login
if st.session_state["logged_in"] and "just_logged_in" not in st.session_state:
    st.session_state["just_logged_in"] = True
    st.experimental_rerun()

# --- DASHBOARD START ---
st.title("🎉 Gratuity Tracker Dashboard")
st.markdown("Upload your Excel file. The app saves records by Emp ID and shows filters and charts.")

save_path = "saved_data.xlsx"

def calculate_years(joining_date, exit_date=None):
    today = datetime.today()
    end_date = exit_date if pd.notna(exit_date) else today
    return round((end_date - joining_date).days / 365, 2)

def update_data(existing, new_data):
    new_data["Emp ID"] = new_data["Emp ID"].astype(str)
    existing["Emp ID"] = existing["Emp ID"].astype(str)
    existing = existing.set_index("Emp ID")
    new_data = new_data.set_index("Emp ID")
    existing.update(new_data)
    merged = pd.concat([existing, new_data[~new_data.index.isin(existing.index)]])
    merged.reset_index(inplace=True)
    return merged

uploaded_file = st.file_uploader("📤 Upload Employee Excel", type=["xlsx"])

if uploaded_file:
    new_df = pd.read_excel(uploaded_file, parse_dates=["Joining Date", "Exit Date"])
    new_df["Completed Years"] = new_df.apply(lambda row: calculate_years(row["Joining Date"], row["Exit Date"]), axis=1)
    new_df["Status"] = new_df["Exit Date"].apply(lambda x: "Exited" if pd.notna(x) and x < datetime.today() else "Working")
    new_df["Gratuity Eligible"] = new_df["Completed Years"] >= 5

    if os.path.exists(save_path):
        old_df = pd.read_excel(save_path, parse_dates=["Joining Date", "Exit Date"])
        df = update_data(old_df, new_df)
    else:
        df = new_df

    df.to_excel(save_path, index=False)
    st.success("✅ Data uploaded and saved.")
elif os.path.exists(save_path):
    df = pd.read_excel(save_path, parse_dates=["Joining Date", "Exit Date"])
else:
    st.warning("⚠️ No data available. Please upload an Excel file.")
    st.stop()

# --- FILTER SIDEBAR ---
st.sidebar.header("🔍 Filter")
dept_options = st.sidebar.multiselect("Select Department", options=df["Department"].unique(), default=df["Department"].unique())
eligible_only = st.sidebar.checkbox("Show Gratuity Eligible Only", value=True)
start_date = st.sidebar.date_input("Joining Date From", value=datetime(2015, 1, 1))
end_date = st.sidebar.date_input("Joining Date To", value=datetime.today())

filtered_df = df[
    (df["Department"].isin(dept_options)) &
    (df["Joining Date"] >= pd.to_datetime(start_date)) &
    (df["Joining Date"] <= pd.to_datetime(end_date))
]

if eligible_only:
    filtered_df = filtered_df[(filtered_df["Gratuity Eligible"]) | (filtered_df["Status"] == "Working")]

# --- TABLE DISPLAY ---
st.subheader("📋 Filtered Employee Table")
st.dataframe(filtered_df)

# --- CHARTS ---
st.subheader("📈 Gratuity Eligibility Distribution")
if not filtered_df.empty:
    pie_data = filtered_df["Gratuity Eligible"].value_counts().rename(index={True: "Eligible", False: "Not Eligible"})
    fig_pie = px.pie(names=pie_data.index, values=pie_data.values, title="Gratuity Eligibility")
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("🏢 Employees by Department")
    dept_chart = filtered_df["Department"].value_counts().reset_index()
    dept_chart.columns = ["Department", "Count"]
    fig_bar = px.bar(dept_chart, x="Department", y="Count", color="Department", title="Employees by Department")
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No data to show. Adjust your filters.")

# --- DOWNLOAD BUTTON ---
st.download_button("⬇️ Download Filtered Report", data=filtered_df.to_csv(index=False), file_name="filtered_gratuity_report.csv", mime="text/csv")

   

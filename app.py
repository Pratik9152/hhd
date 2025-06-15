import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import requests
from streamlit_lottie import st_lottie

# --- Page Config ---
st.set_page_config(page_title="Gratuity Tracker", layout="wide")

# --- Animated Background ---
st.markdown("""
    <style>
    body {
        background: linear-gradient(270deg, #ff9a9e, #fad0c4, #fad0c4, #ffdde1);
        background-size: 800% 800%;
        animation: gradient 30s ease infinite;
    }
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stApp { font-family: 'Segoe UI', sans-serif; }
    .stButton>button, .stDownloadButton>button {
        background-color: #6a11cb;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
    </style>
""", unsafe_allow_html=True)

# --- Lottie Animation Loader ---
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_employee = load_lottie_url("https://assets7.lottiefiles.com/packages/lf20_puciaact.json")

# --- Login ---
users = {"admin": "password123", "hr": "hr2024"}
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔐 Login to Gratuity Tracker")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
    if login_btn:
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("❌ Invalid username or password")
    st.stop()
from streamlit_lottie import st_lottie
import requests

def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Try this animated education Lottie
lottie_employee = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_w51pcehl.json")

if lottie_employee:
    st_lottie(lottie_employee, height=250, key="emp_anim")
else:
    st.warning("⚠️ Animation not loaded. Check internet or URL.")

# --- Header + Lottie ---
st.title("🎉 Gratuity Tracker Dashboard")
st_lottie(lottie_employee, height=200, key="emp_anim")

save_path = "saved_data.xlsx"

def calculate_years(joining, exit=None):
    end = exit if pd.notna(exit) else datetime.today()
    return round((end - joining).days / 365, 2)

def update_data(existing, new):
    new["Emp ID"] = new["Emp ID"].astype(str)
    existing["Emp ID"] = existing["Emp ID"].astype(str)
    existing = existing.set_index("Emp ID")
    new = new.set_index("Emp ID")
    existing.update(new)
    merged = pd.concat([existing, new[~new.index.isin(existing.index)]])
    merged.reset_index(inplace=True)
    return merged

# --- File Upload ---
uploaded = st.file_uploader("📤 Upload Employee Excel", type=["xlsx"])
if uploaded:
    new_df = pd.read_excel(uploaded, parse_dates=["Joining Date", "Exit Date"])
    new_df["Completed Years"] = new_df.apply(lambda row: calculate_years(row["Joining Date"], row["Exit Date"]), axis=1)
    new_df["Status"] = new_df["Exit Date"].apply(lambda x: "Exited" if pd.notna(x) and x < datetime.today() else "Working")
    new_df["Gratuity Eligible"] = new_df["Completed Years"] >= 5
    if os.path.exists(save_path):
        old_df = pd.read_excel(save_path, parse_dates=["Joining Date", "Exit Date"])
        df = update_data(old_df, new_df)
    else:
        df = new_df
    df.to_excel(save_path, index=False)
    st.success("✅ Data saved.")
elif os.path.exists(save_path):
    df = pd.read_excel(save_path, parse_dates=["Joining Date", "Exit Date"])
else:
    st.warning("⚠️ Please upload an Excel file.")
    st.stop()

# --- Summary Cards ---
st.markdown("### 📊 Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Employees", len(df))
col2.metric("Gratuity Eligible", len(df[df["Gratuity Eligible"]]))
col3.metric("Currently Working", len(df[df["Status"] == "Working"]))

# --- Filters ---
st.sidebar.header("🔍 Filter")
depts = st.sidebar.multiselect("Department", df["Department"].unique(), default=df["Department"].unique())
eligible_only = st.sidebar.checkbox("Only Gratuity Eligible", True)
start = st.sidebar.date_input("Joining From", datetime(2015, 1, 1))
end = st.sidebar.date_input("Joining To", datetime.today())

filtered = df[
    (df["Department"].isin(depts)) &
    (df["Joining Date"] >= pd.to_datetime(start)) &
    (df["Joining Date"] <= pd.to_datetime(end))
]
if eligible_only:
    filtered = filtered[(filtered["Gratuity Eligible"]) | (filtered["Status"] == "Working")]

# --- Table ---
st.subheader("📋 Filtered Employee Table")
st.dataframe(filtered)

# --- Charts ---
if not filtered.empty:
    st.subheader("📈 Gratuity Eligibility")
    pie_data = filtered["Gratuity Eligible"].value_counts().rename(index={True: "Eligible", False: "Not Eligible"})
    pie_fig = px.pie(names=pie_data.index, values=pie_data.values, title="Eligibility Status")
    st.plotly_chart(pie_fig, use_container_width=True)

    st.subheader("🏢 Department Distribution")
    dept_data = filtered["Department"].value_counts().reset_index()
    dept_data.columns = ["Department", "Count"]
    dept_fig = px.bar(dept_data, x="Department", y="Count", color="Department", title="Employees by Department")
    st.plotly_chart(dept_fig, use_container_width=True)
else:
    st.info("Try adjusting filters to show data.")

# --- Download Button ---
st.download_button("⬇️ Download Filtered Report", data=filtered.to_csv(index=False), file_name="filtered_gratuity_report.csv", mime="text/csv")

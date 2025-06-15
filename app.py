# Gratuity Tracker with Secure Email and Animated Dashboard

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import requests
import smtplib
from email.message import EmailMessage
from streamlit_lottie import st_lottie
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page setup
st.set_page_config(page_title="Gratuity Tracker", layout="wide")

# Background Styling
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url('https://images.unsplash.com/photo-1557683304-673a23048d34?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }
    [data-testid="stHeader"] {
        background-color: rgba(255, 255, 255, 0);
    }
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.7);
    }
    .main {
        background-color: rgba(255, 255, 255, 0.3);
        padding: 1rem;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# Load Lottie animation
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

lottie_employee = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_w51pcehl.json")

# Simple Login System
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

# Title + animation
st.title("🎉 Gratuity Tracker Dashboard")
if lottie_employee:
    st_lottie(lottie_employee, height=250, key="emp_lottie")
else:
    st.warning("⚠️ Animation failed to load.")

save_path = "saved_data.xlsx"

# Calculate years function
def calculate_years(joining, exit=None):
    end = exit if pd.notna(exit) else datetime.today()
    return round((end - joining).days / 365, 2)

# Merge/Update data
def update_data(existing, new):
    new["Emp ID"] = new["Emp ID"].astype(str)
    existing["Emp ID"] = existing["Emp ID"].astype(str)
    existing = existing.set_index("Emp ID")
    new = new.set_index("Emp ID")
    existing.update(new)
    merged = pd.concat([existing, new[~new.index.isin(existing.index)]])
    merged.reset_index(inplace=True)
    return merged

# Send Email Function (secure)
def send_email_easy(to_email, subject, body, attachment_path=None):
    sender_email = os.getenv("GMAIL_USER")
    app_password = os.getenv("GMAIL_PASS")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email
    msg.set_content(body)

    if attachment_path:
        with open(attachment_path, "rb") as f:
            file_data = f.read()
            file_name = attachment_path.split("/")[-1]
            msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        return f"❌ Error: {e}"

# Upload Excel
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

# Overview Metrics
st.markdown("### 📊 Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Employees", len(df))
col2.metric("Gratuity Eligible", len(df[df["Gratuity Eligible"]]))
col3.metric("Currently Working", len(df[df["Status"] == "Working"]))

# Sidebar Filters
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

# Display Table
st.subheader("📋 Filtered Employee Table")
st.dataframe(filtered)

# Animated Progress Bars
st.subheader("📊 Employee Gratuity Progress")
for _, row in filtered.iterrows():
    percent = min((row["Completed Years"] / 5) * 100, 100)
    st.markdown(f"**{row['Emp ID']} - {row['Name']}**")
    st.progress(percent / 100, text=f"{row['Completed Years']} years completed ({percent:.1f}%)")

# Charts
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

# 📥 Download filtered report if available
if not filtered.empty:
    st.download_button(
        "⬇️ Download Filtered Report",
        data=filtered.to_csv(index=False),
        file_name="filtered_gratuity_report.csv",
        mime="text/csv"
    )

# 📧 Always show email section
st.subheader("📧 Send Gratuity Report via Email")
email = st.text_input("Enter recipient email address")

if st.button("Send Email Report"):
    if not filtered.empty:
        filtered.to_csv("filtered_report.csv", index=False)
        result = send_email_easy(
            to_email=email,
            subject="Gratuity Tracker Report",
            body="Attached is the Gratuity Eligibility Report.",
            attachment_path="filtered_report.csv"
        )
        if result == True:
            st.success("✅ Email sent successfully!")
        else:
            st.error(result)
    else:
        st.warning("⚠️ No data to send. Please upload or filter data.")

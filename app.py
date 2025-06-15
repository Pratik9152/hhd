# Gratuity Tracker App with Downloadable Excel Format and Email Sending

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(page_title="Gratuity Tracker", layout="wide")

# Function: Send Email
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

# Function: Create sample Excel format
def generate_sample_excel():
    sample_data = {
        "Emp ID": ["E001", "E002"],
        "Name": ["John Doe", "Jane Smith"],
        "Department": ["HR", "Finance"],
        "Joining Date": ["2015-06-01", "2018-09-15"],
        "Exit Date": ["", ""]
    }
    df_sample = pd.DataFrame(sample_data)
    return df_sample

# Title
st.title("🧮 Gratuity Tracker System")

# Download sample Excel format
st.markdown("### 📥 Download Excel Format")
df_sample = generate_sample_excel()
st.download_button(
    label="Download Excel Format",
    data=df_sample.to_csv(index=False),
    file_name="gratuity_format.csv",
    mime="text/csv"
)

# Upload user file
uploaded = st.file_uploader("📤 Upload Filled Employee Excel File", type=["xlsx", "csv"])
if uploaded:
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded, parse_dates=["Joining Date", "Exit Date"])

    # Convert date columns
    df["Joining Date"] = pd.to_datetime(df["Joining Date"], errors='coerce')
    df["Exit Date"] = pd.to_datetime(df["Exit Date"], errors='coerce')

    # Calculate completed years
    def calculate_years(joining, exit=None):
        end = exit if pd.notna(exit) else datetime.today()
        return round((end - joining).days / 365, 2)

    df["Completed Years"] = df.apply(lambda row: calculate_years(row["Joining Date"], row["Exit Date"]), axis=1)
    df["Status"] = df["Exit Date"].apply(lambda x: "Exited" if pd.notna(x) and x < datetime.today() else "Working")
    df["Gratuity Eligible"] = df["Completed Years"] >= 5

    # Filters
    st.markdown("### 🔍 Filter Employees")
    departments = st.multiselect("Filter by Department", df["Department"].unique(), default=df["Department"].unique())
    eligible_only = st.checkbox("Show only Gratuity Eligible", value=True)

    filtered_df = df[df["Department"].isin(departments)]
    if eligible_only:
        filtered_df = filtered_df[filtered_df["Gratuity Eligible"] == True]

    # Show table
    st.markdown("### 📋 Filtered Data")
    st.dataframe(filtered_df)

    # Download filtered report
    st.download_button(
        "⬇️ Download Filtered Report",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_gratuity_report.csv",
        mime="text/csv"
    )

    # Email send section
    st.markdown("### 📧 Send Report via Email")
    recipient = st.text_input("Enter recipient email")
    if st.button("Send Email Report"):
        filtered_df.to_csv("filtered_report.csv", index=False)
        result = send_email_easy(
            to_email=recipient,
            subject="Gratuity Report",
            body="Attached is the filtered gratuity report as per your request.",
            attachment_path="filtered_report.csv"
        )
        if result == True:
            st.success("✅ Email sent successfully!")
        else:
            st.error(result)
else:
    st.warning("⚠️ Please upload a filled Excel or CSV file to continue.")

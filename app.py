import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

# Load environment variables from .env file
load_dotenv()

# 🌈 Page setup and animated gradient background
st.set_page_config(page_title="🌌 Gratuity Tracker Dashboard", layout="wide")
st.markdown("""
    <style>
    body {
        background: linear-gradient(-45deg, #e3f2fd, #ffebee, #f3e5f5, #e8f5e9);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    [data-testid="stSidebar"] {
        background-color: #ffffffaa;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#4A148C;'>✨ Gratuity Tracker with Email & Analytics</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Upload ➤ Track ➤ Visualize ➤ Send Report</p>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar filter
st.sidebar.title("🔍 Filters & Settings")
min_years = st.sidebar.slider("Minimum Years for Eligibility", 0, 40, 5)

# 📥 Sample Excel Format
def sample_format():
    return pd.DataFrame({
        "Emp ID": ["E101", "E102"],
        "Name": ["Arjun", "Meera"],
        "Department": ["Finance", "HR"],
        "Joining Date": ["2014-06-01", "2016-09-15"],
        "Exit Date": ["", ""]
    })

st.subheader("📥 Download Excel Format")
sample_df = sample_format()
st.download_button("📂 Download Template", data=sample_df.to_csv(index=False), file_name="gratuity_template.csv", mime="text/csv")

# 📤 Upload Excel/CSV
st.subheader("📤 Upload Employee Data")
uploaded_file = st.file_uploader("Upload Excel or CSV file", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
    df["Joining Date"] = pd.to_datetime(df["Joining Date"], errors="coerce")
    df["Exit Date"] = pd.to_datetime(df["Exit Date"], errors="coerce")

    def calc_years(join, exit=None):
        end = exit if pd.notna(exit) else datetime.today()
        return round((end - join).days / 365, 2)

    df["Completed Years"] = df.apply(lambda row: calc_years(row["Joining Date"], row["Exit Date"]), axis=1)
    df["Status"] = df["Exit Date"].apply(lambda x: "Exited" if pd.notna(x) else "Working")
    df["Gratuity Eligible"] = df["Completed Years"] >= min_years

    # 📊 Summary
    st.subheader("📊 Summary Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Total Employees", len(df))
    col2.metric("🏆 Eligible", df["Gratuity Eligible"].sum())
    col3.metric("💼 Working", (df["Status"] == "Working").sum())

    # 📋 Show Data
    st.subheader("📋 Data Preview")
    st.dataframe(df)

    # 📈 Charts
    st.subheader("📈 Charts")
    pie_chart = px.pie(df, names="Gratuity Eligible", title="Gratuity Eligibility")
    st.plotly_chart(pie_chart, use_container_width=True)

    bar_chart = px.bar(df["Department"].value_counts().reset_index(), x="index", y="Department",
                       labels={"index": "Department", "Department": "Employees"},
                       title="Department-wise Count")
    st.plotly_chart(bar_chart, use_container_width=True)

    # 📧 Email Section
    st.subheader("📧 Send Report via Email")
    recipient = st.text_input("Enter recipient's email address")
    if st.button("Send Report"):
        df.to_csv("filtered_report.csv", index=False)
        msg = EmailMessage()
        msg["Subject"] = "📩 Gratuity Tracker Report"
        msg["From"] = os.getenv("GMAIL_USER")
        msg["To"] = recipient
        msg.set_content("Please find the attached gratuity report.")

        with open("filtered_report.csv", "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename="gratuity_report.csv")

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_PASS"))
                smtp.send_message(msg)
            st.success("✅ Report sent successfully!")
        except Exception as e:
            st.error(f"❌ Email failed to send: {e}")
else:
    st.warning("📤 Please upload a file to continue.")

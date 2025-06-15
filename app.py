import streamlit as st
import pandas as pd
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Gratuity Tracker", layout="wide")
st.title("🧮 Gratuity Tracker System")

# Function to generate sample format
def get_sample():
    df = pd.DataFrame({
        "Emp ID": ["E001", "E002"],
        "Name": ["Alice", "Bob"],
        "Department": ["HR", "Finance"],
        "Joining Date": ["2016-01-10", "2018-05-23"],
        "Exit Date": ["", ""]
    })
    return df

# 📥 Download Excel Format
st.markdown("### 📥 Download Excel Format")
sample_df = get_sample()
st.download_button(
    "Download Excel Format",
    data=sample_df.to_csv(index=False),
    file_name="gratuity_format.csv",
    mime="text/csv"
)

# 📤 Upload Filled Excel File
uploaded = st.file_uploader("Upload Filled Excel File", type=["csv", "xlsx"])
if uploaded:
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    df["Joining Date"] = pd.to_datetime(df["Joining Date"], errors="coerce")
    df["Exit Date"] = pd.to_datetime(df["Exit Date"], errors="coerce")

    def completed_years(j, e=None):
        end = e if pd.notna(e) else datetime.today()
        return round((end - j).days / 365, 2)

    df["Completed Years"] = df.apply(lambda x: completed_years(x["Joining Date"], x["Exit Date"]), axis=1)
    df["Gratuity Eligible"] = df["Completed Years"] >= 5

    st.markdown("### 📋 Filtered Employees")
    st.dataframe(df)

    # 📧 Send Email
    st.markdown("### 📧 Send Report via Email")
    to_email = st.text_input("Enter email to send report")
    if st.button("Send Email"):
        df.to_csv("report.csv", index=False)

        msg = EmailMessage()
        msg["Subject"] = "Gratuity Report"
        msg["From"] = os.getenv("GMAIL_USER")
        msg["To"] = to_email
        msg.set_content("Please find attached the filtered gratuity report.")
        with open("report.csv", "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="csv", filename="report.csv")

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_PASS"))
                smtp.send_message(msg)
            st.success("✅ Email sent!")
        except Exception as e:
            st.error(f"❌ Failed: {e}")
else:
    st.info("Please upload the file to continue.")

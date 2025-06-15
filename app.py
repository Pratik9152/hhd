import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# --- Dummy login system ---
users = {"admin": "password123", "hr": "hr2024"}

def login():
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
        else:
            st.sidebar.error("Invalid credentials")
    return st.session_state.get("logged_in", False)

if not login():
    st.stop()

# --- App Interface ---
st.set_page_config(page_title="Gratuity Tracker", layout="wide")
st.title("🏢 Employee Gratuity Tracker (5+ Years Eligibility)")
st.markdown("Upload your latest employee Excel file below. The app auto-checks gratuity eligibility and generates insights.")

uploaded_file = st.file_uploader("📤 Upload Employee Excel File", type=["xlsx"])

def calculate_years(joining_date, exit_date=None):
    today = datetime.today()
    end_date = exit_date if pd.notna(exit_date) else today
    return round((end_date - joining_date).days / 365, 2)

if uploaded_file:
    df = pd.read_excel(uploaded_file, parse_dates=["Joining Date", "Exit Date"])
    df["Completed Years"] = df.apply(lambda row: calculate_years(row["Joining Date"], row["Exit Date"]), axis=1)
    df["Status"] = df["Exit Date"].apply(lambda x: "Exited" if pd.notna(x) and x < datetime.today() else "Working")
    df["Gratuity Eligible"] = df["Completed Years"] >= 5

    st.subheader("📊 Live Dashboard")
    st.dataframe(df.style.applymap(lambda x: "background-color: #d1e7dd" if x is True else "", subset=["Gratuity Eligible"]))

    eligible_df = df[df["Gratuity Eligible"] & (df["Status"] == "Working")]
    
    # --- Animated Chart ---
    st.subheader("📈 Gratuity Eligibility Overview")
    chart_data = df["Gratuity Eligible"].value_counts().rename(index={True: "Eligible", False: "Not Eligible"})
    fig = px.pie(names=chart_data.index, values=chart_data.values, title="Eligibility Distribution", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    # --- Download Button ---
    st.download_button("⬇️ Download Eligible Report", data=eligible_df.to_csv(index=False), file_name="eligible_gratuity_employees.csv", mime="text/csv")

    # --- Simulated Email Sender ---
    st.subheader("📧 Send Report via Email")
    with st.form("email_form"):
        email_to = st.text_input("Recipient Email")
        email_body = st.text_area("Email Message", value="Hi, please find attached the gratuity eligibility report.")
        submitted = st.form_submit_button("Send Email")
        if submitted:
            if email_to:
                st.success(f"✅ Email sent successfully to {email_to} (simulated).")
            else:
                st.error("❌ Please enter a valid email address.")

else:
    st.warning("Please upload a valid Excel file. Sample format below.")

    sample_df = pd.DataFrame({
        "Emp ID": [1001, 1002],
        "Name": ["Rahul Shah", "Priya Mehta"],
        "Department": ["HR", "Finance"],
        "Joining Date": ["2018-01-10", "2016-06-22"],
        "Exit Date": ["", "2023-12-31"]
    })
    st.dataframe(sample_df)

    sample_file = io.BytesIO()
    sample_df.to_excel(sample_file, index=False)
    st.download_button("📥 Download Sample Excel Format", data=sample_file.getvalue(), file_name="sample_employee_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
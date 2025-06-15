import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# ✅ SET PAGE CONFIG FIRST
st.set_page_config(page_title="Gratuity Tracker", layout="wide")

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
st.title("🏢 Employee Gratuity Tracker (5+ Years Eligibility)")
st.markdown("Upload or view the latest employee Excel file. The app auto-checks gratuity eligibility and generates live insights.")

uploaded_file = st.file_uploader("📤 Upload Employee Excel File", type=["xlsx"])

def calculate_years(joining_date, exit_date=None):
    today = datetime.today()
    end_date = exit_date if pd.notna(exit_date) else today
    return round((end_date - joining_date).days / 365, 2)

# --- File Save Path ---
save_path = "saved_data.xlsx"

# If new file uploaded, overwrite saved_data.xlsx
if uploaded_file:
    df = pd.read_excel(uploaded_file, parse_dates=["Joining Date", "Exit Date"])
    df["Completed Years"] = df.apply(lambda row: calculate_years(row["Joining Date"], row["Exit Date"]), axis=1)
    df["Status"] = df["Exit Date"].apply(lambda x: "Exited" if pd.notna(x) and x < datetime.today() else "Working")
    df["Gratuity Eligible"] = df["Completed Years"] >= 5
    df.to_excel(save_path, index=False)  # Save for future users
    st.success("✅ Data uploaded and saved!")
elif os.path.exists(save_path):
    df = pd.read_excel(save_path, parse_dates=["Joining Date", "Exit Date"])
    df["Completed Years"] = df.apply(lambda row: calculate_years(row["Joining Date"], row["Exit Date"]), axis=1)
    df["Status"] = df["Exit Date"].apply(lambda x: "Exited" if pd.notna(x) and x < datetime.today() else "Working")
    df["Gratuity Eligible"] = df["Completed Years"] >= 5
    st.info("Loaded previously uploaded employee data.")
else:
    st.warning("No uploaded file yet. Please upload Excel file.")
    st.stop()

# --- Main Dashboard Display ---
st.subheader("📋 Employee Gratuity Table")
st.dataframe(df.style.applymap(lambda x: "background-color: #d1e7dd" if x is True else "", subset=["Gratuity Eligible"]))

eligible_df = df[df["Gratuity Eligible"] & (df["Status"] == "Working")]

# --- Animated Pie Chart ---
st.subheader("📈 Gratuity Eligibility Overview")
chart_data = df["Gratuity Eligible"].value_counts().rename(index={True: "Eligible", False: "Not Eligible"})
fig_pie = px.pie(names=chart_data.index, values=chart_data.values, title="Eligibility Distribution", hole=0.4)
st.plotly_chart(fig_pie, use_container_width=True)

# --- Bar Chart by Department ---
st.subheader("🏬 Eligible Employees by Department")
dept_data = eligible_df["Department"].value_counts().reset_index()
dept_data.columns = ["Department", "Eligible Count"]
fig_bar = px.bar(dept_data, x="Department", y="Eligible Count", color="Department", title="Eligible Employees by Department")
st.plotly_chart(fig_bar, use_container_width=True)

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

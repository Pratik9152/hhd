import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="Gratuity Tracker", layout="wide")

# --- Login System ---
users = {"admin": "password123", "hr": "hr2024"}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown("""
        <style>
        body {
            background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
        }
        .login-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 80vh;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.title("🔐 Login to Gratuity Tracker")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")
    st.markdown("</div>", unsafe_allow_html=True)

    if login_btn:
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")
    st.stop()

# --- Main Interface ---
st.markdown(
    "<style>body {background: linear-gradient(to right, #e0c3fc, #8ec5fc);}</style>",
    unsafe_allow_html=True
)

st.title("🎉 Gratuity Tracker Dashboard")
st.markdown("Upload your Excel file to update employee data. This app will track and store history automatically.")

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
else:
    if os.path.exists(save_path):
        df = pd.read_excel(save_path, parse_dates=["Joining Date", "Exit Date"])
    else:
        st.warning("Please upload an Excel file.")
        st.stop()

# --- Filtering Section ---
st.sidebar.header("🔍 Filter Data")
dept_options = st.sidebar.multiselect("Select Department", options=df["Department"].unique(), default=df["Department"].unique())
eligible_only = st.sidebar.checkbox("Show only Gratuity Eligible", value=True)
start_date = st.sidebar.date_input("Joining Date From", value=datetime(2015, 1, 1))
end_date = st.sidebar.date_input("Joining Date To", value=datetime.today())

filtered_df = df[
    (df["Department"].isin(dept_options)) &
    (df["Joining Date"] >= pd.to_datetime(start_date)) &
    (df["Joining Date"] <= pd.to_datetime(end_date))
]

if eligible_only:
    filtered_df = filtered_df[(filtered_df["Gratuity Eligible"]) | (filtered_df["Status"] == "Working")]

# --- Table Display ---
st.subheader("📋 Filtered Employee Table")
st.dataframe(filtered_df)

# --- Charts ---
st.subheader("📈 Gratuity Status Distribution")
pie_data = filtered_df["Gratuity Eligible"].value_counts().rename(index={True: "Eligible", False: "Not Eligible"})
fig_pie = px.pie(names=pie_data.index, values=pie_data.values, title="Gratuity Eligibility")
st.plotly_chart(fig_pie, use_container_width=True)

st.subheader("🏢 Employees by Department")
dept_chart = filtered_df["Department"].value_counts().reset_index()
dept_chart.columns = ["Department", "Count"]
fig_bar = px.bar(dept_chart, x="Department", y="Count", color="Department", title="Employees by Department")
st.plotly_chart(fig_bar, use_container_width=True)

# --- Download Button ---
st.download_button("⬇️ Download Filtered Report", data=filtered_df.to_csv(index=False), file_name="filtered_gratuity_report.csv", mime="text/csv")


   

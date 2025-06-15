# Gratuity Tracker App

This is a no-code Gratuity Tracker app built with Streamlit. You can upload Excel files, view employee eligibility, download reports, and share your dashboard with others.

## 📁 Files Included
- `app.py`: Main dashboard app (upload, analysis, download)
- `requirements.txt`: Required Python packages
- `sample_employee_data.xlsx`: Sample Excel file format

## 🚀 How to Run Locally
1. Install Python (if not installed)
2. Open terminal / command prompt
3. Navigate to folder and run:

```
pip install -r requirements.txt
streamlit run app.py
```

## 🌐 How to Deploy on Streamlit Cloud
1. Upload these files to GitHub
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Click "New App" and paste your GitHub repo link
4. Done! Share your dashboard link

---

**Excel Format Required:**

| Emp ID | Name | Department | Joining Date | Exit Date |
|--------|------|------------|--------------|-----------|

- Leave `Exit Date` blank for active employees.
- App auto-calculates eligibility (5+ years of service).
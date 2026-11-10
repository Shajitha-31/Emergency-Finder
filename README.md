# 🚨 Emergency Finder

### Smart Emergency Response, Incident Reporting, and Disaster Management Platform

<p align="center">
  A centralized platform designed to simplify emergency reporting, identify critical incidents, and support faster response coordination.
</p>

---

## 📌 About the Project

Emergency Finder is a web-based emergency response and disaster management platform that connects citizens and administrators through a centralized system.

Citizens can report emergencies by providing incident details, location information, and optional photo evidence. Administrators can monitor reported incidents, identify their priority, manage response teams, and track response progress.

## 🎯 Objectives

- Simplify emergency incident reporting.
- Identify and prioritize critical incidents.
- Capture emergency locations using GPS.
- Help administrators identify nearby suitable response teams.
- Improve emergency monitoring and coordination.

## 🚀 Key Features

- **Citizen Registration & Login:** Secure user access.
- **Emergency Reporting:** Submit incidents with descriptions and categories.
- **GPS Location Tracking:** Capture incident coordinates.
- **Voice-Based Reporting:** Support voice-assisted report entry.
- **Photo Evidence Upload:** Attach incident photographs.
- **Smart Priority Assessment:** Categorize incidents as Critical, High, Medium, or Low.
- **Duplicate Report Detection:** Flag potentially similar reports.
- **Response Team Management:** Register and manage emergency response teams.
- **Nearby Team Recommendation:** Suggest suitable available teams based on location.
- **Incident Status Tracking:** Track Reported, Assigned, In Progress, and Resolved incidents.
- **Admin Dashboard:** Monitor incidents, teams, and emergency locations.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python Flask |
| Database | SQLite |
| Maps | Leaflet |
| Map Data | OpenStreetMap |
| Location | Browser Geolocation API |

## 📂 Project Structure

```text
Emergency_Finder/
│
├── app.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── home.html
│   ├── register.html
│   ├── candidate.html
│   └── dashboard.html
│
└── static/
    ├── style.css
    ├── script.js
    └── uploads/
```

## ⚙️ Installation and Setup

**1. Clone the repository**

```bash
git clone https://github.com/Shajitha-31/Emergency-Finder.git
```

**2. Navigate to the project folder**

```bash
cd Emergency-Finder
```

**3. Create a virtual environment**

```bash
python -m venv venv
```

**4. Activate the environment (Windows)**

```bash
venv\Scripts\activate
```

**5. Install dependencies**

```bash
pip install -r requirements.txt
```

**6. Run the application**

```bash
python app.py
```

**7. Open in your browser**

```text
http://127.0.0.1:5000
```

## 🔄 Application Workflow

1. Citizen registers and logs in.
2. Citizen submits an emergency report.
3. The system records the incident details and available location information.
4. The system calculates an indicative priority.
5. The administrator reviews the incident.
6. A suitable nearby response team can be suggested.
7. The administrator manages the assignment and incident status.
8. The citizen can view the report progress.

## 📸 Application Screenshots

Add screenshots of your actual application here.

**Admin Dashboard**

<!-- Add dashboard screenshot here -->

**Emergency Reporting Page**

<!-- Add reporting page screenshot here -->

**Emergency Location Map**

<!-- Add map screenshot here -->

## 🌟 Future Enhancements

- Real-time emergency notifications.
- SMS and email alerts.
- Multilingual voice reporting.
- AI-based incident classification.
- Live response-team location tracking.
- Integration with verified official emergency services.

## ⚠️ Disclaimer

Emergency Finder is a hackathon prototype. It is not an official emergency service or certified dispatch system. Priority assessments and team recommendations require human verification. Users should contact official emergency services during real emergencies.

## 👩‍💻 Project Information

**Project Name:** Emergency Finder

**Category:** Emergency Response and Disaster Management

**Backend:** Python Flask

**Database:** SQLite

**Project Repository:** [Emergency Finder on GitHub](https://github.com/Shajitha-31/Emergency-Finder)

---

<p align="center">
  <b>Emergency Finder – Making Emergency Reporting Smarter and More Accessible.</b>
</p>

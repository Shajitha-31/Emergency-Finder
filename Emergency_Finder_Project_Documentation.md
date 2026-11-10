# Emergency Finder

**Smart Emergency Response, Incident Reporting, and Disaster Management
Platform**

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Backend-Flask-black)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue)
![Frontend](https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJavaScript-orange)
![Maps](https://img.shields.io/badge/Maps-Leaflet%2FOpenStreetMap-green)

------------------------------------------------------------------------

## 1. Problem Statement

During emergencies and disasters, people may find it difficult to report
incidents quickly and receive appropriate assistance. Reports can arrive
through different channels, location information may be incomplete, and
coordinators may struggle to identify urgent incidents or locate
suitable response teams.

Manual reporting and coordination can cause delays, duplicate effort,
and poor visibility into incident progress. A centralized system is
needed to collect reports, assess their urgency, display their
locations, and support response-team coordination.

**Emergency Finder** is a web-based emergency reporting and response coordination
prototype. It connects citizens and administrators through a common
platform. Citizens can submit incident reports, while administrators can
review incidents, assess priority, manage response teams, and monitor
response progress.

## 2. Proposed Solution

Emergency Finder provides the following workflow:

-   Citizens can register, log in, and submit emergency reports.
-   Reports can include a title, category, description, location, number
    of people affected, optional contact details, and an optional
    photograph.
-   Browser geolocation can capture coordinates when the user grants
    permission.
-   Voice reporting can help enter report text in browsers that support
    speech recognition.
-   A rule-based scoring mechanism assigns an indicative severity level.
-   Multiple incidents can be submitted under the same category; each
    submission is stored as a separate report.
-   Possible duplicate reports can be flagged for administrator review
    without deleting or merging the original submissions.
-   Administrators can register response teams and manage their service
    category, location, contact details, and availability.
-   The system can suggest a nearby suitable available team when the
    necessary coordinates and category information are available.
-   Administrators can monitor incidents through a dashboard, map, and
    status updates.

Emergency Finder is a coordination aid and prototype. It does not replace
official emergency services or dispatch procedures.

## 3. Key Features

  -----------------------------------------------------------------------
  Feature                 Description             Output
  ----------------------- ----------------------- -----------------------
  Citizen registration    Account creation and    Citizen access
  and login               authentication          

  Emergency reporting     Captures incident       Separate incident
                          details and location    record

  GPS location capture    Uses browser            Latitude and longitude
                          geolocation with        
                          permission              

  Voice-assisted          Uses supported browser  Transcribed report text
  reporting               speech recognition      

  Photo evidence upload   Allows an optional      Incident image
                          image attachment        

  Priority assessment     Applies configurable    Critical, High, Medium,
                          rule-based scoring      or Low

  Multiple reports per    Allows repeated use of  Independent incident
  category                a category              records

  Duplicate awareness     Flags similar reports   Duplicate warning
                          for review              

  Response-team           Registers teams and     Team directory
  management              tracks availability     

  Nearby team suggestion  Uses coordinates and    Suggested response team
                          category suitability    

  Incident status         Tracks Reported,        Response progress
  tracking                Assigned, In Progress,  
                          and Resolved            

  Admin dashboard         Summarizes incidents,   Centralized monitoring
                          priorities, teams, and  
                          locations               
  -----------------------------------------------------------------------

## 4. Technology Stack

### Frontend

  -----------------------------------------------------------------------
  Technology                          Role
  ----------------------------------- -----------------------------------
  HTML5                               Page structure and forms

  CSS3                                Responsive styling and user
                                      interface

  JavaScript                          Client-side interaction and browser
                                      APIs

  Leaflet                             Interactive incident map

  OpenStreetMap                       Map tile data

  Browser Geolocation API             Optional location capture

  Browser Speech Recognition API      Voice-assisted text entry where
                                      supported
  -----------------------------------------------------------------------

### Backend and Storage

  Technology           Role
  -------------------- ----------------------------------------------------
  Python               Main programming language
  Flask                Web framework and application routes
  SQLite               Persistent storage for users, incidents, and teams
  Werkzeug utilities   Password hashing and secure file-name handling

### External Services

  -----------------------------------------------------------------------
  Service                             Role
  ----------------------------------- -----------------------------------
  OpenStreetMap Nominatim             Address-to-coordinate lookup, where
                                      configured

  OpenStreetMap tiles                 Map background rendered through
                                      Leaflet
  -----------------------------------------------------------------------

## 5. System Modules

### 5.1 Citizen Module

Provides registration, login, emergency report submission, and
report-status viewing. Citizens can enter incident information, provide
a location, and optionally attach a photograph.

### 5.2 Incident Reporting Module

Validates and stores each submitted incident. The category is not a
unique identifier: multiple reports can use the same category, and every
submission receives its own record.

### 5.3 Priority Assessment Module

Uses configured rules to assign an indicative priority: - **Critical:**
requires immediate administrator attention under the configured rules. -
**High:** indicates a serious incident requiring prompt review. -
**Medium:** indicates a moderate incident. - **Low:** indicates a
lower-priority report.

The score is only a triage aid and must be checked by a responsible
human operator.

### 5.4 Duplicate-Report Review Module

Compares selected report text and location details to identify possible
similarities. A similarity warning is not proof that two reports
describe the same event. Reports remain stored separately.

### 5.5 Response-Team Module

Allows administrators to add response teams with team name, code,
supported category, location, coordinates, contact details, and
availability.

### 5.6 Nearby Team Recommendation Module

Uses geographic coordinates and the Haversine distance formula to
estimate distance between an incident and response teams. It can suggest
a nearby available team whose service category matches the incident. The
suggestion is not a confirmed dispatch.

### 5.7 Administrator Dashboard

Provides incident summaries, priority levels, team information, incident
statuses, and mapped locations. Administrators can review reports and
update their progress.

## 6. System Workflow

``` text
Citizen
   |
   v
Register / Login
   |
   v
Submit Emergency Report
   |
   +--> Enter incident details
   +--> Add location / capture GPS
   +--> Optional voice input
   +--> Optional photo evidence
   |
   v
Flask Backend
   |
   +--> Validate and store report in SQLite
   +--> Calculate indicative priority
   +--> Check for possible duplicate reports
   |
   v
Administrator Dashboard
   |
   +--> Review incident and map location
   +--> Review priority and duplicate warning
   +--> Find a suitable nearby available team
   +--> Assign / update response status
   |
   v
Citizen Views Report Status
```

## 7. Data Managed by the Application

**User information** - User name - Email address - Hashed password

**Incident information** - Incident title, category, and description -
Reported location - Latitude and longitude, when available - Number of
people affected - Contact information, when provided - Uploaded image
path, when provided - Priority/severity and incident status - Submission
timestamp

**Response-team information** - Team name and code - Supported incident
category - Team location and coordinates - Contact details -
Availability

The application should collect only information needed for emergency
coordination and protect it appropriately.

## 8. Project Structure

``` text
Emergency_Finder/
│
├── app.py
├── requirements.txt
├── resqnet.db                 # Created automatically by the application
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
    └── uploads/               # Uploaded incident photos
```

The exact file names may differ from the final implementation. Database
initialization and upload-folder creation depend on the application
startup code.

## 9. Installation and Setup

### Prerequisites

-   Python 3.x
-   pip
-   A modern web browser
-   Internet access for map tiles and geocoding, if those services are
    enabled

### Step 1: Open the project directory

``` bash
cd Emergency_Finder
```

### Step 2: Create a virtual environment

``` bash
python -m venv venv
```

Windows PowerShell:

``` powershell
.\venv\Scripts\Activate.ps1
```

macOS or Linux:

``` bash
source venv/bin/activate
```

### Step 3: Install dependencies

``` bash
pip install -r requirements.txt
```

If the requirements file has not been created, install Flask:

``` bash
pip install Flask
```

Install any other dependencies specified by the actual application.

### Step 4: Run the application

``` bash
python app.py
```

Open the local URL printed in the terminal, commonly:

``` text
http://127.0.0.1:5000
```

## 10. Demonstration and Testing

1.  Register a new citizen account.
2.  Log in using the registered account.
3.  Submit an emergency report with a category, description, and
    location.
4.  Submit another report using the same category and verify that both
    reports are retained separately.
5.  Test GPS capture after granting browser location permission.
6.  Test voice input in a browser that supports the Speech Recognition
    API.
7.  Upload an optional incident photograph.
8.  Log in as an administrator and review the incident list.
9.  Check the displayed severity and possible-duplicate warning.
10. Register a response team and enter its location and availability.
11. Check whether a suitable nearby team is suggested when coordinates
    are available.
12. Update an incident through the available status stages and verify
    the change.

Use test data only. Do not use the prototype to coordinate a real
emergency.

## 11. Innovation and Novelty

Emergency Finder integrates several capabilities into one incident-management
workflow:

-   **Multi-channel reporting:** structured forms, voice-assisted input,
    and optional photo evidence.
-   **Location-aware reports:** GPS coordinates make incidents easier to
    locate on a map.
-   **Priority-assisted triage:** configurable rules highlight reports
    that may need urgent attention.
-   **Duplicate awareness without data loss:** similar reports are
    flagged while each submission is preserved.
-   **Location-based team suggestions:** geographic distance and
    category suitability help administrators identify a nearby available
    team.
-   **Centralized response visibility:** incident review, team
    information, map visualization, and status tracking are available in
    one dashboard.

The core innovation is the integration of these functions into one
accessible prototype.

## 12. Feasibility and Future Enhancements

### Feasibility

-   Flask provides a lightweight framework for the web application.
-   SQLite supports local prototype storage without a separate database
    server.
-   HTML, CSS, and JavaScript support a browser-based interface.
-   Leaflet and OpenStreetMap provide map visualization.
-   Browser geolocation and speech recognition are available when
    supported by the device and browser and when permission is granted.

### Future Enhancements

-   Integrate verified official emergency-service contact and dispatch
    workflows.
-   Add SMS, email, or push notifications.
-   Introduce role-based access for citizens, administrators, and
    response personnel.
-   Add real-time team location updates with consent and privacy
    safeguards.
-   Improve duplicate detection using a tested text-similarity or
    machine-learning model.
-   Add multilingual reporting and accessibility improvements.
-   Add audit logs, backups, monitoring, and stronger security controls.
-   Integrate verified weather, flood, fire, or other hazard data
    sources.
-   Conduct usability, security, and load testing before wider
    deployment.

## 13. Limitations and Safety Disclaimer

Emergency Finder is a hackathon prototype intended to demonstrate emergency
incident reporting and coordination.

-   It is **not** an official emergency service or certified emergency
    dispatch system.
-   Priority scores and team suggestions are decision-support outputs
    and must be reviewed by authorized personnel.
-   GPS accuracy depends on the device, browser, signal, and user
    permission.
-   Voice input depends on browser support, language availability,
    microphone permission, and network conditions.
-   Address lookup and map display depend on external OpenStreetMap
    services and their usage policies.
-   A suggested team is not a guarantee of availability, suitability, or
    arrival time.
-   Do not rely on this prototype for life-critical decisions or delay
    contacting local emergency services.

Before public deployment, implement secure session management, CSRF
protection, input validation, upload restrictions, rate limiting, HTTPS,
access controls, secure secrets, database backups, and privacy controls.

## 14. Conclusion

Emergency Finder aims to make emergency incident reporting and response
coordination more organized by connecting citizens and administrators
through a centralized web platform. By combining location-aware
reporting, priority assistance, duplicate awareness, response-team
management, map visualization, and status tracking, the prototype
demonstrates how digital tools can support more informed emergency
coordination.

## 15. Project Details

-   **Project Name:** Emergency Finder
-   **Project Category:** Emergency Response / Disaster Management
-   **Project Type:** Web Application Prototype
-   **Backend:** Python Flask
-   **Frontend:** HTML, CSS, JavaScript
-   **Database:** SQLite
-   **Mapping:** Leaflet and OpenStreetMap

Add the actual team members, institution, mentor, and contact details
before submitting this document.

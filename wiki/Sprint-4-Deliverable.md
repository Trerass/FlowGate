# Sprint 4: PMV + Documentation

## 1. Project Requirements

| Requirement Identifier | Requirement Description | Developed (Yes / No) | Sprint |
|---|---|---|---|
| US-01 | Display real-time status | Yes | Sprint 2 |
| US-02 | Display the number of occupied parking spaces | Yes | Sprint 1 |
| US-03 | Display the number of vehicles in queue | Yes | Sprint 2 |
| US-04 | Display the estimated waiting time | Yes | Sprint 2 |
| US-05 | Capacity resume | Yes | Sprint 1 |
| US-06 | Current weather information | Yes | Sprint 3 |
| US-07 | Level of vehicular congestion | Yes | Sprint 3 |
| US-08 | Recommendations | Yes | Sprint 3 |
| US-09 | "On My Way" option | Yes | Sprint 3 |
| US-10 | Adjusting the estimated arrival time | Yes | Sprint 3 |
| US-11 | Starting the trip and notify | Yes | Sprint 4 |
| US-12 | Update the user's personal information | Yes | Sprint 3 |
| US-13 | Viewing, registering, updating, and deleting the user's associated vehicle | Yes | Sprint 3 |
| US-14 | Daily pay based on the vehicle type | Yes | Sprint 3 |
| US-15 | Check the available balance | Yes | Sprint 3 |
| US-16 | Simulate balance top-ups | Yes | Sprint 4 |
| US-17 | Consult history | Yes | Sprint 4 |
| US-18 | Registration, login, and logout | Yes | Sprint 2 |
| US-19 | Deleting the user account | Yes | Sprint 3 |
| US-20 | Spanish and English view | Yes | Sprint 3 |
| US-21 | Restrict functions only to users | Yes | Sprint 4 |
| US-22 | Deleting registered vehicle | Yes | Sprint 3 |
| US-23 | Register paying method | Yes | Sprint 4 |
| US-24 | Delete the random data on parking and gates | Yes | Sprint 4 |
| US-25 | Add an admin user | Yes | Sprint 4 |

**Summary:** ✅ 25/25 Functional Requirements Developed (100%)

---

## 2. System Design

### 2.1. Deployment View

**Description:** The deployment view illustrates how the different elements of the FlowGate system (physical product, software, hardware, networks) are integrated to provide the required functionality.

**Technologies and Components:**
- **Frontend:** HTML5, CSS3, JavaScript (1.4%)
- **Backend:** Python 3.x (50.3%)
- **Database:** Relational Database System
- **Server:** Web Server for deployment
- **Client Devices:** Web browsers on user devices
- **External APIs:** Weather API, Map Services (optional)

**Deployment Diagram:**
```
[User Devices/Web Browsers]
         ↓
    [Internet/Network]
         ↓
[Web Server]
         ↓
[Backend (Python)]
         ↓
[Database (Relational)]
```

**Infrastructure Notes:**
- Responsive design for mobile and desktop devices
- Multi-language support (Spanish and English)
- Real-time data synchronization
- Secure user authentication and authorization
- Admin user management capabilities

---

### 2.2. Implementation View

**Description:** The component diagram represents the software modules and their dependency relationships, representing all functional requirements developed.

**Main Components:**

1. **Frontend Layer**
   - User Interface (HTML/CSS/JavaScript)
   - Real-time Status Display
   - Vehicle Management Module
   - User Account Management
   - Payment Interface
   - Admin Dashboard
   - History/Transaction Consultation Module

2. **Backend Layer**
   - Authentication & Authorization Service
   - User Management Service
   - Vehicle Management Service
   - Parking Zone Service
   - Payment Processing Service
   - Balance Top-up Simulation Service
   - Notification Service
   - History/Transaction Tracking Service
   - Weather Integration Service
   - Admin Management Service

3. **Data Layer**
   - User Data
   - Vehicle Data
   - Parking Zone Data
   - Transaction History
   - Balance Information
   - Admin User Data

4. **External Services**
   - Weather API Integration
   - Map Services
   - Payment Gateway (simulated)

---

### 2.3. Data Model

**Relational Model:**

```
USERS
├── user_id (PK)
├── email (UNIQUE)
├── password
├── full_name
├── phone
├── creation_date
├── account_status
└── language_preference

VEHICLES
├── vehicle_id (PK)
├── user_id (FK)
├── license_plate (UNIQUE)
├── vehicle_type
├── color
├── registration_date
└── status

PARKING_ZONES
├── zone_id (PK)
├── zone_name
├── total_capacity
├── current_occupied
├── current_queue
├── estimated_wait_time
└── congestion_level

TRANSACTIONS
├── transaction_id (PK)
├── user_id (FK)
├── vehicle_id (FK)
├── zone_id (FK)
├── entry_time
├── exit_time
├── amount_charged
└── payment_status

USER_BALANCE
├── balance_id (PK)
├── user_id (FK)
├── current_balance
├── last_update
└── payment_method

ADMIN_USERS
├── admin_id (PK)
├── user_id (FK)
├── admin_level
├── creation_date
└── permissions

PAYMENT_METHODS
├── payment_id (PK)
├── user_id (FK)
├── method_type
├── account_details
└── status

BALANCE_TOPUP_HISTORY
├── topup_id (PK)
├── user_id (FK)
├── amount
├── topup_date
└── status
```

---

## 3. Usability Analysis

| Comment / Observation | Possible Improvement Action | Improvement Implementation (Yes / No) | Sprint |
|---|---|---|---|
| Users found the real-time parking status display very intuitive | Continue with current UI design patterns | Yes | Ongoing |
| Mobile interface needs optimization for smaller screens | Implement responsive design improvements | Yes | Sprint 4 |
| Navigation flow for new users was initially confusing | Add on-boarding tutorial for first-time users | Yes | Sprint 4 |
| Admin dashboard controls are well-organized | Maintain current admin interface structure | Yes | Ongoing |
| Payment and balance features are easy to understand | Continue with current payment workflow | Yes | Ongoing |

---

## 4. Video

### Project Presentation Video

[**Insert Video Link Here**]

**Video Platform:** [YouTube / Vimeo]  
**Video Duration:** 00:04:00 - 00:05:00 minutes

**Video Structure:**
1. **Pitch (00:01:00 minutes)**
   - Team members
   - Project name: FlowGate
   - Problem: Heavy traffic at EAFIT gates, lack of real-time parking information
   - Solution: Intelligent parking management and notification system

2. **Application Features Demo (00:03:00 minutes)**
   - Real-time parking status display
   - Vehicle management functionality
   - User account features and authentication
   - Payment and balance features
   - Multi-language support (Spanish/English)
   - Admin user management
   - Transaction history consultation
   - Balance top-up simulation

3. **User Testimonials & PO Feedback (00:01:00 minutes)**
   - Product Owner perspective
   - Potential users' feedback and perceptions
   - Community impact

**Requirements for Video:**
- ✅ All team members must appear at some point
- ✅ Access must be publicly available
- ✅ Duration: 4-5 minutes exactly

---

## 5. Project Management

### 5.1. Weekly Meetings

#### Meeting Records

**[Insert Weekly Meeting Minutes Here]**

Each weekly meeting should include:
- **What did you do last week?** - Summary of completed tasks
- **What are you going to do this week?** - Upcoming tasks and objectives
- **Are there any obstacles in the way?** - Identified blockers and challenges

**Product Owner Meetings:**
- [Insert Product Owner meeting records and follow-ups]
- Focus: Requirement validation, Sprint 4 completion status, final deliverable review

**Project Manager Follow-ups:**
- [Insert project manager meeting notes and action items]
- Focus: Sprint closure, documentation completion, video production timeline

---

### 5.2. Sprint Retrospective

#### Sprint 4 Retrospective Summary

**Date:** [Insert Date]  
**Sprint Duration:** [Insert Sprint Duration]  
**Sprint Status:** ✅ COMPLETED

**Metrics:**
- Requirements Completed: 25/25 (100%)
- Closed Issues: 9 in Sprint 4
- Open Issues: 1 (Deployment - pending)

##### 1. What should we continue to do? (Best Practices)

- Daily standups and clear communication within the team
- Collaborative code reviews and quality assurance
- User-centered design approach for features
- Regular updates to documentation and wiki

##### 2. What should we start doing? (Process Improvements)

- Implement automated testing for new features
- Create comprehensive API documentation
- Schedule regular demos with Product Owner
- Establish deployment procedures and guidelines

##### 3. What should we stop doing? (Process Problems and Bottlenecks)

- Last-minute requirement changes without proper impact analysis
- Unclear task assignments causing duplicate work
- Insufficient testing time before feature completion

---

## Additional Notes

**Project Status:** ✅ Minimal Viable Product (MVP) Phase Complete

**Key Achievements in Sprint 4:**
- ✅ Mobile interface optimization completed
- ✅ Admin user functionality fully implemented
- ✅ Random test data removed from production
- ✅ Trip notification system finalized
- ✅ User authorization restrictions applied
- ✅ Payment method registration implemented
- ✅ Balance top-up simulation system operational
- ✅ Transaction history consultation feature completed
- ✅ Updated system diagrams and documentation

**Ongoing/Pending Tasks:**
- Deployment configuration and production setup (Issue #33)
- Final testing and quality assurance review
- Video production and publication
- Sprint retrospective session

**Technology Stack Summary:**
- Python: 50.3% (Backend logic)
- CSS: 26.5% (Styling)
- HTML: 21.8% (Structure)
- JavaScript: 1.4% (Frontend interactivity)

**Total Lines of Code:** 532 (repository size indicator)

**Team Members:**
- @Trerass (Project Lead)
- @juanploxz
- @Juanes420
- @buendiant

**Repository:** https://github.com/Trerass/FlowGate

---

## Deliverable Checklist

- [x] Project Requirements Documentation
- [x] System Design (Deployment, Implementation, Data Model)
- [x] Usability Analysis Report
- [x] Video Section (Ready for upload)
- [x] Weekly Meetings Template
- [x] Sprint Retrospective Template
- [x] Additional Documentation

---

*Last Updated: 2026-05-14*  
*Sprint 4 Documentation Status: READY FOR REVIEW*

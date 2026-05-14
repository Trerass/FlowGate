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
| US-16 | Simulate balance top-ups | No | Sprint 4 |
| US-17 | Consult history | No | Sprint 4 |
| US-18 | Registration, login, and logout | Yes | Sprint 2 |
| US-19 | Deleting the user account | Yes | Sprint 3 |
| US-20 | Spanish and English view | Yes | Sprint 3 |
| US-21 | Restrict functions only to users | Yes | Sprint 4 |
| US-22 | Deleting registered vehicle | Yes | Sprint 3 |
| US-23 | Register paying method | No | Sprint 4 |
| US-24 | Delete the random data on parking and gates | Yes | Sprint 4 |
| US-25 | Add an admin user | Yes | Sprint 4 |

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

2. **Backend Layer**
   - Authentication & Authorization Service
   - User Management Service
   - Vehicle Management Service
   - Parking Zone Service
   - Payment Processing Service
   - Notification Service
   - Weather Integration Service

3. **Data Layer**
   - User Data
   - Vehicle Data
   - Parking Zone Data
   - Transaction History
   - Balance Information

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
└── creation_date

PAYMENT_METHODS
├── payment_id (PK)
├── user_id (FK)
├── method_type
├── account_details
└── status
```

---

## 3. Usability Analysis

| Comment / Observation | Possible Improvement Action | Improvement Implementation (Yes / No) | Sprint |
|---|---|---|---|
| Users found the real-time parking status display very intuitive | Continue with current UI design patterns | Yes | Ongoing |
| Mobile interface needs optimization for smaller screens | Implement responsive design improvements | Yes | Sprint 4 |
| Payment method registration process is unclear to some users | Simplify payment registration flow with step-by-step guide | No | Future |

---

## 4. Video

### Project Presentation Video

[**Insert Video Link Here**]

**Video Platform:** [YouTube / Vimeo]  
**Video Duration:** 00:04:00 - 00:05:00 minutes

**Video Structure:**
1. **Pitch (00:01:00 minutes)**
   - Team members
   - Project name
   - Problem statement
   - Solution overview

2. **Application Features Demo (00:03:00 minutes)**
   - Real-time parking status display
   - Vehicle management functionality
   - User account features
   - Payment and balance features
   - Multi-language support

3. **User Testimonials (00:01:00 minutes)**
   - Product Owner perspective
   - Potential users' feedback and perceptions

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

**Project Manager Follow-ups:**
- [Insert project manager meeting notes and action items]

---

### 5.2. Sprint Retrospective

#### Sprint 4 Retrospective Summary

**Date:** [Insert Date]  
**Sprint Duration:** [Insert Sprint Duration]

##### 1. What should we continue to do? (Best Practices)

- [Best practice 1]
- [Best practice 2]
- [Best practice 3]

##### 2. What should we start doing? (Process Improvements)

- [Process improvement 1]
- [Process improvement 2]
- [Process improvement 3]

##### 3. What should we stop doing? (Process Problems and Bottlenecks)

- [Problem/bottleneck 1]
- [Problem/bottleneck 2]
- [Problem/bottleneck 3]

---

## Additional Notes

**Project Status:** Minimal Viable Product (MVP) Phase Complete

**Key Achievements in Sprint 4:**
- Mobile interface optimization completed
- Admin user functionality implemented
- Random test data removed from production
- Trip notification system finalized
- User authorization restrictions applied

**Ongoing Development:**
- Balance top-up simulation (US-16)
- History consultation feature (US-17)
- Payment method registration (US-23)

**Technology Stack Summary:**
- Python: 50.3%
- CSS: 26.5%
- HTML: 21.8%
- JavaScript: 1.4%

---

*Last Updated: 2026-05-14*

# Flowgate

## Overview
Flowgate is a web application designed to track and visualize traffic congestion at the entrances of parking areas outside the university. The platform helps car owners make better decisions before heading to campus by providing real-time traffic insights, parking management options, and smart recommendations.

With Flowgate, users can:
- Check the current traffic status at parking entrances.
- See how many people are currently heading toward the university in real time.
- Pay for parking using virtual cards.
- Reserve a parking spot in advance.
- Receive recommendations based on traffic conditions and Medellin's weather forecast.

The goal of Flowgate is to reduce congestion, improve parking efficiency, and enhance the overall commuting experience for university drivers.

---

## Features
- **Traffic Severity Indicator**: Visual representation (bar) showing the level of traffic congestion at parking entrances.
- **Real-Time Traffic Flow**: Live count of people currently on their way to the university.
- **Parking Payments**: Secure parking payments using virtual cards.
- **Parking Reservation**: Ability to reserve a parking spot ahead of time.
- **Smart Recommendations**: Personalized recommendations based on traffic conditions and local weather forecasts.

---

## Tech Stack
- **Language & Framework**: Python 3.12 · Django 5
- **Frontend**: Bootstrap 5
- **Database**: SQLite (can be swapped for PostgreSQL or MySQL in production)
- **Image Handling**: Pillow ≥ 10

---

## Quick Start
1. Clone the repository:
   ```bash
   git clone https://github.com/Trerass/FlowGate.git
   cd FlowGate
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

6. Open the application:
   ```text
   http://127.0.0.1:8000/
   ```

---

## Contact
For questions or collaboration inquiries:

- **Juan Antonio Buendia** - jabuendias@eafit.edu.co
- **Jeronimo Contreras Sierra** - jcontreras@eafit.edu.co

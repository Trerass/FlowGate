# Flowgate

## Overview
Flowgate is a web application designed to track and visualize traffic congestion at the entrances of parking areas outside the university. The platform helps car owners make better decisions before heading to campus by providing real-time traffic insights, parking management options, and smart recommendations.

With Flowgate, users can:
- Check the current traffic status at parking entrances.
- See how many people are currently heading toward the university in real time.
- Recharge their wallet through Wompi Colombia.
- Reserve a parking spot in advance.
- Receive recommendations based on traffic conditions and Medellin's weather forecast.

The goal of Flowgate is to reduce congestion, improve parking efficiency, and enhance the overall commuting experience for university drivers.

---

## Features
- **Traffic Severity Indicator**: Visual representation (bar) showing the level of traffic congestion at parking entrances.
- **Real-Time Traffic Flow**: Live count of people currently on their way to the university.
- **Parking Payments**: Secure COP wallet recharges through Wompi Colombia.
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

### Weather data
FlowGate uses the Open-Meteo forecast API for current weather on the dashboard. No API key is required.

By default the coordinates point to the La Aguacatala area in Medellin. You can override them before running the server:

```bash
set FLOWGATE_WEATHER_LATITUDE=6.198763
set FLOWGATE_WEATHER_LONGITUDE=-75.5772014
```

If the API is unavailable, the app keeps running with a fixed fallback instead of random weather values.

---

## Payments
FlowGate supports two payment providers:

- `PAYMENT_PROVIDER=demo`: academic mode. It works locally with SQLite and no external keys.
- `PAYMENT_PROVIDER=wompi`: Wompi Colombia sandbox/production mode, only when Wompi keys are configured.

The app never stores card numbers, CVV, PSE data, Nequi credentials, or Bancolombia credentials. A recharge is first saved as `PENDING` and the wallet balance only changes after the backend marks the transaction as `APPROVED`.

For the academic demo used in class:

```bash
set PAYMENT_PROVIDER=demo
```

For Wompi sandbox, create these environment variables before running the server:


```bash
set PAYMENT_PROVIDER=wompi
set WOMPI_ENV=sandbox
set WOMPI_PUBLIC_KEY=pub_test_xxxxxxxxxxxxxxxxx
set WOMPI_PRIVATE_KEY=prv_test_xxxxxxxxxxxxxxxxx
set WOMPI_INTEGRITY_SECRET=xxxxxxxxxxxxxxxxx
set WOMPI_EVENTS_SECRET=xxxxxxxxxxxxxxxxx
set APP_BASE_URL=http://127.0.0.1:8000
```

Production should use production Wompi keys, `PAYMENT_PROVIDER=wompi`, `WOMPI_ENV=production`, `DJANGO_DEBUG=False`, a strong `DJANGO_SECRET_KEY`, and a public HTTPS `APP_BASE_URL`.

### Sandbox flow
1. Run migrations and start Django:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
2. Log in and open `http://127.0.0.1:8000/payments/?tab=recharge`.
3. Enter a COP amount, for example `$ 20.000 COP`.
4. In `PAYMENT_PROVIDER=demo`, approve, reject, or cancel the academic transaction in the modal.
5. In `PAYMENT_PROVIDER=wompi`, continue to Wompi Checkout. After Wompi redirects back, FlowGate verifies the transaction from the backend and updates the wallet only if the status is `APPROVED`.

### Payment endpoints
- `POST /payments/recharge/`: creates a pending recharge and returns to the confirmation modal.
- `POST /payments/demo/`: resolves an academic demo payment as approved, declined, or voided.
- `GET /payments/wompi/return/`: Wompi redirect URL; verifies transaction status before crediting the wallet.
- `POST /payments/wompi/webhook/`: Wompi event receiver; validates the event checksum before updating local status.

---

## Contact
For questions or collaboration inquiries:

- **Juan Antonio Buendia** - jabuendias@eafit.edu.co
- **Jeronimo Contreras Sierra** - jcontreras@eafit.edu.co
- **Juan Pablo Parra El Masri** - jpparrae@eafit.edu.co

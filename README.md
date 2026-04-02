0# NOVA EATERY — QR Code Restaurant Ordering System

A complete restaurant ordering system with customer-facing pages,
kitchen dashboard, and admin management panel.

\---

## Quick Start

```bash
cd nova\\\_eatery
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000


## Default Credentials

|Role|Username|Password|
|-|-|-|
|Admin|admin|admin123|
|Kitchen Staff|kitchen|kitchen123|



## System URLs

|Page|URL|
|-|-|
|System Hub|/|
|Customer Landing|/landing|
|Menu|/menu|
|Cart|/cart|
|Kitchen Login|/kitchen-login|
|Kitchen Dashboard|/kitchen|
|Admin Login|/admin-login|
|Admin Dashboard|/admin-dashboard|
|Food Management|/admin-food|
|Sales Report|/admin-sales|
|Payment Confirmation|/admin-payment-confirmation|


## Payment methods 

1. Customer browses menu → adds items → proceeds to checkout
2. Customer sends money through mpesa 0706444779 
3. Customer ticks "I have sent the money" → places order
4. Order appears in admin dashboard as **Pending Payment**
5. Admin clicks **Confirm Payment** → order moves to kitchen
6. Kitchen staff update status: Preparing → Ready → Served
7. Customer sees live status on their order tracking page

## Tech Stack

* **Backend**: Python Flask + SQLite
* **Frontend**: HTML5, CSS3, Vanilla JavaScript
* **Auth**: Session-based with Werkzeug password hashing
* **Payment**: Manual M-PESA Paybill (no API integration)

\---
© 2026 TECH NOVA. All rights reserved.


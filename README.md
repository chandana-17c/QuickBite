# QuickBite

A responsive food ordering web application and REST API testing project for Software Testing & Quality Assurance. The React/Vite client calls a modular FastAPI service; the service owns the menu and all monetary calculations. There is no database or payment service.

## Features

- Food menu with 12 items, photos, categories, search and veg labels.
- Responsive homepage, sign in, registration, menu, bag, checkout and order confirmation screens.
- Add/remove items, adjust quantities, coupon entry, calculated delivery, tax and total.
- Demo registration and login. Passwords are hashed server-side (SHA-256 for this in-memory academic demo); browser storage contains only display name, email and a demo token.
- Postman collection with 32 scenarios and expected-value assertions; Newman CLI and HTML report configuration.

## Architecture

- `frontend/`: React, Vite, React Router, Context API and CSS.
- `backend/app/main.py`: FastAPI routes, Pydantic request models, predefined menu, in-memory users and Decimal pricing.
- `testing/`: importable Postman collection and local environment, plus a collection generator.
- `reports/`: Newman exports are written here when the commands below are run.

## Requirements

Python 3.10+ and Node.js 18+ with npm. Internet access is needed the first time packages are installed and for the remote Unsplash photos / Google Fonts. No database is needed.

## Run locally

### Backend

From this `QuickBite` directory, create and activate a virtual environment, install requirements, then run Uvicorn:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs. Health check: http://127.0.0.1:8000/api/health.

### Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server origin is allowed by the API CORS configuration.

### Demo account

- Email: `demo@quickbite.in`
- Password: `QuickBite123!`

Registration stores users in process memory and resets when the backend restarts. The login token is a demo token, not a production authorization mechanism.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Health status |
| POST | `/api/auth/register` | Register an in-memory demo user |
| POST | `/api/auth/login` | Verify demo credentials |
| GET | `/api/menu` | Return the authoritative menu |
| GET | `/api/menu/{item_id}` | Return one menu item |
| POST | `/api/cart/validate` | Validate item IDs and quantities |
| POST | `/api/orders/calculate` | Recalculate totals from menu data |
| POST | `/api/orders/checkout` | Validate and create an in-memory demo order response |

Calculation rules: minimum food subtotal ₹100.00; ₹40.00 delivery when subtotal is below ₹499.00; free delivery at ₹499.00 and above; `QUICK10` gives 10% off; `SAVE50` gives ₹50 off; tax is 5% of discounted subtotal. Each money result is rounded to two decimal places using Decimal and half-up rounding. Unknown coupon codes, invalid item IDs, invalid quantities and below-minimum totals receive 4xx responses. Client supplied prices are ignored.

## Postman and Newman

Import `testing/QuickBite_API_Testing.postman_collection.json` and `testing/QuickBite_Local.postman_environment.json` into Postman, select **QuickBite Local**, and ensure the API is running. The collection contains 34 requests; a collection pre-request script makes the registration email unique for each run. Requests are ordered so registration precedes duplicate registration and login.

Install Newman and the HTML reporter from the project root:

```powershell
npm install
```

Run the collection with live CLI assertions:

```powershell
npm run test:api
```

Generate a CLI summary and HTML report at `reports/newman-report.html`:

```powershell
npm run test:api:report
```

Export machine-readable results as well:

```powershell
npm run test:api:json
```

The Newman CLI/report output provides actual request counts, assertion pass/fail counts, response times and run duration. Reports are generated only by executing these commands; a report is not included until such a run succeeds.

## Defect demonstration

The final source contains the correct 5% tax rule. For a controlled live demonstration, temporarily change the tax calculation in `backend/app/main.py` from `money(discounted*Decimal("0.05"))` to `money(discounted*Decimal("0.04"))`, start/restart the API, and run `npm run test:api:report`. `QUICK10 discount and tax` will fail its expected tax assertion (₹11.21 expected for QUICK10 on ₹249; 4% produces ₹8.96). Restore `0.05`, rerun the suite and inspect the new report.

- Severity: Major (incorrect customer charge calculation).
- Priority: High (core order total is wrong).
- Reproduction: calculate order for item 1, quantity 1, coupon QUICK10.
- Expected: discounted subtotal ₹224.10; tax ₹11.21; total ₹275.31.
- Defective result: tax ₹8.96; total ₹273.06.
- Root cause: tax rate configured as 4% instead of 5%.
- Resolution: restore 5% and rerun the test suite.

This is a documented demonstration recipe, not a claimed execution. The defect is not present in the delivered source.

## Coverage and limitations

Postman/Newman metrics count API requests and assertions. They are not source-code coverage. Backend source coverage can be measured separately after dependencies are installed, for example by running `cd backend`, then `python -m coverage run -m uvicorn app.main:app` is not a useful request workload on its own; use an API-driving test harness with coverage enabled, then `python -m coverage report` / `python -m coverage html`. This project does not claim a source coverage percentage.

Authentication, orders and registration are in-memory demo flows, with no database persistence or real authorization/session enforcement. No payment processing is included. The demo SHA-256 password hash is not suitable for production; use a password hashing library with salt and a persistent identity store in a real deployment.


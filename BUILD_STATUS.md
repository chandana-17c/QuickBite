# Build status

## Implemented
- React/Vite responsive ordering UI: homepage, menu, registration, login, cart, checkout, confirmation.
- FastAPI service with all requested routes, Pydantic validation, in-memory demo account/registration, authoritative menu pricing and Decimal calculations.
- 12 menu items, remote food images, search/category filters, quantity editing and removal, coupon/quote/checkout flow.
- Importable Postman v2.1 collection and environment with 34 ordered scenarios and JavaScript expected-value assertions.
- Newman scripts for CLI execution, HTML report and JSON export; defect demonstration instructions.

## Execution status
- Source and collection generation completed locally.
- The available shell exposes Node.js v24.22.3 and Git. Python, `py`, npm, npx, uv and pip commands are unavailable in this execution environment.
- Consequently dependencies could not be installed; the FastAPI server, Vite app, Newman collection, live browser flow and actual HTML report have not been executed here. No test statistics are claimed.
- Run instructions are in README.md. Once Python/npm are available, start the backend and frontend, then execute `npm install` and `npm run test:api:report` from the project root. The genuine report will be saved under `reports/`.

## Known limitations
- Demo users/orders live in memory and reset on backend restart.
- Demo token is not enforced as authorization; authentication is a UI demo.
- Remote Unsplash image and Google Fonts requests need internet access.
- Source-code coverage has not been measured; Newman assertions are API test metrics.


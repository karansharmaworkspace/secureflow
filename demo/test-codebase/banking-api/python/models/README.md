# Python Models

Pydantic data model definitions for the Python banking API. Defines 3 entity schemas used across route handlers for request/response typing.

## Files

### user.py — Data Models (31 lines)

Pydantic v2 `BaseModel` classes:

- **`User`** — Primary user entity: `id` (int), `name`, `email`, `phone`, `account_number`, `ifsc_code`, `kyc_status`, `created_at` (datetime), `is_active` (bool, default True)
- **`AccountBalance`** — Balance response: `account_number`, `balance` (float), `currency` (default "INR"), `last_updated` (datetime)
- **`Transaction`** — Transaction record: `id` (int), `from_account`, `to_account`, `amount` (float), `status`, `timestamp` (datetime)

All models use `from pydantic import BaseModel` and provide automatic validation and serialization via FastAPI integration.

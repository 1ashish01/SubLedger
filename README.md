## Project Status

The core SubLedger billing backend has been implemented.

Implemented functionality includes:

- Plan and customer management
- Subscription management
- Invoice generation with plan-price snapshots
- Payment attempt creation and status updates
- Invoice balance and payment status tracking
- Ledger entries for invoice creation and payment events
- Database migrations using Alembic
- Automated API and business-logic tests

### Testing

The current automated test suite contains **43 passing tests**.

Run the test suite from the project root:

```bash
pytest
```

### API Documentation

Start the FastAPI application and access the interactive API documentation at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

Refer to [DESIGN.md](DESIGN.md) for the detailed Low-Level Design, entity relationships, architectural decisions, and billing workflows.
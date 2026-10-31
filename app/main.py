
from fastapi import FastAPI

from app.core.config import settings
from app.api.routes import (
    plans,
    customers,
    subscriptions,
    invoices,
    payments,
    ledger,
)


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)


# Health check
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "application": settings.app_name,
    }


# Register API routers
app.include_router(plans.router)
app.include_router(customers.router)
app.include_router(subscriptions.router)
app.include_router(invoices.router)
app.include_router(payments.router)
app.include_router(ledger.router)


from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate
from app.services import plan_service


router = APIRouter(
    prefix="/plans",
    tags=["Plans"],
)


@router.post(
    "/",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_plan(
    plan_data: PlanCreate,
    db: Session = Depends(get_db),
):
    return plan_service.create_plan(db, plan_data)


@router.get(
    "/",
    response_model=list[PlanResponse],
)
def get_all_plans(
    db: Session = Depends(get_db),
):
    return plan_service.get_all_plans(db)


@router.get(
    "/{plan_id}",
    response_model=PlanResponse,
)
def get_plan(
    plan_id: UUID,
    db: Session = Depends(get_db),
):
    return plan_service.get_plan(db, plan_id)


@router.patch(
    "/{plan_id}",
    response_model=PlanResponse,
)
def update_plan(
    plan_id: UUID,
    plan_data: PlanUpdate,
    db: Session = Depends(get_db),
):
    return plan_service.update_plan(
        db,
        plan_id,
        plan_data,
    )


@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_plan(
    plan_id: UUID,
    db: Session = Depends(get_db),
):
    plan_service.delete_plan(db, plan_id)

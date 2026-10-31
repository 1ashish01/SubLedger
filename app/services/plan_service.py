
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.plan import Plan
from app.repositories import plan_repository
from app.schemas.plan import PlanCreate, PlanUpdate


def create_plan(db: Session, plan_data: PlanCreate) -> Plan:
    existing_plan = plan_repository.get_plan_by_name(
        db,
        plan_data.name,
    )

    if existing_plan:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A plan with this name already exists",
        )

    plan = Plan(**plan_data.model_dump())

    return plan_repository.create_plan(db, plan)


def get_plan(db: Session, plan_id) -> Plan:
    plan = plan_repository.get_plan_by_id(db, plan_id)

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )

    return plan


def get_all_plans(db: Session) -> list[Plan]:
    return plan_repository.get_all_plans(db)


def update_plan(
    db: Session,
    plan_id,
    plan_data: PlanUpdate,
) -> Plan:
    plan = get_plan(db, plan_id)

    update_data = plan_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing_plan = plan_repository.get_plan_by_name(
            db,
            update_data["name"],
        )

        if existing_plan and existing_plan.id != plan.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A plan with this name already exists",
            )

    for field, value in update_data.items():
        setattr(plan, field, value)

    return plan_repository.update_plan(db, plan)


def delete_plan(db: Session, plan_id) -> None:
    plan = get_plan(db, plan_id)

    plan_repository.delete_plan(db, plan)

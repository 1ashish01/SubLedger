from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.plan import Plan


def create_plan(db: Session, plan: Plan) -> Plan:
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_plan_by_id(db: Session, plan_id) -> Plan | None:
    statement = select(Plan).where(Plan.id == plan_id)
    return db.scalar(statement)


def get_plan_by_name(db: Session, name: str) -> Plan | None:
    statement = select(Plan).where(Plan.name == name)
    return db.scalar(statement)


def get_all_plans(db: Session) -> list[Plan]:
    statement = select(Plan).order_by(Plan.created_at.desc())
    return list(db.scalars(statement).all())


def update_plan(db: Session, plan: Plan) -> Plan:
    db.commit()
    db.refresh(plan)
    return plan


def delete_plan(db: Session, plan: Plan) -> None:
    db.delete(plan)
    db.commit()
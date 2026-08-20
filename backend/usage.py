from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Usage


FREE_DAILY_LIMIT = 5


def get_usage_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def get_daily_usage(
    db: Session,
    user_identifier: str,
) -> int:
    usage_date = get_usage_date()

    statement = select(Usage).where(
        Usage.user_identifier == user_identifier,
        Usage.usage_date == usage_date,
    )

    usage = db.execute(statement).scalar_one_or_none()

    if usage is None:
        return 0

    return usage.verification_count


def can_verify(
    db: Session,
    user_identifier: str,
) -> bool:
    return get_daily_usage(
        db,
        user_identifier,
    ) < FREE_DAILY_LIMIT


def record_verification(
    db: Session,
    user_identifier: str,
) -> Usage:
    usage_date = get_usage_date()

    statement = select(Usage).where(
        Usage.user_identifier == user_identifier,
        Usage.usage_date == usage_date,
    )

    usage = db.execute(statement).scalar_one_or_none()

    if usage is None:
        usage = Usage(
            user_identifier=user_identifier,
            usage_date=usage_date,
            verification_count=1,
        )
        db.add(usage)
    else:
        usage.verification_count += 1

    db.commit()
    db.refresh(usage)

    return usage

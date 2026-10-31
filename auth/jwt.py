import jwt
from datetime import datetime, timedelta, timezone

from settings import settings


def create_access_token(data: dict):

    payload = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.JWT_EXPIRE_MINUTES
        )
    )

    payload.update({
        "exp": expire
    })

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
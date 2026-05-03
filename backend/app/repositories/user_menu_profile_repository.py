"""
Repository for UserMenuProfile CRUD operations.

Records which menu profile a user has selected.
One row per user; absence means the default profile applies.
"""

from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models import UserMenuProfile, MenuProfile


class UserMenuProfileRepository:
    """CRUD operations for UserMenuProfile."""

    def get_by_user_id(self, db: Session, user_id: str) -> Optional[UserMenuProfile]:
        return (
            db.query(UserMenuProfile)
            .options(joinedload(UserMenuProfile.profile))
            .filter(UserMenuProfile.user_id == user_id)
            .first()
        )

    def set_profile(self, db: Session, user_id: str, profile_id: str) -> UserMenuProfile:
        """Create or update the user's selected profile."""
        existing = db.query(UserMenuProfile).filter(UserMenuProfile.user_id == user_id).first()
        if existing:
            existing.profile_id = profile_id
            db.commit()
            db.refresh(existing)
            return existing

        record = UserMenuProfile(user_id=user_id, profile_id=profile_id)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


user_menu_profile_repository = UserMenuProfileRepository()

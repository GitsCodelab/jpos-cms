"""
Repository for MenuProfile CRUD operations.

Handles database access for menu profiles and their top-level
menu item associations.
"""

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models import MenuProfile, ProfileMenuItem, MenuItem


class MenuProfileRepository:
    """CRUD operations for MenuProfile."""

    def get_all_active(self, db: Session) -> List[MenuProfile]:
        return (
            db.query(MenuProfile)
            .filter(MenuProfile.is_active == True)
            .order_by(MenuProfile.display_name)
            .all()
        )

    def get_by_id(self, db: Session, profile_id: str) -> Optional[MenuProfile]:
        return db.query(MenuProfile).filter(MenuProfile.id == profile_id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[MenuProfile]:
        return db.query(MenuProfile).filter(MenuProfile.name == name).first()

    def get_default(self, db: Session) -> Optional[MenuProfile]:
        return (
            db.query(MenuProfile)
            .filter(MenuProfile.is_default == True, MenuProfile.is_active == True)
            .first()
        )

    def get_profile_with_menus(self, db: Session, profile_id: str) -> Optional[MenuProfile]:
        """Load profile together with ordered top-level menu items."""
        return (
            db.query(MenuProfile)
            .options(
                joinedload(MenuProfile.profile_menu_items).joinedload(ProfileMenuItem.menu_item)
            )
            .filter(MenuProfile.id == profile_id)
            .first()
        )

    def get_all(self, db: Session) -> List[MenuProfile]:
        """Return all profiles regardless of active status."""
        return (
            db.query(MenuProfile)
            .order_by(MenuProfile.display_name)
            .all()
        )

    def get_top_level_item_ids_for_profile(self, db: Session, profile_id: str) -> List[str]:
        """Return menu_item_id values linked to this profile (top-level only)."""
        rows = (
            db.query(ProfileMenuItem.menu_item_id)
            .filter(ProfileMenuItem.profile_id == profile_id)
            .all()
        )
        return [r.menu_item_id for r in rows]

    def add_item_to_profile(
        self, db: Session, profile_id: str, menu_item_id: str, order_index: int = 0
    ) -> ProfileMenuItem:
        """Link a top-level menu item to a profile (idempotent)."""
        existing = (
            db.query(ProfileMenuItem)
            .filter(
                ProfileMenuItem.profile_id == profile_id,
                ProfileMenuItem.menu_item_id == menu_item_id,
            )
            .first()
        )
        if existing:
            return existing
        link = ProfileMenuItem(
            profile_id=profile_id,
            menu_item_id=menu_item_id,
            order_index=order_index,
        )
        db.add(link)
        db.commit()
        db.refresh(link)
        return link

    def remove_item_from_profile(
        self, db: Session, profile_id: str, menu_item_id: str
    ) -> bool:
        """Unlink a menu item from a profile. Returns True if a row was deleted."""
        deleted = (
            db.query(ProfileMenuItem)
            .filter(
                ProfileMenuItem.profile_id == profile_id,
                ProfileMenuItem.menu_item_id == menu_item_id,
            )
            .delete(synchronize_session=False)
        )
        db.commit()
        return deleted > 0

    def set_active(self, db: Session, profile_id: str, is_active: bool) -> Optional[MenuProfile]:
        """Activate or deactivate a profile."""
        profile = self.get_by_id(db, profile_id)
        if not profile:
            return None
        profile.is_active = is_active
        db.commit()
        db.refresh(profile)
        return profile

    def create(self, db: Session, name: str, display_name: str, description: str = None, is_default: bool = False) -> MenuProfile:
        profile = MenuProfile(
            name=name,
            display_name=display_name,
            description=description,
            is_default=is_default,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile


menu_profile_repository = MenuProfileRepository()

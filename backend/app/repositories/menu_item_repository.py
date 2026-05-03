"""
Repository for MenuItem CRUD operations.

Handles database access for individual menu items and their
hierarchical parent-child relationships.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import MenuItem, ProfileMenuItem


class MenuItemRepository:
    """CRUD operations for MenuItem."""

    def get_by_key(self, db: Session, key: str) -> Optional[MenuItem]:
        return db.query(MenuItem).filter(MenuItem.key == key).first()

    def get_by_id(self, db: Session, item_id: str) -> Optional[MenuItem]:
        return db.query(MenuItem).filter(MenuItem.id == item_id).first()

    def get_top_level_for_profile(self, db: Session, profile_id: str) -> List[MenuItem]:
        """Return top-level items for a profile ordered by order_index."""
        return (
            db.query(MenuItem)
            .join(ProfileMenuItem, ProfileMenuItem.menu_item_id == MenuItem.id)
            .filter(ProfileMenuItem.profile_id == profile_id)
            .order_by(ProfileMenuItem.order_index)
            .all()
        )

    def create(
        self,
        db: Session,
        key: str,
        label: str,
        icon_name: str = None,
        permission: str = None,
        parent_id: str = None,
        order_index: int = 0,
        is_group: bool = False,
    ) -> MenuItem:
        item = MenuItem(
            key=key,
            label=label,
            icon_name=icon_name,
            permission=permission,
            parent_id=parent_id,
            order_index=order_index,
            is_group=is_group,
        )
        db.add(item)
        db.flush()  # get id without committing
        return item

    def link_to_profile(
        self, db: Session, profile_id: str, menu_item_id: str, order_index: int = 0
    ) -> ProfileMenuItem:
        link = ProfileMenuItem(
            profile_id=profile_id,
            menu_item_id=menu_item_id,
            order_index=order_index,
        )
        db.add(link)
        db.flush()
        return link

    def get_all(self, db: Session) -> List[MenuItem]:
        """Return all menu items ordered by order_index."""
        return (
            db.query(MenuItem)
            .order_by(MenuItem.order_index)
            .all()
        )

    def get_all_top_level(self, db: Session) -> List[MenuItem]:
        """Return all top-level menu items (parent_id is None)."""
        return (
            db.query(MenuItem)
            .filter(MenuItem.parent_id == None)  # noqa: E711
            .order_by(MenuItem.order_index)
            .all()
        )

    def set_active(self, db: Session, item_id: str, is_active: bool) -> Optional[MenuItem]:
        """Activate or deactivate a menu item."""
        item = self.get_by_id(db, item_id)
        if not item:
            return None
        item.is_active = is_active
        db.commit()
        db.refresh(item)
        return item

    def delete(self, db: Session, item_id: str) -> bool:
        """Delete a menu item by id. Returns True if deleted."""
        item = self.get_by_id(db, item_id)
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True


menu_item_repository = MenuItemRepository()

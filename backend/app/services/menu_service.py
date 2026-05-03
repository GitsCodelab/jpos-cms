"""
Menu Service — business logic for dynamic menu generation.

Responsibilities:
- Retrieve active menu profiles
- Build nested menu trees for a given profile
- Resolve the current user's profile (or default)
- Handle profile selection
"""

from typing import List, Optional, Dict
import uuid

from sqlalchemy.orm import Session

from app.models import MenuItem
from app.repositories.menu_profile_repository import menu_profile_repository
from app.repositories.menu_item_repository import menu_item_repository
from app.repositories.user_menu_profile_repository import user_menu_profile_repository
from app.schemas import (
    MenuProfileResponse,
    MenuProfileWithMenusResponse,
    MenuItemResponse,
    UserMenuProfileResponse,
    MenuItemAdminResponse,
    MenuItemCreate,
    MenuProfileStatusResponse,
    MenuItemStatusResponse,
)


class MenuService:
    """Business logic for menu profiles and dynamic menu generation."""

    # ------------------------------------------------------------------
    # Profile listing
    # ------------------------------------------------------------------

    def get_all_profiles(self, db: Session) -> List[MenuProfileResponse]:
        profiles = menu_profile_repository.get_all_active(db)
        return [MenuProfileResponse.model_validate(p) for p in profiles]

    # ------------------------------------------------------------------
    # Menu tree building
    # ------------------------------------------------------------------

    def _build_item_tree(self, item: MenuItem) -> MenuItemResponse:
        """Recursively build a MenuItemResponse tree from an ORM MenuItem."""
        children = [self._build_item_tree(child) for child in sorted(item.children, key=lambda c: c.order_index)]
        return MenuItemResponse(
            id=item.id,
            key=item.key,
            label=item.label,
            icon_name=item.icon_name,
            permission=item.permission,
            order_index=item.order_index,
            is_group=item.is_group,
            children=children,
        )

    def get_profile_menus(self, db: Session, profile_id: str) -> MenuProfileWithMenusResponse:
        """Return a profile with its full nested menu tree."""
        profile = menu_profile_repository.get_profile_with_menus(db, profile_id)
        if not profile:
            raise LookupError(f"Menu profile '{profile_id}' not found")

        # Sort top-level items by ProfileMenuItem.order_index
        sorted_links = sorted(profile.profile_menu_items, key=lambda pm: pm.order_index)
        menu_trees = [self._build_item_tree(pm.menu_item) for pm in sorted_links]

        return MenuProfileWithMenusResponse(
            id=profile.id,
            name=profile.name,
            display_name=profile.display_name,
            description=profile.description,
            is_default=profile.is_default,
            is_active=profile.is_active,
            created_at=profile.created_at,
            menus=menu_trees,
        )

    # ------------------------------------------------------------------
    # Current user menu
    # ------------------------------------------------------------------

    def get_current_menu(self, db: Session, user_id: str) -> MenuProfileWithMenusResponse:
        """
        Return the menu tree for the current user.
        Falls back to the default profile if the user has not selected one.
        """
        user_profile = user_menu_profile_repository.get_by_user_id(db, user_id)

        if user_profile:
            profile_id = user_profile.profile_id
        else:
            default = menu_profile_repository.get_default(db)
            if not default:
                raise RuntimeError("No default menu profile configured")
            profile_id = default.id

        return self.get_profile_menus(db, profile_id)

    # ------------------------------------------------------------------
    # Profile selection
    # ------------------------------------------------------------------

    def select_profile(self, db: Session, user_id: str, profile_id: str) -> UserMenuProfileResponse:
        """Assign a menu profile to a user."""
        profile = menu_profile_repository.get_by_id(db, profile_id)
        if not profile or not profile.is_active:
            raise LookupError(f"Menu profile '{profile_id}' not found or inactive")

        record = user_menu_profile_repository.set_profile(db, user_id, profile_id)
        # Reload profile for the response
        record.profile = profile

        return UserMenuProfileResponse(
            user_id=record.user_id,
            profile=MenuProfileResponse.model_validate(profile),
        )

    # ------------------------------------------------------------------
    # Admin: profile activate / deactivate
    # ------------------------------------------------------------------

    def get_all_profiles_admin(self, db: Session) -> List[MenuProfileResponse]:
        """Return all profiles regardless of active status (for admin)."""
        profiles = menu_profile_repository.get_all(db)
        return [MenuProfileResponse.model_validate(p) for p in profiles]

    def activate_profile(self, db: Session, profile_id: str) -> MenuProfileStatusResponse:
        profile = menu_profile_repository.set_active(db, profile_id, True)
        if not profile:
            raise LookupError(f"Menu profile '{profile_id}' not found")
        return MenuProfileStatusResponse.model_validate(profile)

    def deactivate_profile(self, db: Session, profile_id: str) -> MenuProfileStatusResponse:
        profile = menu_profile_repository.set_active(db, profile_id, False)
        if not profile:
            raise LookupError(f"Menu profile '{profile_id}' not found")
        return MenuProfileStatusResponse.model_validate(profile)

    # ------------------------------------------------------------------
    # Admin: menu items management
    # ------------------------------------------------------------------

    def get_all_items(self, db: Session) -> List[MenuItemAdminResponse]:
        """Return all menu items (flat) for admin management."""
        items = menu_item_repository.get_all(db)
        return [MenuItemAdminResponse.model_validate(i) for i in items]

    def create_item(self, db: Session, payload: MenuItemCreate) -> MenuItemAdminResponse:
        """Create a new top-level menu item."""
        existing = menu_item_repository.get_by_key(db, payload.key)
        if existing:
            raise ValueError(f"Menu item with key '{payload.key}' already exists")
        item = menu_item_repository.create(
            db,
            key=payload.key,
            label=payload.label,
            icon_name=payload.icon_name,
            permission=payload.permission,
            parent_id=None,
            order_index=payload.order_index,
            is_group=payload.is_group,
        )
        db.commit()
        db.refresh(item)
        return MenuItemAdminResponse.model_validate(item)

    def delete_item(self, db: Session, item_id: str) -> None:
        """Delete a menu item by id."""
        deleted = menu_item_repository.delete(db, item_id)
        if not deleted:
            raise LookupError(f"Menu item '{item_id}' not found")

    def activate_item(self, db: Session, item_id: str) -> MenuItemStatusResponse:
        item = menu_item_repository.set_active(db, item_id, True)
        if not item:
            raise LookupError(f"Menu item '{item_id}' not found")
        return MenuItemStatusResponse.model_validate(item)

    def deactivate_item(self, db: Session, item_id: str) -> MenuItemStatusResponse:
        item = menu_item_repository.set_active(db, item_id, False)
        if not item:
            raise LookupError(f"Menu item '{item_id}' not found")
        return MenuItemStatusResponse.model_validate(item)

    # ------------------------------------------------------------------
    # Admin: profile-item assignment
    # ------------------------------------------------------------------

    def get_profile_item_ids(self, db: Session, profile_id: str) -> List[str]:
        """Return the list of top-level item IDs assigned to a profile."""
        profile = menu_profile_repository.get_by_id(db, profile_id)
        if not profile:
            raise LookupError(f"Menu profile '{profile_id}' not found")
        return menu_profile_repository.get_top_level_item_ids_for_profile(db, profile_id)

    def add_item_to_profile(self, db: Session, profile_id: str, item_id: str) -> None:
        """Link a top-level menu item to a profile."""
        profile = menu_profile_repository.get_by_id(db, profile_id)
        if not profile:
            raise LookupError(f"Menu profile '{profile_id}' not found")
        item = menu_item_repository.get_by_id(db, item_id)
        if not item:
            raise LookupError(f"Menu item '{item_id}' not found")
        # Use count of existing items as order_index
        current = menu_profile_repository.get_top_level_item_ids_for_profile(db, profile_id)
        order_index = len(current)
        menu_profile_repository.add_item_to_profile(db, profile_id, item_id, order_index)

    def remove_item_from_profile(self, db: Session, profile_id: str, item_id: str) -> None:
        """Unlink a menu item from a profile."""
        profile = menu_profile_repository.get_by_id(db, profile_id)
        if not profile:
            raise LookupError(f"Menu profile '{profile_id}' not found")
        removed = menu_profile_repository.remove_item_from_profile(db, profile_id, item_id)
        if not removed:
            raise LookupError(f"Item '{item_id}' is not assigned to this profile")


menu_service = MenuService()

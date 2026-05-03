"""
Menu Router — REST API endpoints for dynamic menu profiles.

Endpoints:
    GET  /menu-profiles/admin/all        — list ALL profiles (admin)
    GET  /menu-profiles                  — list active profiles
    GET  /menu-profiles/{id}/menus       — profile with full menu tree
    POST /menu-profiles/select           — set current user's profile
    GET  /menu/current                   — current user's menu tree
    PATCH /menu-profiles/{id}/activate   — activate a profile
    PATCH /menu-profiles/{id}/deactivate — deactivate a profile
    GET  /menu-items                     — list all top-level items (admin)
    POST /menu-items                     — create a new top-level item
    DELETE /menu-items/{id}              — delete a menu item
    PATCH /menu-items/{id}/activate      — activate a menu item
    PATCH /menu-items/{id}/deactivate    — deactivate a menu item
    GET  /menu-profiles/{id}/items       — list item IDs assigned to a profile
    POST /menu-profiles/{id}/items       — add a menu item to a profile
    DELETE /menu-profiles/{id}/items/{item_id} — remove item from a profile
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.security import require_jwt_token
from app.services.menu_service import menu_service
from app.schemas import (
    MenuProfileResponse,
    MenuProfileWithMenusResponse,
    UserMenuProfileSelectRequest,
    UserMenuProfileResponse,
    MenuItemAdminResponse,
    MenuItemCreate,
    MenuProfileStatusResponse,
    MenuItemStatusResponse,
)
from typing import List

router = APIRouter(tags=["Menu"])


def _resolve_user_id(db: Session, username: str) -> str:
    """Resolve JWT sub (username) to the user's actual UUID primary key."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user.id


# ---------------------------------------------------------------------------
# GET /menu-profiles/admin/all  — must come before /{profile_id} routes
# ---------------------------------------------------------------------------

@router.get(
    "/menu-profiles/admin/all",
    response_model=List[MenuProfileResponse],
    summary="List all profiles including inactive ones (admin only)",
)
def list_all_menu_profiles(
    db: Session = Depends(get_db),
    _token: dict = Depends(require_jwt_token),
):
    return menu_service.get_all_profiles_admin(db)


# ---------------------------------------------------------------------------
# GET /menu-profiles
# ---------------------------------------------------------------------------

@router.get(
    "/menu-profiles",
    response_model=List[MenuProfileResponse],
    summary="List all active menu profiles",
)
def list_menu_profiles(
    db: Session = Depends(get_db),
    _token: dict = Depends(require_jwt_token),
):
    return menu_service.get_all_profiles(db)


# ---------------------------------------------------------------------------
# GET /menu-profiles/{profile_id}/menus
# ---------------------------------------------------------------------------

@router.get(
    "/menu-profiles/{profile_id}/menus",
    response_model=MenuProfileWithMenusResponse,
    summary="Get a profile with its full menu tree",
)
def get_profile_menus(
    profile_id: str,
    db: Session = Depends(get_db),
    _token: dict = Depends(require_jwt_token),
):
    try:
        return menu_service.get_profile_menus(db, profile_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# POST /menu-profiles/select
# ---------------------------------------------------------------------------

@router.post(
    "/menu-profiles/select",
    response_model=UserMenuProfileResponse,
    summary="Select a menu profile for the current user",
)
def select_menu_profile(
    body: UserMenuProfileSelectRequest,
    db: Session = Depends(get_db),
    token: dict = Depends(require_jwt_token),
):
    username: str = token.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = _resolve_user_id(db, username)
    try:
        return menu_service.select_profile(db, user_id, body.profile_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# GET /menu/current
# ---------------------------------------------------------------------------

@router.get(
    "/menu/current",
    response_model=MenuProfileWithMenusResponse,
    summary="Get the current user's menu tree",
)
def get_current_menu(
    db: Session = Depends(get_db),
    token: dict = Depends(require_jwt_token),
):
    username: str = token.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = _resolve_user_id(db, username)
    try:
        return menu_service.get_current_menu(db, user_id)
    except (LookupError, RuntimeError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# PATCH /menu-profiles/{profile_id}/activate
# ---------------------------------------------------------------------------

@router.patch(
    "/menu-profiles/{profile_id}/activate",
    response_model=MenuProfileStatusResponse,
    summary="Activate a menu profile",
)
def activate_menu_profile(
    profile_id: str,
    db: Session = Depends(get_db),
    _token: dict = Depends(require_jwt_token),
):
    try:
        return menu_service.activate_profile(db, profile_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# PATCH /menu-profiles/{profile_id}/deactivate
# ---------------------------------------------------------------------------

@router.patch(
    "/menu-profiles/{profile_id}/deactivate",
    response_model=MenuProfileStatusResponse,
    summary="Deactivate a menu profile",
)
def deactivate_menu_profile(
    profile_id: str,
    db: Session = Depends(get_db),
    _token: dict = Depends(require_jwt_token),
):
    try:
        return menu_service.deactivate_profile(db, profile_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# GET /menu-items
# ---------------------------------------------------------------------------

@router.get(
    "/menu-items",
    response_model=List[MenuItemAdminResponse],
    summary="List all top-level menu items for admin management",
)
def list_menu_items(
    db: Session = Depends(get_db),
    _token: dict = Depends(require_jwt_token),
):
    return menu_service.get_all_items(db)


# ---------------------------------------------------------------------------
# POST /menu-items
# ---------------------------------------------------------------------------

@router.post(
    "/menu-items",
    response_model=MenuItemAdminResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new top-level menu item",
)
def create_menu_item(
    body: MenuItemCreate,
    db: Session = Depends(get_db),
    _token: dict = Depends(require_jwt_token),
):
    try:
        return menu_service.create_item(db, body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# ---------------------------------------------------------------------------
# DELETE /menu-items/{item_id}
# ---------------------------------------------------------------------------

@router.delete(
    "/menu-items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a menu item",
)
def delete_menu_item(
    item_id: str,
    db: Session = Depends(get_db),
    _token: dict = Depends(require_jwt_token),
):
    try:
        menu_service.delete_item(db, item_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# PATCH /menu-items/{item_id}/activate
# ---------------------------------------------------------------------------

@router.patch(
    "/menu-items/{item_id}/activate",
    response_model=MenuItemStatusResponse,
    summary="Activate a menu item",
)
def activate_menu_item(
    item_id: str,
    db: Session = Depends(get_db),
    _token: dict = Depends(require_jwt_token),
):
    try:
        return menu_service.activate_item(db, item_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# PATCH /menu-items/{item_id}/deactivate
# ---------------------------------------------------------------------------

@router.patch(
    "/menu-items/{item_id}/deactivate",
    response_model=MenuItemStatusResponse,
    summary="Deactivate a menu item",
)
def deactivate_menu_item(
    item_id: str,
    db: Session = Depends(get_db),
    _token: dict = Depends(require_jwt_token),
):
    try:
        return menu_service.deactivate_item(db, item_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# GET /menu-profiles/{profile_id}/items
# ---------------------------------------------------------------------------

@router.get(
    "/menu-profiles/{profile_id}/items",
    response_model=List[str],
    summary="List menu item IDs assigned to a profile",
)
def get_profile_item_ids(
    profile_id: str,
    db: Session = Depends(get_db),
    _token: dict = Depends(require_jwt_token),
):
    try:
        return menu_service.get_profile_item_ids(db, profile_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# POST /menu-profiles/{profile_id}/items
# ---------------------------------------------------------------------------

class ProfileItemRequest(BaseModel):
    item_id: str


@router.post(
    "/menu-profiles/{profile_id}/items",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Assign a top-level menu item to a profile",
)
def add_item_to_profile(
    profile_id: str,
    body: ProfileItemRequest,
    db: Session = Depends(get_db),
    _token: dict = Depends(require_jwt_token),
):
    try:
        menu_service.add_item_to_profile(db, profile_id, body.item_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# DELETE /menu-profiles/{profile_id}/items/{item_id}
# ---------------------------------------------------------------------------

@router.delete(
    "/menu-profiles/{profile_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a menu item from a profile",
)
def remove_item_from_profile(
    profile_id: str,
    item_id: str,
    db: Session = Depends(get_db),
    _token: dict = Depends(require_jwt_token),
):
    try:
        menu_service.remove_item_from_profile(db, profile_id, item_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

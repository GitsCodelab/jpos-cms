"""
Menu Seed Data — Phase 04

Creates four default menu profiles in the database, seeding them with
the full Standard sidebar structure taken from the frontend menuConfig.

Profiles:
  1. Standard      — full menu (default)
  2. Compact       — core operations only
  3. Operations    — operations & monitoring focused
  4. Fraud Analyst — fraud & transactions focused

Safe to re-run: skips already-seeded profiles.
"""

from sqlalchemy.orm import Session

from app.models import MenuProfile, MenuItem, ProfileMenuItem
from app.repositories.menu_item_repository import menu_item_repository
from app.repositories.menu_profile_repository import menu_profile_repository

# ---------------------------------------------------------------------------
# Full menu structure (mirrors frontend menuConfig.jsx)
# Each item: (key, label, icon_name, permission, children)
# ---------------------------------------------------------------------------

FULL_MENU = [
    ("issuing", "Issuing", "CreditCardOutlined", "issuing", [
        ("/customers", "Customers", "TeamOutlined", "customers.list", []),
        ("/issuing/accounts", "Accounts", "BankOutlined", "issuing.accounts", []),
        ("/issuing/cards", "Cards", "CreditCardOutlined", "issuing.cards", []),
        ("/issuing/cardholders", "Cardholders", "IdcardOutlined", "issuing.cardholders", []),
        ("/issuing/delivery", "Delivery", "SendOutlined", "issuing.delivery", []),
        ("/issuing/operations", "Operations", "ToolOutlined", "issuing.operations", []),
        ("/issuing/operational-requests", "Operational requests", "FormOutlined", "issuing.operational_requests", []),
        ("/issuing/dispute-operations", "Dispute operations", "ExceptionOutlined", "issuing.dispute_operations", []),
        ("/issuing/applications", "Applications", "ContainerOutlined", "issuing.applications", []),
        ("issuing-credit", "Credit", "DollarOutlined", "issuing.credit", [
            ("/issuing/credit/blacklist", "Black list", "StopOutlined", "issuing.credit.blacklist", []),
        ]),
        ("issuing-disputes", "Disputes", "ExceptionOutlined", "issuing.disputes", [
            ("/issuing/disputes", "Disputes", "ExceptionOutlined", "issuing.disputes.list", []),
        ]),
        ("issuing-loyalty", "Loyalty", "TagOutlined", "issuing.loyalty", [
            ("/issuing/loyalty", "Loyalty", "TagOutlined", "issuing.loyalty.list", []),
        ]),
        ("issuing-emv", "EMV", "SafetyOutlined", "issuing.emv", [
            ("/issuing/emv/documents", "Documents", "FileProtectOutlined", "issuing.emv.documents", []),
        ]),
    ]),
    ("acquiring", "Acquiring", "ShopOutlined", "acquiring", [
        ("/acquiring/accounts", "Accounts", "BankOutlined", "acquiring.accounts", []),
        ("/acquiring/merchants", "Merchants", "ShopOutlined", "acquiring.merchants", []),
        ("/acquiring/terminals", "Terminals", "DesktopOutlined", "acquiring.terminals", []),
        ("/acquiring/operations", "Operations", "ToolOutlined", "acquiring.operations", []),
        ("/acquiring/dispute-operations", "Dispute operations", "ExceptionOutlined", "acquiring.dispute_operations", []),
        ("/acquiring/applications", "Applications", "ContainerOutlined", "acquiring.applications", []),
        ("acquiring-configuration", "Configuration", "SettingOutlined", "acquiring.configuration", [
            ("/acquiring/configuration", "Configuration", "SettingOutlined", "acquiring.configuration.list", []),
        ]),
        ("acquiring-disputes", "Disputes", "ExceptionOutlined", "acquiring.disputes", [
            ("/acquiring/disputes/vouchers", "Vouchers batches", "FolderOutlined", "acquiring.disputes.vouchers", []),
            ("/acquiring/disputes/invoices", "Invoices", "FileTextOutlined", "acquiring.disputes.invoices", []),
            ("/acquiring/disputes/mcc-groups", "MCC redefinition groups", "TagsOutlined", "acquiring.disputes.mcc_groups", []),
            ("/acquiring/disputes/companies", "Companies", "BankOutlined", "acquiring.disputes.companies", []),
        ]),
    ]),
    ("operational-rules", "Operational Rules", "BookOutlined", "operational_rules", [
        ("/operational-rules/accounting", "Accounting", "DollarOutlined", "operational_rules.accounting", []),
        ("/operational-rules/processing", "Processing", "SyncOutlined", "operational_rules.processing", []),
        ("/operational-rules/authorization", "Authorization", "SafetyOutlined", "operational_rules.authorization", []),
        ("/operational-rules/naming", "Naming", "TagsOutlined", "operational_rules.naming", []),
        ("/operational-rules/events", "Events", "BellOutlined", "operational_rules.events", []),
        ("/operational-rules/matching", "Matching", "CheckSquareOutlined", "operational_rules.matching", []),
        ("/operational-rules/modifiers", "Modifiers", "SlidersOutlined", "operational_rules.modifiers", []),
        ("/operational-rules/checks", "Checks", "FileProtectOutlined", "operational_rules.checks", []),
        ("/operational-rules/disputes", "Disputes", "ExceptionOutlined", "operational_rules.disputes", []),
    ]),
    ("payment-orders", "Payment Orders", "OrderedListOutlined", "payment_orders", [
        ("/payment-orders/services", "Services", "ApiOutlined", "payment_orders.services", []),
        ("/payment-orders/service-providers", "Service providers", "CustomerServiceOutlined", "payment_orders.service_providers", []),
        ("/payment-orders/parameters", "Parameters", "SlidersOutlined", "payment_orders.parameters", []),
        ("/payment-orders/applications", "Applications", "ContainerOutlined", "payment_orders.applications", []),
        ("/payment-orders/orders", "Orders", "OrderedListOutlined", "payment_orders.orders", []),
    ]),
    ("payment-system", "Payment System", "TransactionOutlined", "payment_system", [
        ("/payment-system/mastercard", "MasterCard", "CreditCardOutlined", "payment_system.mastercard", []),
        ("/payment-system/visa", "VISA", "CreditCardOutlined", "payment_system.visa", []),
        ("/payment-system/cup", "China Union Pay", "CreditCardOutlined", "payment_system.cup", []),
        ("/payment-system/amex", "American Express", "CreditCardOutlined", "payment_system.amex", []),
        ("/payment-system/jcb", "Japan Credit Bureau", "CreditCardOutlined", "payment_system.jcb", []),
        ("/payment-system/mir", "MIR", "CreditCardOutlined", "payment_system.mir", []),
        ("/payment-system/nbc", "NBC", "BankOutlined", "payment_system.nbc", []),
        ("/payment-system/meeza", "Meeza", "CreditCardOutlined", "payment_system.meeza", []),
        ("/payment-system/reconciliation", "Reconciliation", "ReconciliationOutlined", "payment_system.reconciliation", []),
        ("/payment-system/swift", "SWIFT", "GlobalOutlined", "payment_system.swift", []),
        ("/payment-system/diners", "Diners Club", "CreditCardOutlined", "payment_system.diners", []),
        ("/payment-system/gim", "GIM", "BankOutlined", "payment_system.gim", []),
    ]),
    ("monitoring", "Monitoring", "MonitorOutlined", "monitoring", [
        ("/monitoring/notifications", "Notifications", "BellOutlined", "monitoring.notifications", []),
        ("/monitoring/process-files", "Process files", "FileOutlined", "monitoring.process_files", []),
        ("/monitoring/process-schedule", "Process Schedule", "ScheduleOutlined", "monitoring.process_schedule", []),
        ("/monitoring/configuration", "Configuration", "SettingOutlined", "monitoring.configuration", []),
        ("/monitoring/process-logs", "Process logs", "FileSearchOutlined", "monitoring.process_logs", []),
        ("/monitoring/audit-logs", "Audit logs", "AuditOutlined", "monitoring.audit_logs", []),
        ("/monitoring/report-runs", "Report runs", "BarChartOutlined", "monitoring.report_runs", []),
        ("/monitoring/user-sessions", "User sessions", "TeamOutlined", "monitoring.user_sessions", []),
        ("/monitoring/atm-monitoring", "ATM monitoring", "DesktopOutlined", "monitoring.atm_monitoring", []),
        ("monitoring-mis", "MIS", "PieChartOutlined", "monitoring.mis", [
            ("/monitoring/mis", "MIS", "PieChartOutlined", "monitoring.mis.list", []),
        ]),
    ]),
    ("reconciliation", "Reconciliation", "ReconciliationOutlined", "reconciliation", [
        ("/reconciliation/cbs", "CBS", "DatabaseOutlined", "reconciliation.cbs", []),
        ("/reconciliation/atm", "ATM", "DesktopOutlined", "reconciliation.atm", []),
        ("/reconciliation/host", "Host", "ClusterOutlined", "reconciliation.host", []),
        ("/reconciliation/service-provider", "Service provider", "CustomerServiceOutlined", "reconciliation.service_provider", []),
    ]),
    ("routing", "Routing", "BranchesOutlined", "routing", [
        ("/routing/operations", "Operations", "ToolOutlined", "routing.operations", []),
    ]),
    ("campaigns", "Campaigns", "NotificationOutlined", "campaigns", [
        ("/campaigns/campaigns", "Campaigns", "NotificationOutlined", "campaigns.list", []),
        ("/campaigns/promo-campaigns", "Promo campaigns", "TagOutlined", "campaigns.promo", []),
        ("/campaigns/applications", "Applications", "ContainerOutlined", "campaigns.applications", []),
    ]),
    ("fraud-prevention", "Fraud Prevention", "BugOutlined", "fraud_prevention", [
        ("/fraud-prevention/suites", "Suites", "AppstoreAddOutlined", "fraud_prevention.suites", []),
        ("/fraud-prevention/cases", "Cases", "FolderOutlined", "fraud_prevention.cases", []),
        ("/fraud-prevention/matrices", "Matrices", "BlockOutlined", "fraud_prevention.matrices", []),
        ("/fraud-prevention/alerts", "Fraud alerts", "BellOutlined", "fraud_prevention.alerts", []),
        ("/fraud-prevention/alert-monitoring", "Fraud alert monitoring", "MonitorOutlined", "fraud_prevention.alert_monitoring", []),
    ]),
    ("structure", "Structure", "ClusterOutlined", "structure", [
        ("/structure/bank-organization", "Bank organization", "BankOutlined", "structure.bank_organization", []),
        ("/structure/networks", "Networks", "GlobalOutlined", "structure.networks", []),
    ]),
    ("administration", "Administration", "CrownOutlined", "administration", [
        ("/administration/processes", "Processes", "SyncOutlined", "administration.processes", []),
        ("/administration/permissions", "Permissions", "LockOutlined", "administration.permissions", []),
        ("/administration/communication", "Communication", "PhoneOutlined", "administration.communication", []),
        ("/administration/security", "Security", "SafetyOutlined", "administration.security", []),
        ("/administration/interface", "Interface", "DesktopOutlined", "administration.interface", []),
        ("/administration/settings", "Settings", "SettingOutlined", "administration.settings", []),
    ]),
    ("configuration", "Configuration", "SettingOutlined", "configuration", [
        ("/configuration/calendar", "Calendar", "CalendarOutlined", "configuration.calendar", []),
        ("/configuration/fees", "Fees", "DollarOutlined", "configuration.fees", []),
        ("/configuration/limits", "Limits", "DashboardOutlined", "configuration.limits", []),
        ("/configuration/converters", "Converters", "RetweetOutlined", "configuration.converters", []),
        ("/configuration/cycles", "Cycles", "SyncOutlined", "configuration.cycles", []),
        ("/configuration/rates", "Rates", "RiseOutlined", "configuration.rates", []),
        ("/configuration/card-types", "Card types", "CreditCardOutlined", "configuration.card_types", []),
        ("/configuration/notification", "Notification", "BellOutlined", "configuration.notification", []),
        ("/configuration/reporting", "Reporting", "BarChartOutlined", "configuration.reporting", []),
        ("/configuration/scoring", "Scoring", "FundOutlined", "configuration.scoring", []),
        ("/configuration/database-connections", "Database Connections", "DatabaseOutlined", "configuration.database_connections", []),
        ("configuration-menu", "Menu", "AppstoreAddOutlined", "configuration.menu", [
            ("/configuration/menu-profiles", "Menu Profiles", "AppstoreOutlined", "configuration.menu.profiles", []),
            ("/configuration/menu-items", "Menu Items", "UnorderedListOutlined", "configuration.menu.items", []),
        ]),
        ("configuration-directory", "Directory", "FolderOutlined", "configuration.directory", [
            ("/configuration/directory/flexible-fields", "Flexible fields", "FormOutlined", "configuration.directory.flexible_fields", []),
        ]),
        ("configuration-applications", "Applications", "ContainerOutlined", "configuration.applications", [
            ("/configuration/applications/validation", "Configuration validation", "CheckSquareOutlined", "configuration.applications.validation", []),
        ]),
    ]),
]

# ---------------------------------------------------------------------------
# Profile definitions: name → list of top-level keys to include
# ---------------------------------------------------------------------------

PROFILES = [
    {
        "name": "standard",
        "display_name": "Standard",
        "description": "Full menu with all available sections. Recommended for administrators.",
        "is_default": True,
        "top_level_keys": None,  # None = all items
    },
    {
        "name": "compact",
        "display_name": "Compact",
        "description": "Core operational sections. Ideal for daily transaction processing.",
        "is_default": False,
        "top_level_keys": [
            "monitoring",
            "reconciliation",
            "fraud-prevention",
            "configuration",
        ],
    },
    {
        "name": "operations",
        "display_name": "Operations",
        "description": "Operations and monitoring focused. Suited for operations teams.",
        "is_default": False,
        "top_level_keys": [
            "monitoring",
            "reconciliation",
            "routing",
            "administration",
            "configuration",
        ],
    },
    {
        "name": "fraud-analyst",
        "display_name": "Fraud Analyst",
        "description": "Fraud monitoring and analysis focused. Optimized for fraud analysts.",
        "is_default": False,
        "top_level_keys": [
            "fraud-prevention",
            "monitoring",
            "reconciliation",
            "configuration",
        ],
    },
    {
        "name": "reports-files",
        "display_name": "Reports & Files",
        "description": "Focused on monitoring, file processing, and reporting. Suited for reporting teams.",
        "is_default": False,
        "top_level_keys": [
            "monitoring",
            "payment-system",
            "reconciliation",
            "configuration",
        ],
    },
]


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

def _ensure_item(db: Session, key: str, label: str, icon_name: str, permission: str, parent_id: str, order_index: int, is_group: bool) -> MenuItem:
    """Get existing item by key or create it. Updates parent_id if it changed (supports restructuring)."""
    existing = menu_item_repository.get_by_key(db, key)
    if existing:
        # Reparent if the seed structure changed
        if existing.parent_id != parent_id:
            existing.parent_id = parent_id
            existing.order_index = order_index
            db.flush()
        return existing
    return menu_item_repository.create(
        db,
        key=key,
        label=label,
        icon_name=icon_name,
        permission=permission,
        parent_id=parent_id,
        order_index=order_index,
        is_group=is_group,
    )


def _seed_children(db: Session, children: list, parent_id: str) -> None:
    """Recursively create child menu items."""
    for idx, (key, label, icon_name, permission, grandchildren) in enumerate(children):
        is_group = len(grandchildren) > 0
        item = _ensure_item(db, key, label, icon_name, permission, parent_id, idx, is_group)
        if grandchildren:
            _seed_children(db, grandchildren, item.id)


def seed_menu_profiles(db: Session) -> None:
    """
    Idempotent seed: creates menu profiles and items if they don't already exist.
    Safe to call on every startup.
    """
    # 1. Ensure all menu items exist
    top_level_items: dict[str, MenuItem] = {}
    for idx, (key, label, icon_name, permission, children) in enumerate(FULL_MENU):
        is_group = len(children) > 0
        item = _ensure_item(db, key, label, icon_name, permission, None, idx, is_group)
        top_level_items[key] = item
        if children:
            _seed_children(db, children, item.id)

    db.commit()

    # 2. Ensure all profiles exist and link their top-level items
    for profile_def in PROFILES:
        existing = menu_profile_repository.get_by_name(db, profile_def["name"])
        if existing:
            continue  # already seeded

        profile = menu_profile_repository.create(
            db,
            name=profile_def["name"],
            display_name=profile_def["display_name"],
            description=profile_def["description"],
            is_default=profile_def["is_default"],
        )

        keys_to_include = profile_def["top_level_keys"]
        if keys_to_include is None:
            # Standard: include all top-level items in order
            ordered_items = [top_level_items[key] for key, *_ in FULL_MENU if key in top_level_items]
        else:
            ordered_items = [top_level_items[key] for key in keys_to_include if key in top_level_items]

        for order_idx, item in enumerate(ordered_items):
            menu_item_repository.link_to_profile(db, profile.id, item.id, order_idx)

    db.commit()
    print("[seed] Menu profiles seeded successfully.")

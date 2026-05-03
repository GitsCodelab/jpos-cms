"""
Customer Account Repository — Phase 05

Queries MAIN.ACC_ACCOUNT joined to MAIN.PRD_CUSTOMER.

Column aliases match CustomerAccountResponse fields:
  id             → ACC_ACCOUNT.ID
  customer_id    → ACC_ACCOUNT.CUSTOMER_ID
  account_number → ACC_ACCOUNT.ACCOUNT_NUMBER
  currency       → ACC_ACCOUNT.CURRENCY
  status         → ACC_ACCOUNT.STATUS
  balance        → NULL (balance data not stored in ACC_ACCOUNT)
"""

from typing import Any, List

from sqlalchemy import text
from sqlalchemy.orm import Session


def _schema_prefix(db: Session) -> str:
    try:
        opts = db.get_bind().get_execution_options()
        schema = (opts.get("schema_translate_map") or {}).get(None) or ""
    except Exception:
        schema = ""
    return f"{schema}." if schema else ""


class CustomerAccountRepository:

    def get_by_customer(self, db: Session, customer_id: str) -> List[Any]:
        p = _schema_prefix(db)
        sql = text(f"""
            SELECT
                TO_CHAR(a.ID)          AS id,
                TO_CHAR(a.CUSTOMER_ID) AS customer_id,
                a.ACCOUNT_NUMBER       AS account_number,
                a.CURRENCY             AS currency,
                CAST(NULL AS NUMBER)   AS balance,
                a.STATUS               AS status
            FROM {p}ACC_ACCOUNT a
            JOIN {p}PRD_CUSTOMER c ON c.ID = a.CUSTOMER_ID
            WHERE a.CUSTOMER_ID = :cid
            ORDER BY a.ID DESC
        """)
        return db.execute(sql, {"cid": int(customer_id)}).mappings().all()


customer_account_repository = CustomerAccountRepository()

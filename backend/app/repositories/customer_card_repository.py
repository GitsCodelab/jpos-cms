"""
Customer Card Repository — Phase 05

Queries MAIN.ISS_CARD joined with MAIN.ISS_CARD_INSTANCE (latest instance)
to return card details for a customer.

Column aliases:
  id            → ISS_CARD.ID
  customer_id   → ISS_CARD.CUSTOMER_ID
  card_number   → ISS_CARD.CARD_MASK  (may be full PAN; service masks it)
  card_type     → ISS_CARD.CATEGORY
  status        → ISS_CARD_INSTANCE.STATUS (latest instance, or NULL)
  expiry_date   → ISS_CARD_INSTANCE.EXPIR_DATE (formatted MM/YYYY)
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


class CustomerCardRepository:

    def get_by_customer(self, db: Session, customer_id: str) -> List[Any]:
        p = _schema_prefix(db)
        sql = text(f"""
            SELECT
                TO_CHAR(c.ID)          AS id,
                TO_CHAR(c.CUSTOMER_ID) AS customer_id,
                c.CARD_MASK            AS card_number,
                c.CATEGORY             AS card_type,
                ci.STATUS              AS status,
                TO_CHAR(ci.EXPIR_DATE, 'MM/YYYY') AS expiry_date
            FROM {p}ISS_CARD c
            LEFT JOIN {p}ISS_CARD_INSTANCE ci
                   ON ci.CARD_ID = c.ID AND ci.IS_LAST_SEQ_NUMBER = 1
            WHERE c.CUSTOMER_ID = :cid
            ORDER BY c.ID DESC
        """)
        return db.execute(sql, {"cid": int(customer_id)}).mappings().all()


customer_card_repository = CustomerCardRepository()

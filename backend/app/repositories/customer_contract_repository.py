"""
Customer Contract Repository — Phase 05

Queries MAIN.PRD_CONTRACT joined to MAIN.PRD_CUSTOMER.
Uses MAIN.GET_ARTICLE_DESC() to resolve CONTRACT_TYPE code to a description.

Column aliases match CustomerContractResponse fields:
  id                → PRD_CONTRACT.ID
  customer_id       → PRD_CONTRACT.CUSTOMER_ID
  contract_number   → PRD_CONTRACT.CONTRACT_NUMBER
  product_type      → PRD_CONTRACT.CONTRACT_TYPE  (raw code)
  contract_type_desc→ GET_ARTICLE_DESC(CONTRACT_TYPE) (human description)
  status            → NULL (PRD_CONTRACT has no STATUS column)
  open_date         → PRD_CONTRACT.START_DATE
  close_date        → PRD_CONTRACT.END_DATE
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


class CustomerContractRepository:

    def get_by_customer(self, db: Session, customer_id: str) -> List[Any]:
        p = _schema_prefix(db)
        sql = text(f"""
            SELECT
                TO_CHAR(cn.ID)          AS id,
                TO_CHAR(cn.CUSTOMER_ID) AS customer_id,
                cn.CONTRACT_NUMBER      AS contract_number,
                cn.CONTRACT_TYPE        AS product_type,
                {p}GET_ARTICLE_DESC(cn.CONTRACT_TYPE) AS contract_type_desc,
                CAST(NULL AS VARCHAR2(1)) AS status,
                cn.START_DATE           AS open_date,
                cn.END_DATE             AS close_date
            FROM {p}PRD_CONTRACT cn
            JOIN {p}PRD_CUSTOMER c ON c.ID = cn.CUSTOMER_ID
            WHERE cn.CUSTOMER_ID = :cid
            ORDER BY cn.START_DATE DESC NULLS LAST
        """)
        return db.execute(sql, {"cid": int(customer_id)}).mappings().all()


customer_contract_repository = CustomerContractRepository()

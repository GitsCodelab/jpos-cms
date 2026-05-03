"""
Customer Repository — Phase 05

Queries against MAIN.PRD_CUSTOMER (Oracle taly-dev-bo connection).

Search joins PRD_CUSTOMER → ISS_CARD → ISS_CARDHOLDER to retrieve the
cardholder name, since PRD_CUSTOMER holds no first/last name columns.

Column aliases in the raw SQL are intentionally mapped to the field names
expected by the service layer (_to_customer_search_result / _to_customer_detail).

Schema prefix is extracted dynamically from the engine's schema_translate_map
execution option so no value is hardcoded here.
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session


def _schema_prefix(db: Session) -> str:
    """Return e.g. 'MAIN.' or '' based on the engine's schema_translate_map."""
    try:
        opts = db.get_bind().get_execution_options()
        schema = (opts.get("schema_translate_map") or {}).get(None) or ""
    except Exception:
        schema = ""
    return f"{schema}." if schema else ""


class CustomerRepository:

    def search(
        self,
        db: Session,
        *,
        q: Optional[str] = None,
        national_id: Optional[str] = None,
        status: Optional[str] = None,
        segment: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> Tuple[List[Any], Optional[int]]:
        """
        Search customers by cardholder name or customer number.

        Returns (items, total). total is None on pages > 1 to avoid double COUNT.
        When no filters are given, returns all customers ordered by name (browse mode).
        Raises ValueError if a filter value is provided but is too short.

        Row objects are aliased to match CustomerSearchResult / CustomerDetailResponse
        field names (id, first_name, national_id, status, segment, created_at).
        """
        for val in filter(None, [q, national_id]):
            if len(val.strip()) < 3:
                raise ValueError("Search input must be at least 3 characters.")

        p = _schema_prefix(db)

        conditions: List[str] = []
        params: Dict[str, Any] = {}

        if q:
            conditions.append("UPPER(ch.CARDHOLDER_NAME) LIKE UPPER(:q)")
            # Support wildcard patterns: *xxx* / xxx* / *xxx  →  %xxx% / xxx% / %xxx
            # If the user typed no * at all, default to contains match (%xxx%)
            raw = q.strip()
            if "*" in raw:
                params["q"] = raw.replace("*", "%")
            else:
                params["q"] = f"%{raw}%"

        if national_id:
            conditions.append("c.CUSTOMER_NUMBER = :cust_num")
            params["cust_num"] = national_id.strip()

        if status:
            conditions.append("c.STATUS = :cust_status")
            params["cust_status"] = status

        if segment:
            conditions.append("c.CATEGORY = :category")
            params["category"] = segment

        where_sql = ("AND " + " AND ".join(conditions)) if conditions else ""

        # COUNT on page 1 only
        total: Optional[int] = None
        if page == 1:
            count_sql = text(f"""
                SELECT COUNT(DISTINCT c.ID)
                FROM {p}PRD_CUSTOMER c
                JOIN {p}ISS_CARD card ON card.CUSTOMER_ID = c.ID
                JOIN {p}ISS_CARDHOLDER ch ON ch.ID = card.CARDHOLDER_ID
                WHERE 1=1 {where_sql}
            """)
            total = db.execute(count_sql, params).scalar() or 0

        capped_page = min(page, 200)
        offset = (capped_page - 1) * page_size
        params["offset"] = offset
        params["page_size"] = page_size

        # Columns aliased to match service-layer expectations:
        #   id          → str(PRD_CUSTOMER.ID)
        #   first_name  → ISS_CARDHOLDER.CARDHOLDER_NAME  (full name)
        #   national_id → PRD_CUSTOMER.CUSTOMER_NUMBER
        #   status      → PRD_CUSTOMER.STATUS
        #   segment     → PRD_CUSTOMER.CATEGORY
        #   created_at  → PRD_CUSTOMER.REG_DATE
        search_sql = text(f"""
            SELECT *
            FROM (
                SELECT
                    TO_CHAR(c.ID) AS id,
                    MIN(ch.CARDHOLDER_NAME) AS first_name,
                    CAST(NULL AS VARCHAR2(1)) AS last_name,
                    c.CUSTOMER_NUMBER AS national_id,
                    CAST(NULL AS VARCHAR2(1)) AS mobile,
                    CAST(NULL AS VARCHAR2(1)) AS email,
                    c.STATUS AS status,
                    c.CATEGORY AS segment,
                    CAST(NULL AS VARCHAR2(1)) AS branch_id,
                    c.REG_DATE AS created_at,
                    MIN(ch.CARDHOLDER_NAME) AS sort_name
                FROM {p}PRD_CUSTOMER c
                JOIN {p}ISS_CARD card ON card.CUSTOMER_ID = c.ID
                JOIN {p}ISS_CARDHOLDER ch ON ch.ID = card.CARDHOLDER_ID
                WHERE 1=1 {where_sql}
                GROUP BY c.ID, c.CUSTOMER_NUMBER, c.STATUS, c.CATEGORY, c.REG_DATE
                ORDER BY sort_name
            )
            OFFSET :offset ROWS FETCH NEXT :page_size ROWS ONLY
        """)
        rows = db.execute(search_sql, params).mappings().all()
        return list(rows), total

    def get_by_id(self, db: Session, customer_id: str) -> Optional[Any]:
        """
        Fetch a single customer by PRD_CUSTOMER.ID.
        Returns a mapping row with the same aliases as search(), or None.
        """
        p = _schema_prefix(db)
        sql = text(f"""
            SELECT
                TO_CHAR(c.ID) AS id,
                MIN(ch.CARDHOLDER_NAME) AS first_name,
                CAST(NULL AS VARCHAR2(1)) AS last_name,
                c.CUSTOMER_NUMBER AS national_id,
                CAST(NULL AS VARCHAR2(1)) AS mobile,
                CAST(NULL AS VARCHAR2(1)) AS email,
                c.STATUS AS status,
                c.CATEGORY AS segment,
                CAST(NULL AS VARCHAR2(1)) AS branch_id,
                c.REG_DATE AS created_at
            FROM {p}PRD_CUSTOMER c
            LEFT JOIN {p}ISS_CARD card ON card.CUSTOMER_ID = c.ID
            LEFT JOIN {p}ISS_CARDHOLDER ch ON ch.ID = card.CARDHOLDER_ID
            WHERE c.ID = :cid
            GROUP BY c.ID, c.CUSTOMER_NUMBER, c.STATUS, c.CATEGORY, c.REG_DATE
            FETCH FIRST 1 ROWS ONLY
        """)
        result = db.execute(sql, {"cid": int(customer_id)}).mappings().first()
        return result


customer_repository = CustomerRepository()

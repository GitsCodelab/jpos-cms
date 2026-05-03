"""
Customer Contact Repository — Phase 05

Contact linkage to PRD_CUSTOMER is not yet established in the taly-dev-bo schema.
Returns empty list until the correct join path is confirmed with the DBA.
"""

from typing import Any, List

from sqlalchemy.orm import Session


class CustomerContactRepository:

    def get_by_customer(self, db: Session, customer_id: str) -> List[Any]:
        return []


customer_contact_repository = CustomerContactRepository()

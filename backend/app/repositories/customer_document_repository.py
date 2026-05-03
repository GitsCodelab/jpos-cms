"""
Customer Document Repository — Phase 05

Document linkage to PRD_CUSTOMER is not yet established in the taly-dev-bo schema.
Returns empty list until the correct join path is confirmed with the DBA.
"""

from typing import Any, List

from sqlalchemy.orm import Session


class CustomerDocumentRepository:

    def get_by_customer(self, db: Session, customer_id: str) -> List[Any]:
        return []


customer_document_repository = CustomerDocumentRepository()

"""
Transaction Service

Handles transaction-related business logic:
1. Querying and filtering transactions (by date, amount, currency, status, etc.)
2. Pagination and search
3. Bulk import from external sources
4. Aggregation for reporting
5. Status transitions
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import Transaction, TransactionStatus, TransactionType
from app.repositories.base_repository import BaseRepository


class TransactionService:
    """Transaction service: handles transaction queries, filtering, and management."""

    def __init__(self):
        self.repo = BaseRepository(Transaction)

    def create_transaction(
        self,
        db: Session,
        amount: float,
        currency: str,
        transaction_type: TransactionType,
        external_reference: str,
        transaction_date: datetime,
        description: str = None,
        source_system: str = None,
    ) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            db: Database session
            amount: Transaction amount (must be > 0)
            currency: ISO currency code (USD, EUR, etc.)
            transaction_type: DEBIT or CREDIT
            external_reference: Unique reference from external system
            transaction_date: When transaction occurred
            description: Optional description
            source_system: System where transaction originated (jPOS, SWIFT, etc.)
        
        Returns:
            New Transaction instance (status=NEW)
        """
        transaction = Transaction(
            id=self._generate_id("TXN"),
            amount=amount,
            currency=currency,
            transaction_type=transaction_type,
            external_reference=external_reference,
            transaction_date=transaction_date,
            description=description,
            source_system=source_system,
            status=TransactionStatus.NEW,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    def list_transactions(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[List[Transaction], int]:
        """
        List transactions with optional filtering and pagination.
        
        Supported filters:
        - status: TransactionStatus enum value
        - currency: Currency code
        - transaction_type: DEBIT or CREDIT
        - amount: Single value or {gte, lte, gt, lt} for range
        - created_after: datetime
        - created_before: datetime
        
        Args:
            db: Database session
            skip: Pagination offset
            limit: Pagination limit
            filters: Filter dict
            order_by: Column to sort by (prefix with '-' for DESC, default: '-transaction_date')
        
        Returns:
            Tuple of (transactions list, total count)
        """
        if order_by is None:
            order_by = "-transaction_date"

        # Process filters
        processed_filters = {}
        if filters:
            for key, value in filters.items():
                if key == "created_after":
                    processed_filters["created_at"] = {"gte": value}
                elif key == "created_before":
                    if "created_at" in processed_filters:
                        processed_filters["created_at"]["lte"] = value
                    else:
                        processed_filters["created_at"] = {"lte": value}
                elif key in ["status", "currency", "transaction_type", "amount"]:
                    processed_filters[key] = value

        total = self.repo.count(db, filters=processed_filters)
        transactions = self.repo.list(
            db,
            skip=skip,
            limit=limit,
            filters=processed_filters,
            order_by=order_by,
        )

        return transactions, total

    def search_transactions(
        self,
        db: Session,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Transaction], int]:
        """
        Search transactions by reference or description.
        
        Args:
            db: Database session
            search_term: Term to search for
            skip: Pagination offset
            limit: Pagination limit
        
        Returns:
            Tuple of (matching transactions, total count)
        """
        search_columns = ["external_reference", "description", "source_system"]
        transactions = self.repo.search(
            db,
            search_term=search_term,
            search_columns=search_columns,
            skip=skip,
            limit=limit,
        )
        
        total = len(transactions)  # Note: real implementation would count separately
        return transactions, total

    def get_transaction_by_id(self, db: Session, transaction_id: str) -> Optional[Transaction]:
        """Get a transaction by ID."""
        return self.repo.get(db, transaction_id)

    def get_transaction_by_reference(
        self,
        db: Session,
        external_reference: str,
    ) -> Optional[Transaction]:
        """Get a transaction by external reference (should be unique)."""
        return db.query(Transaction).filter(
            Transaction.external_reference == external_reference
        ).first()

    def bulk_import_transactions(
        self,
        db: Session,
        transactions_data: List[Dict],
        source_system: str = "import",
    ) -> int:
        """
        Bulk import transactions from external source.
        
        High-performance operation for large data loads.
        Uses SQLAlchemy bulk_insert_mappings for efficiency.
        
        Args:
            db: Database session
            transactions_data: List of transaction dicts
            source_system: Source system label
        
        Returns:
            Number of transactions inserted
        
        Example:
            transactions_data = [
                {
                    'amount': 100.00,
                    'currency': 'USD',
                    'transaction_type': 'DEBIT',
                    'external_reference': 'TXN001',
                    'transaction_date': datetime.now(),
                },
                ...
            ]
            count = service.bulk_import_transactions(db, transactions_data)
        """
        # Add required fields
        for txn in transactions_data:
            txn['id'] = self._generate_id("TXN")
            txn['status'] = TransactionStatus.NEW.value
            txn['source_system'] = source_system
            txn['created_at'] = datetime.utcnow()
            txn['updated_at'] = datetime.utcnow()

        # Use bulk insert for performance
        db.bulk_insert_mappings(Transaction, transactions_data)
        db.commit()

        return len(transactions_data)

    def get_transaction_summary(
        self,
        db: Session,
        filters: Optional[Dict] = None,
    ) -> Dict:
        """
        Get aggregated transaction summary (for dashboard).
        
        Returns totals by type and status.
        
        Args:
            db: Database session
            filters: Optional filters to apply
        
        Returns:
            Dict with summary metrics
        """
        # Base queries
        query = db.query(Transaction)
        if filters:
            for key, value in filters.items():
                if key == "currency" and hasattr(Transaction, key):
                    query = query.filter(getattr(Transaction, key) == value)

        total_transactions = query.count()
        total_amount = self.repo.aggregate(
            db, "sum", "amount", filters=filters or {}
        ) or 0.0

        # By status
        by_status = {}
        for status in TransactionStatus:
            count = query.filter(Transaction.status == status).count()
            if count > 0:
                by_status[status.value] = count

        # By type
        by_type = {}
        for txn_type in TransactionType:
            count = query.filter(Transaction.transaction_type == txn_type).count()
            if count > 0:
                by_type[txn_type.value] = count

        return {
            "total_transactions": total_transactions,
            "total_amount": float(total_amount),
            "by_status": by_status,
            "by_type": by_type,
        }

    def update_transaction_status(
        self,
        db: Session,
        transaction_id: str,
        new_status: TransactionStatus,
    ) -> Optional[Transaction]:
        """
        Update transaction status (e.g., NEW → MATCHED → RESOLVED).
        
        Args:
            db: Database session
            transaction_id: Transaction ID
            new_status: New status value
        
        Returns:
            Updated transaction or None if not found
        """
        transaction = self.repo.get(db, transaction_id)
        if not transaction:
            return None

        transaction.status = new_status
        transaction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(transaction)
        return transaction

    def get_transactions_by_date_range(
        self,
        db: Session,
        date_from: datetime,
        date_to: datetime,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Transaction], int]:
        """
        Get transactions within a date range (common for reconciliation).
        
        Args:
            db: Database session
            date_from: Start datetime
            date_to: End datetime
            skip: Pagination offset
            limit: Pagination limit
        
        Returns:
            Tuple of (transactions, total count)
        """
        transactions = self.repo.filter_by_date_range(
            db,
            date_column="transaction_date",
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit,
        )

        total = db.query(Transaction).filter(
            Transaction.transaction_date >= date_from,
            Transaction.transaction_date <= date_to,
        ).count()

        return transactions, total

    @staticmethod
    def _generate_id(prefix: str) -> str:
        """Generate unique ID with prefix."""
        import uuid

        return f"{prefix}-{uuid.uuid4().hex[:12]}"

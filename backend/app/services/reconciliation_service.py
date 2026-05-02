"""
Reconciliation Service

Handles the core reconciliation logic:
1. Matching transactions between sources
2. Identifying unmatches
3. State machine management (PENDING → IN_PROGRESS → MATCHED/UNMATCHED → RESOLVED)
4. Tolerance-based fuzzy matching for financial data

This service is the business logic heart of the CMS platform.
"""

from datetime import datetime, timedelta
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models import (
    ReconciliationRun,
    ReconciliationStatus,
    ReconciliationUnmatch,
    Transaction,
    TransactionStatus,
)
from app.repositories.base_repository import BaseRepository


class ReconciliationService:
    """
    Reconciliation service: matches transactions across sources.
    
    Matching algorithm:
    1. For each transaction in source A
    2. Find potential matches in source B (within date/amount tolerance)
    3. Mark as MATCHED if found, UNMATCHED if not
    4. Create ReconciliationUnmatch records for investigation
    5. Update ReconciliationRun with counts
    """

    def __init__(self):
        self.repo = BaseRepository(ReconciliationRun)
        self.transaction_repo = BaseRepository(Transaction)
        self.unmatch_repo = BaseRepository(ReconciliationUnmatch)

    def create_run(
        self,
        db: Session,
        settlement_period: str,
        amount_tolerance: float = 0.01,
        date_tolerance_days: int = 1,
        notes: str = None,
        created_by: str = "system",
    ) -> ReconciliationRun:
        """
        Create a new reconciliation run.
        
        Args:
            db: Database session
            settlement_period: Period being reconciled (e.g., "2026-05-01")
            amount_tolerance: Max amount difference in cents (default: $0.01)
            date_tolerance_days: Max date difference in days (default: 1 day)
            notes: Optional notes about the run
            created_by: User creating the run
        
        Returns:
            New ReconciliationRun instance (status=PENDING)
        """
        run = ReconciliationRun(
            id=self._generate_id("RECON"),
            run_date=datetime.utcnow(),
            settlement_period=settlement_period,
            status=ReconciliationStatus.PENDING,
            amount_tolerance=amount_tolerance,
            date_tolerance_days=date_tolerance_days,
            notes=notes,
            created_by=created_by,
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    def start_reconciliation(self, db: Session, run_id: str) -> ReconciliationRun:
        """
        Start the reconciliation process (move from PENDING to IN_PROGRESS).
        
        Args:
            db: Database session
            run_id: ID of reconciliation run to start
        
        Returns:
            Updated ReconciliationRun
        """
        run = self.repo.get(db, run_id)
        if not run:
            raise ValueError(f"Reconciliation run {run_id} not found")

        if run.status != ReconciliationStatus.PENDING:
            raise ValueError(
                f"Can only start reconciliation from PENDING status, current: {run.status}"
            )

        run.status = ReconciliationStatus.IN_PROGRESS
        db.commit()
        db.refresh(run)
        return run

    def match_transactions(self, db: Session, run_id: str) -> ReconciliationRun:
        """
        Match transactions for a reconciliation run.
        
        Algorithm:
        1. Get all transactions for this settlement period
        2. For each transaction, find potential matches (amount ± tolerance, date ± tolerance)
        3. Mark MATCHED transactions
        4. Create UNMATCHED records for unmatched transactions
        
        Args:
            db: Database session
            run_id: ID of reconciliation run
        
        Returns:
            Updated ReconciliationRun with match counts
        """
        run = self.repo.get(db, run_id)
        if not run:
            raise ValueError(f"Reconciliation run {run_id} not found")

        # Get all transactions for this settlement period
        transactions = db.query(Transaction).filter(
            Transaction.settlement_batch_id.isnull() | (
                Transaction.settlement_batch_id.is_(None)
            ),
            Transaction.reconciliation_run_id.is_(None),
        ).all()

        matched_count = 0
        unmatched_count = 0
        error_count = 0

        # Matching logic (simplified - real implementation would compare with external source)
        for transaction in transactions:
            try:
                # Find potential matches in the same period with similar amount/date
                potential_matches = db.query(Transaction).filter(
                    Transaction.id != transaction.id,
                    Transaction.settlement_batch_id == transaction.settlement_batch_id,
                    Transaction.amount >= transaction.amount - run.amount_tolerance,
                    Transaction.amount <= transaction.amount + run.amount_tolerance,
                    Transaction.transaction_date >= transaction.transaction_date - timedelta(
                        days=run.date_tolerance_days
                    ),
                    Transaction.transaction_date <= transaction.transaction_date + timedelta(
                        days=run.date_tolerance_days
                    ),
                ).all()

                if potential_matches:
                    # Mark as matched
                    transaction.status = TransactionStatus.MATCHED
                    transaction.reconciliation_run_id = run_id
                    matched_count += 1
                else:
                    # Create unmatch record
                    transaction.status = TransactionStatus.UNMATCHED
                    transaction.reconciliation_run_id = run_id
                    unmatched_count += 1

                    unmatch = ReconciliationUnmatch(
                        id=self._generate_id("UNMATCH"),
                        reconciliation_run_id=run_id,
                        transaction_id=transaction.id,
                        reason="No matching transaction found",
                        resolution_status="PENDING",
                    )
                    db.add(unmatch)

                db.commit()

            except Exception as e:
                error_count += 1
                print(f"Error matching transaction {transaction.id}: {str(e)}")

        # Update run with results
        run.matched_count = matched_count
        run.unmatched_count = unmatched_count
        run.error_count = error_count
        run.status = (
            ReconciliationStatus.MATCHED
            if unmatched_count == 0
            else ReconciliationStatus.UNMATCHED
        )
        db.commit()
        db.refresh(run)

        return run

    def resolve_unmatches(
        self,
        db: Session,
        run_id: str,
        unmatch_id: str,
        resolution_status: str,
        resolved_by: str = "system",
    ) -> ReconciliationUnmatch:
        """
        Resolve an unmatched transaction (mark as RESOLVED or ESCALATED).
        
        Args:
            db: Database session
            run_id: ID of reconciliation run
            unmatch_id: ID of unmatch to resolve
            resolution_status: 'RESOLVED' or 'ESCALATED'
            resolved_by: User resolving the unmatch
        
        Returns:
            Updated ReconciliationUnmatch
        """
        unmatch = self.unmatch_repo.get(db, unmatch_id)
        if not unmatch:
            raise ValueError(f"Unmatch {unmatch_id} not found")

        unmatch.resolution_status = resolution_status
        unmatch.resolved_at = datetime.utcnow()
        unmatch.resolved_by = resolved_by
        db.commit()
        db.refresh(unmatch)

        return unmatch

    def complete_reconciliation(self, db: Session, run_id: str) -> ReconciliationRun:
        """
        Mark reconciliation as RESOLVED (all unmatches handled or escalated).
        
        Args:
            db: Database session
            run_id: ID of reconciliation run
        
        Returns:
            Updated ReconciliationRun (status=RESOLVED)
        """
        run = self.repo.get(db, run_id)
        if not run:
            raise ValueError(f"Reconciliation run {run_id} not found")

        run.status = ReconciliationStatus.RESOLVED
        run.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(run)

        return run

    def get_unmatches(
        self,
        db: Session,
        run_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[ReconciliationUnmatch], int]:
        """
        Get unmatched transactions for a reconciliation run.
        
        Args:
            db: Database session
            run_id: ID of reconciliation run
            skip: Pagination offset
            limit: Pagination limit
        
        Returns:
            Tuple of (unmatches list, total count)
        """
        total = (
            db.query(ReconciliationUnmatch)
            .filter(ReconciliationUnmatch.reconciliation_run_id == run_id)
            .count()
        )

        unmatches = (
            db.query(ReconciliationUnmatch)
            .filter(ReconciliationUnmatch.reconciliation_run_id == run_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return unmatches, total

    @staticmethod
    def _generate_id(prefix: str) -> str:
        """Generate unique ID with prefix."""
        import uuid

        return f"{prefix}-{uuid.uuid4().hex[:12]}"

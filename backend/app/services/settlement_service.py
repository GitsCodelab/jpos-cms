"""
Settlement Service

Handles settlement batch and statement operations:
1. Create settlement batches (group transactions for settlement)
2. Calculate NET settlement (debit - credit per currency)
3. Generate settlement statements
4. Track settlement lifecycle (DRAFT → FINALIZED → APPROVED)
5. Support daily settlement reconciliation
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    SettlementBatch,
    SettlementStatus,
    SettlementStatement,
    Transaction,
    TransactionType,
)
from app.repositories.base_repository import BaseRepository


class SettlementService:
    """Settlement service: manages settlement batches and statements."""

    def __init__(self):
        self.batch_repo = BaseRepository(SettlementBatch)
        self.statement_repo = BaseRepository(SettlementStatement)

    def create_batch(
        self,
        db: Session,
        settlement_period: str,
        currency: str,
        notes: str = None,
    ) -> SettlementBatch:
        """
        Create a new settlement batch.
        
        Args:
            db: Database session
            settlement_period: Period (e.g., "2026-05-01")
            currency: ISO currency code (USD, EUR, etc.)
            notes: Optional notes
        
        Returns:
            New SettlementBatch instance (status=DRAFT)
        """
        batch = SettlementBatch(
            id=self._generate_id("BATCH"),
            batch_date=datetime.utcnow(),
            settlement_period=settlement_period,
            currency=currency,
            status=SettlementStatus.DRAFT,
            notes=notes,
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
        return batch

    def add_transactions_to_batch(
        self,
        db: Session,
        batch_id: str,
        transaction_ids: List[str],
    ) -> SettlementBatch:
        """
        Add transactions to a settlement batch.
        
        Automatically calculates totals and NET settlement.
        
        Args:
            db: Database session
            batch_id: Batch ID
            transaction_ids: List of transaction IDs to add
        
        Returns:
            Updated SettlementBatch with calculated totals
        """
        batch = self.batch_repo.get(db, batch_id)
        if not batch:
            raise ValueError(f"Batch {batch_id} not found")

        # Update transactions and recalculate batch totals
        transactions = (
            db.query(Transaction)
            .filter(Transaction.id.in_(transaction_ids))
            .all()
        )

        total_amount = 0.0
        debit_total = 0.0
        credit_total = 0.0

        for txn in transactions:
            txn.settlement_batch_id = batch_id
            total_amount += txn.amount

            if txn.transaction_type == TransactionType.DEBIT:
                debit_total += txn.amount
            else:
                credit_total += txn.amount

        # Update batch totals
        batch.total_amount = total_amount
        batch.transaction_count = len(transactions)
        batch.debit_amount = debit_total
        batch.credit_amount = credit_total
        batch.net_amount = abs(debit_total - credit_total)
        batch.net_direction = "DEBIT" if debit_total > credit_total else "CREDIT"

        db.commit()
        db.refresh(batch)

        return batch

    def finalize_batch(
        self,
        db: Session,
        batch_id: str,
        reference: str = None,
    ) -> SettlementBatch:
        """
        Finalize settlement batch (move from DRAFT to FINALIZED).
        
        Args:
            db: Database session
            batch_id: Batch ID
            reference: Settlement reference number
        
        Returns:
            Updated SettlementBatch (status=FINALIZED)
        """
        batch = self.batch_repo.get(db, batch_id)
        if not batch:
            raise ValueError(f"Batch {batch_id} not found")

        batch.status = SettlementStatus.FINALIZED
        batch.finalized_at = datetime.utcnow()
        if reference:
            batch.reference = reference

        db.commit()
        db.refresh(batch)

        return batch

    def create_statement(
        self,
        db: Session,
        settlement_period: str,
        prepared_by: str = "system",
    ) -> SettlementStatement:
        """
        Create settlement statement (summary of all batches for period).
        
        Aggregates all finalized batches in the period.
        
        Args:
            db: Database session
            settlement_period: Settlement period (e.g., "2026-05-01")
            prepared_by: User preparing statement
        
        Returns:
            New SettlementStatement
        """
        # Get all finalized batches for period
        batches = (
            db.query(SettlementBatch)
            .filter(
                SettlementBatch.settlement_period == settlement_period,
                SettlementBatch.status == SettlementStatus.FINALIZED,
            )
            .all()
        )

        # Aggregate totals
        total_transactions = sum(b.transaction_count for b in batches)
        total_amount = sum(b.total_amount for b in batches)
        total_debit = sum(b.debit_amount for b in batches)
        total_credit = sum(b.credit_amount for b in batches)
        net_settlement = abs(total_debit - total_credit)

        statement = SettlementStatement(
            id=self._generate_id("STMT"),
            statement_date=datetime.utcnow(),
            settlement_period=settlement_period,
            status=SettlementStatus.DRAFT,
            total_transactions=total_transactions,
            total_amount=total_amount,
            total_debit_amount=total_debit,
            total_credit_amount=total_credit,
            net_settlement=net_settlement,
            prepared_by=prepared_by,
        )

        db.add(statement)
        db.commit()
        db.refresh(statement)

        return statement

    def approve_statement(
        self,
        db: Session,
        statement_id: str,
        approved_by: str = "system",
    ) -> SettlementStatement:
        """
        Approve settlement statement.
        
        Args:
            db: Database session
            statement_id: Statement ID
            approved_by: User approving
        
        Returns:
            Updated SettlementStatement (status=APPROVED)
        """
        statement = self.statement_repo.get(db, statement_id)
        if not statement:
            raise ValueError(f"Statement {statement_id} not found")

        statement.status = SettlementStatus.APPROVED
        statement.approved_by = approved_by
        statement.approved_at = datetime.utcnow()
        statement.finalized_at = datetime.utcnow()

        db.commit()
        db.refresh(statement)

        return statement

    def get_daily_net_settlement(
        self,
        db: Session,
        settlement_date: str,
    ) -> List[Dict]:
        """
        Get NET settlement positions for a date (by currency).
        
        Returns list of currencies with debit/credit totals and NET amount.
        
        Args:
            db: Database session
            settlement_date: Date to summarize (YYYY-MM-DD format)
        
        Returns:
            List of dicts with currency, debit_total, credit_total, net_amount
        """
        # Group by currency and sum debits/credits
        result = (
            db.query(
                SettlementBatch.currency,
                func.sum(SettlementBatch.debit_amount).label("debit_total"),
                func.sum(SettlementBatch.credit_amount).label("credit_total"),
                func.count(SettlementBatch.id).label("batch_count"),
            )
            .filter(SettlementBatch.settlement_period == settlement_date)
            .group_by(SettlementBatch.currency)
            .all()
        )

        positions = []
        for currency, debit, credit, count in result:
            net = abs((debit or 0) - (credit or 0))
            direction = "DEBIT" if (debit or 0) > (credit or 0) else "CREDIT"

            positions.append({
                "currency": currency,
                "debit_total": float(debit or 0),
                "credit_total": float(credit or 0),
                "net_amount": float(net),
                "net_direction": direction,
                "batch_count": count,
            })

        return positions

    def list_batches(
        self,
        db: Session,
        settlement_period: Optional[str] = None,
        status: Optional[SettlementStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[SettlementBatch], int]:
        """
        List settlement batches with optional filtering.
        
        Args:
            db: Database session
            settlement_period: Filter by period
            status: Filter by status
            skip: Pagination offset
            limit: Pagination limit
        
        Returns:
            Tuple of (batches, total count)
        """
        filters = {}
        if settlement_period:
            filters["settlement_period"] = settlement_period
        if status:
            filters["status"] = status

        total = self.batch_repo.count(db, filters=filters)
        batches = self.batch_repo.list(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="-batch_date",
        )

        return batches, total

    @staticmethod
    def _generate_id(prefix: str) -> str:
        """Generate unique ID with prefix."""
        import uuid

        return f"{prefix}-{uuid.uuid4().hex[:12]}"

"""
Fraud Monitoring Service

Handles fraud detection and alert management:
1. Rule-based fraud detection (declarative rules)
2. Risk score calculation (sum of triggered rule weights)
3. Alert lifecycle (PENDING → REVIEWED → APPROVED/REJECTED)
4. Real-time alert generation on transaction creation
5. Webhook notifications to external fraud systems
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import (
    FraudAlert,
    FraudAlertStatus,
    FraudRiskLevel,
    FraudRule,
    Transaction,
)
from app.repositories.base_repository import BaseRepository


class FraudService:
    """Fraud service: detects and manages fraud alerts."""

    def __init__(self):
        self.alert_repo = BaseRepository(FraudAlert)
        self.rule_repo = BaseRepository(FraudRule)

    def create_rule(
        self,
        db: Session,
        name: str,
        condition: str,
        weight: float = 10.0,
        description: str = None,
        enabled: bool = True,
        priority: int = 0,
        created_by: str = "system",
    ) -> FraudRule:
        """
        Create a new fraud detection rule.
        
        Args:
            db: Database session
            name: Rule name (unique)
            condition: Condition expression (e.g., "amount > 100000")
            weight: Contribution to risk score (0-100)
            description: Rule description
            enabled: Whether rule is active
            priority: Execution priority (higher first)
            created_by: User creating rule
        
        Returns:
            New FraudRule instance
        """
        rule = FraudRule(
            id=self._generate_id("RULE"),
            name=name,
            description=description,
            condition=condition,
            weight=weight,
            enabled=enabled,
            priority=priority,
            created_by=created_by,
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule

    def evaluate_transaction(
        self,
        db: Session,
        transaction: Transaction,
    ) -> FraudAlert:
        """
        Evaluate a transaction against fraud rules and create alert if triggered.
        
        Algorithm:
        1. Get all enabled fraud rules (ordered by priority)
        2. Evaluate transaction against each rule
        3. Sum weights of triggered rules → risk_score
        4. Classify risk (LOW 0-33, MEDIUM 34-66, HIGH 67-100)
        5. Create FraudAlert if score > 0
        
        Args:
            db: Database session
            transaction: Transaction to evaluate
        
        Returns:
            FraudAlert instance (may have score=0 if no rules triggered)
        """
        rules = (
            db.query(FraudRule)
            .filter(FraudRule.enabled == True)
            .order_by(FraudRule.priority.desc())
            .all()
        )

        triggered_rules = []
        total_risk_score = 0.0

        for rule in rules:
            try:
                # Simple condition evaluation (in production, use sandboxed evaluator)
                if self._evaluate_condition(rule.condition, transaction):
                    triggered_rules.append(rule.id)
                    total_risk_score += rule.weight
            except Exception as e:
                print(f"Error evaluating rule {rule.id}: {str(e)}")

        # Cap risk score at 100
        risk_score = min(total_risk_score, 100.0)

        # Classify risk level
        if risk_score == 0:
            risk_level = FraudRiskLevel.LOW
        elif risk_score < 34:
            risk_level = FraudRiskLevel.LOW
        elif risk_score < 67:
            risk_level = FraudRiskLevel.MEDIUM
        else:
            risk_level = FraudRiskLevel.HIGH

        # Create alert
        alert = FraudAlert(
            id=self._generate_id("ALERT"),
            transaction_id=transaction.id,
            risk_score=risk_score,
            risk_level=risk_level,
            triggered_rules=json.dumps(triggered_rules),
            status=FraudAlertStatus.PENDING,
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        return alert

    def list_alerts(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[FraudAlertStatus] = None,
        risk_level: Optional[FraudRiskLevel] = None,
        order_by: str = "-alert_date",
    ) -> Tuple[List[FraudAlert], int]:
        """
        List fraud alerts with optional filtering.
        
        Args:
            db: Database session
            skip: Pagination offset
            limit: Pagination limit
            status: Filter by alert status
            risk_level: Filter by risk level
            order_by: Sort column (default: -alert_date for newest first)
        
        Returns:
            Tuple of (alerts list, total count)
        """
        filters = {}
        if status:
            filters["status"] = status
        if risk_level:
            filters["risk_level"] = risk_level

        total = self.alert_repo.count(db, filters=filters)
        alerts = self.alert_repo.list(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=order_by,
        )

        return alerts, total

    def review_alert(
        self,
        db: Session,
        alert_id: str,
        decision: FraudAlertStatus,
        comment: str = None,
        reviewed_by: str = "system",
    ) -> FraudAlert:
        """
        Review and make decision on fraud alert.
        
        Args:
            db: Database session
            alert_id: Alert ID
            decision: APPROVED or REJECTED
            comment: Review comment
            reviewed_by: User making decision
        
        Returns:
            Updated FraudAlert
        """
        alert = self.alert_repo.get(db, alert_id)
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        if decision not in [FraudAlertStatus.APPROVED, FraudAlertStatus.REJECTED]:
            raise ValueError(f"Invalid decision: {decision}")

        alert.status = decision
        alert.reviewed_at = datetime.utcnow()
        alert.reviewed_by = reviewed_by
        alert.resolution_comment = comment

        db.commit()
        db.refresh(alert)

        return alert

    def get_fraud_summary(self, db: Session) -> Dict:
        """
        Get fraud summary for dashboard.
        
        Returns:
            Dict with fraud metrics
        """
        total_alerts = db.query(FraudAlert).count()
        pending_alerts = db.query(FraudAlert).filter(
            FraudAlert.status == FraudAlertStatus.PENDING
        ).count()

        high_risk = db.query(FraudAlert).filter(
            FraudAlert.risk_level == FraudRiskLevel.HIGH
        ).count()
        medium_risk = db.query(FraudAlert).filter(
            FraudAlert.risk_level == FraudRiskLevel.MEDIUM
        ).count()
        low_risk = db.query(FraudAlert).filter(
            FraudAlert.risk_level == FraudRiskLevel.LOW
        ).count()

        avg_score = db.query(FraudAlert).count()
        if avg_score > 0:
            from sqlalchemy import func

            avg_score = db.query(func.avg(FraudAlert.risk_score)).scalar() or 0.0

        return {
            "total_alerts": total_alerts,
            "pending_alerts": pending_alerts,
            "high_risk_count": high_risk,
            "medium_risk_count": medium_risk,
            "low_risk_count": low_risk,
            "average_risk_score": float(avg_score),
        }

    @staticmethod
    def _evaluate_condition(condition: str, transaction: Transaction) -> bool:
        """
        Evaluate fraud rule condition against transaction.
        
        CAUTION: In production, use a sandboxed expression evaluator (RestrictedPython, etc.)
        
        Supported conditions:
        - amount > 100000
        - amount <= 500
        - transaction_type == "DEBIT"
        - currency != "USD"
        - (amount > 100000 AND transaction_type == "CREDIT")
        
        Args:
            condition: Condition string
            transaction: Transaction to evaluate
        
        Returns:
            True if condition is met, False otherwise
        """
        try:
            # Safe context for evaluation
            safe_dict = {
                "amount": transaction.amount,
                "transaction_type": transaction.transaction_type.value,
                "currency": transaction.currency,
                "source_system": transaction.source_system or "",
            }

            # Simple condition evaluation (production: use RestrictedPython)
            result = eval(condition, {"__builtins__": {}}, safe_dict)
            return bool(result)
        except Exception:
            return False

    @staticmethod
    def _generate_id(prefix: str) -> str:
        """Generate unique ID with prefix."""
        import uuid

        return f"{prefix}-{uuid.uuid4().hex[:12]}"

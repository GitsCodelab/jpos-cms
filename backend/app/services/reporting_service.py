"""
Reporting Service

Handles asynchronous report generation:
1. Create report jobs (returns immediately, processes in background)
2. Track job status (PENDING → PROCESSING → COMPLETED/FAILED)
3. Multiple export formats (PDF, CSV, Excel, JSON)
4. Scheduled report cleanup (retention policy)
5. Report parameterization (date ranges, filters, etc.)

In production: use Celery or RQ for async task processing.
For MVP: synchronous processing (background via FastAPI BackgroundTask).
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import ReportFormat, ReportJob, ReportStatus


class ReportingService:
    """Reporting service: manages async report generation jobs."""

    def __init__(self):
        pass

    def create_report_job(
        self,
        db: Session,
        report_type: str,
        format: ReportFormat = ReportFormat.PDF,
        settlement_period: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        filters: Optional[Dict] = None,
        requested_by: str = "system",
    ) -> ReportJob:
        """
        Create a report generation job.
        
        Job starts in PENDING state and can be picked up by background worker.
        
        Args:
            db: Database session
            report_type: Type of report (reconciliation, settlement, fraud, etc.)
            format: Export format (PDF, CSV, EXCEL, JSON)
            settlement_period: Optional period filter
            date_from: Optional date range start
            date_to: Optional date range end
            filters: Optional additional filters (JSON dict)
            requested_by: User requesting report
        
        Returns:
            New ReportJob instance (status=PENDING)
        """
        job = ReportJob(
            id=self._generate_id("JOB"),
            report_type=report_type,
            settlement_period=settlement_period,
            date_from=date_from,
            date_to=date_to,
            filters=json.dumps(filters) if filters else None,
            format=format,
            status=ReportStatus.PENDING,
            requested_by=requested_by,
            expires_at=datetime.utcnow() + timedelta(days=30),  # Auto-cleanup
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        return job

    def start_job(self, db: Session, job_id: str) -> ReportJob:
        """
        Mark job as PROCESSING (background task started).
        
        Args:
            db: Database session
            job_id: Job ID
        
        Returns:
            Updated ReportJob
        """
        job = self._get_job(db, job_id)
        job.status = ReportStatus.PROCESSING
        job.started_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
        return job

    def complete_job(
        self,
        db: Session,
        job_id: str,
        file_path: str,
        file_size_bytes: int,
    ) -> ReportJob:
        """
        Mark job as COMPLETED with file path.
        
        Args:
            db: Database session
            job_id: Job ID
            file_path: Path to generated report file
            file_size_bytes: Size of file in bytes
        
        Returns:
            Updated ReportJob (status=COMPLETED)
        """
        job = self._get_job(db, job_id)
        job.status = ReportStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.file_path = file_path
        job.file_size_bytes = file_size_bytes
        db.commit()
        db.refresh(job)
        return job

    def fail_job(
        self,
        db: Session,
        job_id: str,
        error_message: str,
    ) -> ReportJob:
        """
        Mark job as FAILED with error message.
        
        Args:
            db: Database session
            job_id: Job ID
            error_message: Error details
        
        Returns:
            Updated ReportJob (status=FAILED)
        """
        job = self._get_job(db, job_id)
        job.status = ReportStatus.FAILED
        job.completed_at = datetime.utcnow()
        job.error_message = error_message
        db.commit()
        db.refresh(job)
        return job

    def get_job(self, db: Session, job_id: str) -> Optional[ReportJob]:
        """Get report job by ID."""
        return db.query(ReportJob).filter(ReportJob.id == job_id).first()

    def list_jobs(
        self,
        db: Session,
        report_type: Optional[str] = None,
        status: Optional[ReportStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[ReportJob], int]:
        """
        List report jobs with optional filtering.
        
        Args:
            db: Database session
            report_type: Filter by report type
            status: Filter by status
            skip: Pagination offset
            limit: Pagination limit
        
        Returns:
            Tuple of (jobs list, total count)
        """
        query = db.query(ReportJob)

        if report_type:
            query = query.filter(ReportJob.report_type == report_type)
        if status:
            query = query.filter(ReportJob.status == status)

        total = query.count()
        jobs = query.order_by(ReportJob.created_at.desc()).offset(skip).limit(limit).all()

        return jobs, total

    def cleanup_expired_jobs(self, db: Session) -> int:
        """
        Delete expired report jobs (older than retention period).
        
        Configured via REPORT_RETENTION_DAYS environment variable.
        Should run daily via scheduled task (Celery beat, APScheduler, etc.)
        
        Args:
            db: Database session
        
        Returns:
            Number of jobs deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=30)  # Default 30 days
        jobs_to_delete = db.query(ReportJob).filter(
            ReportJob.expires_at < cutoff_date
        ).all()

        count = len(jobs_to_delete)
        for job in jobs_to_delete:
            db.delete(job)

        db.commit()
        return count

    def _get_job(self, db: Session, job_id: str) -> ReportJob:
        """Get job or raise error if not found."""
        job = self.get_job(db, job_id)
        if not job:
            raise ValueError(f"Report job {job_id} not found")
        return job

    @staticmethod
    def _generate_id(prefix: str) -> str:
        """Generate unique ID with prefix."""
        import uuid

        return f"{prefix}-{uuid.uuid4().hex[:12]}"


# ============================================================================
# REPORT GENERATORS (Business Logic)
# ============================================================================


class ReconciliationReportGenerator:
    """Generate reconciliation report from database data."""

    @staticmethod
    def generate(db: Session, settlement_period: str, format: str) -> str:
        """
        Generate reconciliation report for period.
        
        Returns: file_path where report is saved
        """
        # Implementation: fetch reconciliation data, format and save
        # For now: return placeholder
        return f"/tmp/report_reconciliation_{settlement_period}.{format.lower()}"


class SettlementReportGenerator:
    """Generate settlement statement report."""

    @staticmethod
    def generate(db: Session, settlement_period: str, format: str) -> str:
        """
        Generate settlement statement for period.
        
        Returns: file_path where report is saved
        """
        return f"/tmp/report_settlement_{settlement_period}.{format.lower()}"


class FraudReportGenerator:
    """Generate fraud summary report."""

    @staticmethod
    def generate(
        db: Session,
        date_from: datetime,
        date_to: datetime,
        format: str,
    ) -> str:
        """
        Generate fraud summary for date range.
        
        Returns: file_path where report is saved
        """
        start_str = date_from.strftime("%Y%m%d")
        end_str = date_to.strftime("%Y%m%d")
        return f"/tmp/report_fraud_{start_str}_{end_str}.{format.lower()}"

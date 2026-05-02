"""
Base Repository Pattern for generic CRUD operations.

This abstract base class provides common database operations that work
with any SQLAlchemy model, enabling code reuse across all repositories.

Pattern:
- One repository per domain entity (TransactionRepository, ReconciliationRepository, etc.)
- Each repository inherits from BaseRepository
- Services use repositories for data access (decoupled from ORM)
- Supports filtering, pagination, and bulk operations

Benefits:
- Consistent query patterns across the application
- Easy to switch databases (PostgreSQL → Oracle) without changing service code
- Testable: mock repositories in unit tests
- Scalable: add caching, sharding logic in repository layer
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD repository for any SQLAlchemy model.
    
    Subclass this for domain-specific repositories with additional methods.
    
    Example:
        class TransactionRepository(BaseRepository[Transaction, TransactionCreate, TransactionUpdate]):
            pass
        
        repo = TransactionRepository(Transaction)
        transaction = repo.create(db, obj_in=TransactionCreate(...))
        transactions = repo.list(db, skip=0, limit=100)
    """

    def __init__(self, model: Type[ModelType]):
        """Initialize repository with SQLAlchemy model class."""
        self.model = model

    def create(
        self,
        db: Session,
        obj_in: CreateSchemaType,
        **kwargs,
    ) -> ModelType:
        """Create a new record in database."""
        db_obj = self.model(**obj_in.dict(), **kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a record by primary key."""
        return db.query(self.model).filter(self.model.id == id).first()

    def list(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> List[ModelType]:
        """
        List records with optional filtering and pagination.
        
        Args:
            db: SQLAlchemy session
            skip: Offset for pagination
            limit: Max records to return
            filters: Dict of {column_name: value} for WHERE clause
            order_by: Column name to sort by (prefix with '-' for DESC)
        
        Returns:
            List of model instances
        """
        query = db.query(self.model)

        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    column = getattr(self.model, key)
                    if isinstance(value, list):
                        query = query.filter(column.in_(value))
                    elif isinstance(value, dict):
                        # Handle range filters: {"gte": 100, "lte": 500}
                        if "gte" in value:
                            query = query.filter(column >= value["gte"])
                        if "lte" in value:
                            query = query.filter(column <= value["lte"])
                        if "gt" in value:
                            query = query.filter(column > value["gt"])
                        if "lt" in value:
                            query = query.filter(column < value["lt"])
                    else:
                        query = query.filter(column == value)

        # Apply ordering
        if order_by:
            if order_by.startswith("-"):
                query = query.order_by(desc(getattr(self.model, order_by[1:])))
            else:
                query = query.order_by(getattr(self.model, order_by))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        return query.all()

    def count(
        self,
        db: Session,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Count records matching filters."""
        query = db.query(func.count(self.model.id))

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    column = getattr(self.model, key)
                    if isinstance(value, list):
                        query = query.filter(column.in_(value))
                    else:
                        query = query.filter(column == value)

        return query.scalar() or 0

    def update(
        self,
        db: Session,
        id: Any,
        obj_in: UpdateSchemaType,
    ) -> Optional[ModelType]:
        """Update a record by primary key."""
        db_obj = self.get(db, id)
        if not db_obj:
            return None

        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: Any) -> bool:
        """Delete a record by primary key."""
        db_obj = self.get(db, id)
        if not db_obj:
            return False

        db.delete(db_obj)
        db.commit()
        return True

    def bulk_create(
        self,
        db: Session,
        objects: List[CreateSchemaType],
    ) -> int:
        """
        Create multiple records efficiently.
        
        For Oracle: uses bulk_insert_mappings for better performance on large inserts.
        
        Args:
            db: SQLAlchemy session
            objects: List of create schemas
        
        Returns:
            Number of records inserted
        """
        if not objects:
            return 0

        # Convert schemas to dict for bulk insert
        mappings = [obj.dict() for obj in objects]
        db.bulk_insert_mappings(self.model, mappings)
        db.commit()
        return len(mappings)

    def bulk_update(
        self,
        db: Session,
        updates: List[Dict[str, Any]],
    ) -> int:
        """
        Update multiple records.
        
        Each dict in updates must have 'id' key plus fields to update.
        
        Args:
            db: SQLAlchemy session
            updates: List of dicts with id and fields to update
        
        Returns:
            Number of records updated
        """
        count = 0
        for update_dict in updates:
            record_id = update_dict.pop("id")
            db_obj = self.get(db, record_id)
            if db_obj:
                for key, value in update_dict.items():
                    setattr(db_obj, key, value)
                db.add(db_obj)
                count += 1

        if count > 0:
            db.commit()

        return count

    def filter_by_date_range(
        self,
        db: Session,
        date_column: str,
        date_from,
        date_to,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """
        Query records within a date range (common for financial data).
        
        Args:
            db: SQLAlchemy session
            date_column: Name of date column (e.g., 'created_at', 'transaction_date')
            date_from: Start datetime
            date_to: End datetime
            skip: Offset for pagination
            limit: Max records
        
        Returns:
            List of matching records
        """
        if not hasattr(self.model, date_column):
            raise ValueError(f"Model {self.model.__name__} has no column {date_column}")

        column = getattr(self.model, date_column)
        return (
            db.query(self.model)
            .filter(and_(column >= date_from, column <= date_to))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search(
        self,
        db: Session,
        search_term: str,
        search_columns: List[str],
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """
        Full-text search across multiple columns (for Oracle: use CONTAINS).
        
        Args:
            db: SQLAlchemy session
            search_term: Term to search for
            search_columns: List of column names to search in
            skip: Offset for pagination
            limit: Max records
        
        Returns:
            List of matching records
        """
        filters = []
        for col_name in search_columns:
            if hasattr(self.model, col_name):
                column = getattr(self.model, col_name)
                filters.append(column.ilike(f"%{search_term}%"))

        if not filters:
            return []

        return (
            db.query(self.model)
            .filter(or_(*filters))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def aggregate(
        self,
        db: Session,
        func_name: str,
        column_name: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Aggregate operation (SUM, AVG, COUNT, MIN, MAX).
        
        Useful for reporting and calculations.
        
        Args:
            db: SQLAlchemy session
            func_name: Function name ('sum', 'avg', 'count', 'min', 'max')
            column_name: Column to aggregate
            filters: Optional filters to apply
        
        Returns:
            Aggregated value
        
        Example:
            total = repo.aggregate(db, 'sum', 'amount', filters={'status': 'MATCHED'})
        """
        from sqlalchemy import func as sqla_func

        if not hasattr(self.model, column_name):
            raise ValueError(f"Model has no column {column_name}")

        func_map = {
            "sum": sqla_func.sum,
            "avg": sqla_func.avg,
            "count": sqla_func.count,
            "min": sqla_func.min,
            "max": sqla_func.max,
        }

        if func_name.lower() not in func_map:
            raise ValueError(f"Unknown aggregation function: {func_name}")

        column = getattr(self.model, column_name)
        query = db.query(func_map[func_name.lower()](column))

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)

        return query.scalar()

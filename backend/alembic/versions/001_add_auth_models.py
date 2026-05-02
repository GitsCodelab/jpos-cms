"""Add user authentication models (users, sessions, audit, blacklist)

Revision ID: 001_add_auth_models
Revises: None
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "001_add_auth_models"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create authentication tables."""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('email', sa.String(150), nullable=True),
        sa.Column('role', sa.String(50), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('user_id', sa.String(50), nullable=False),
        sa.Column('token_jti', sa.String(100), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('ix_user_sessions_token_jti', 'user_sessions', ['token_jti'], unique=True)
    op.create_index('ix_user_sessions_expires_at', 'user_sessions', ['expires_at'])
    
    # Create login_audit table
    op.create_table(
        'login_audit',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('user_id', sa.String(50), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('failure_reason', sa.String(255), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_login_audit_username', 'login_audit', ['username'])
    op.create_index('ix_login_audit_user_id', 'login_audit', ['user_id'])
    op.create_index('ix_login_audit_success', 'login_audit', ['success'])
    op.create_index('ix_login_audit_timestamp', 'login_audit', ['timestamp'])
    op.create_index('ix_login_audit_username_timestamp', 'login_audit', ['username', 'timestamp'])
    
    # Create token_blacklist table
    op.create_table(
        'token_blacklist',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('jti', sa.String(100), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('reason', sa.String(50), nullable=False),
        sa.Column('token_expires_at', sa.DateTime(), nullable=False),
        sa.Column('blacklisted_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('jti')
    )
    op.create_index('ix_token_blacklist_jti', 'token_blacklist', ['jti'], unique=True)
    op.create_index('ix_token_blacklist_username', 'token_blacklist', ['username'])
    op.create_index('ix_token_blacklist_token_expires_at', 'token_blacklist', ['token_expires_at'])


def downgrade() -> None:
    """Drop authentication tables."""
    op.drop_table('token_blacklist')
    op.drop_table('login_audit')
    op.drop_table('user_sessions')
    op.drop_table('users')

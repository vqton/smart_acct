"""create auth tables (users, roles, permissions, sessions, audit)

Revision ID: a1b2c3d4e5f6
Revises: f5a6b7c8d9e2
Create Date: 2026-07-01 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f5a6b7c8d9e2'
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table('auth_roles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index('ix_auth_roles_name', 'auth_roles', ['name'])

    op.create_table('auth_users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False, server_default=''),
        sa.Column('full_name', sa.String(length=200), nullable=False),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('must_change_password', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('locale', sa.String(length=10), nullable=False, server_default='vi'),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_auth_users_username', 'auth_users', ['username'])
    op.create_index('ix_auth_users_email', 'auth_users', ['email'])

    op.create_table('auth_permissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('resource', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('resource', 'action', name='uq_permission'),
    )
    op.create_index('ix_permission_resource_action', 'auth_permissions', ['resource', 'action'])

    op.create_table('auth_user_roles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('auth_users.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('auth_roles.id', ondelete='CASCADE'),
                  nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )
    op.create_index('ix_auth_user_roles_user_id', 'auth_user_roles', ['user_id'])
    op.create_index('ix_auth_user_roles_role_id', 'auth_user_roles', ['role_id'])

    op.create_table('auth_role_permissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('auth_roles.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('permission_id', sa.Integer(), sa.ForeignKey('auth_permissions.id', ondelete='CASCADE'),
                  nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )
    op.create_index('ix_auth_role_permissions_role_id', 'auth_role_permissions', ['role_id'])
    op.create_index('ix_auth_role_permissions_permission_id', 'auth_role_permissions', ['permission_id'])

    op.create_table('auth_user_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('auth_users.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('refresh_token_hash', sa.String(length=255), nullable=False),
        sa.Column('device_info', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_auth_user_sessions_user_id', 'auth_user_sessions', ['user_id'])
    op.create_index('ix_session_user_revoked', 'auth_user_sessions', ['user_id', 'revoked'])

    op.create_table('auth_password_reset_tokens',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('auth_users.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_auth_password_reset_tokens_user_id', 'auth_password_reset_tokens', ['user_id'])

    op.create_table('auth_audit_log',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('auth_users.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('event_type', sa.Enum(
            'login_success', 'login_failed', 'logout', 'token_refresh',
            'password_change', 'password_reset', 'account_lock',
            'account_unlock', 'session_revoke', 'role_change',
            'user_create', 'user_update', 'user_delete',
            name='autheventtypedb',
        ), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_auth_audit_log_user_id', 'auth_audit_log', ['user_id'])
    op.create_index('ix_auth_audit_log_event_type', 'auth_audit_log', ['event_type'])
    op.create_index('ix_audit_event_created', 'auth_audit_log', ['event_type', 'created_at'])


def downgrade() -> None:
    op.drop_table('auth_audit_log')
    op.drop_table('auth_password_reset_tokens')
    op.drop_table('auth_user_sessions')
    op.drop_table('auth_role_permissions')
    op.drop_table('auth_user_roles')
    op.drop_table('auth_permissions')
    op.drop_table('auth_users')
    op.drop_table('auth_roles')

    op.execute('DROP TYPE IF EXISTS autheventtypedb')

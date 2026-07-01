"""create document tables (categories, documents, versions)

Revision ID: c2d3e4f5g6h7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-01 22:00:00.000000

"""
from typing import Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c2d3e4f5g6h7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table('document_categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('document_categories.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_document_categories_code', 'document_categories', ['code'])
    op.create_index('ix_document_categories_parent_id', 'document_categories', ['parent_id'])

    op.create_table('documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('document_categories.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('file_name', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mime_type', sa.String(length=100), nullable=False,
                  server_default='application/octet-stream'),
        sa.Column('file_path', sa.String(length=1000), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('tags', sa.String(length=1000), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_documents_company_id', 'documents', ['company_id'])
    op.create_index('ix_documents_company_type', 'documents', ['company_id', 'document_type'])
    op.create_index('ix_documents_company_status', 'documents', ['company_id', 'status'])
    op.create_index('ix_documents_document_type', 'documents', ['document_type'])
    op.create_index('ix_documents_status', 'documents', ['status'])
    op.create_index('ix_documents_reference', 'documents', ['reference_type', 'reference_id'])
    op.create_index('ix_documents_reference_type', 'documents', ['reference_type'])
    op.create_index('ix_documents_reference_id', 'documents', ['reference_id'])
    op.create_index('ix_documents_category_id', 'documents', ['category_id'])
    op.create_index('ix_documents_uploaded_by', 'documents', ['uploaded_by'])

    op.create_table('document_versions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('document_id', sa.Integer(), sa.ForeignKey('documents.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('file_name', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mime_type', sa.String(length=100), nullable=False,
                  server_default='application/octet-stream'),
        sa.Column('file_path', sa.String(length=1000), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('change_notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_document_versions_document_id', 'document_versions', ['document_id'])
    op.create_index('ix_doc_versions_doc_id_number', 'document_versions', ['document_id', 'version_number'])


def downgrade() -> None:
    op.drop_table('document_versions')
    op.drop_table('documents')
    op.drop_table('document_categories')

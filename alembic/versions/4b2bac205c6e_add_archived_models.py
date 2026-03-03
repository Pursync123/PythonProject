"""Add archived models

Revision ID: 4b2bac205c6e
Revises: 
Create Date: 2026-03-02 10:48:43.323142

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4b2bac205c6e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('archived_appointments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('doctor_id', sa.String(length=20), nullable=False),
    sa.Column('slot_id', sa.UUID(), nullable=True),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('requested_datetime', sa.DateTime(), nullable=False),
    sa.Column('cancelled_at', sa.DateTime(), nullable=True),
    sa.Column('cancellation_reason', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('archived_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_archived_appointments_archived_at'), 'archived_appointments', ['archived_at'], unique=False)
    op.create_index(op.f('ix_archived_appointments_doctor_id'), 'archived_appointments', ['doctor_id'], unique=False)
    op.create_index(op.f('ix_archived_appointments_patient_id'), 'archived_appointments', ['patient_id'], unique=False)
    op.create_index(op.f('ix_archived_appointments_requested_datetime'), 'archived_appointments', ['requested_datetime'], unique=False)
    op.create_index(op.f('ix_archived_appointments_slot_id'), 'archived_appointments', ['slot_id'], unique=False)
    op.create_index(op.f('ix_archived_appointments_status'), 'archived_appointments', ['status'], unique=False)
    
    op.create_table('archived_available_slots',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('doctor_id', sa.String(length=20), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('time', sa.Time(), nullable=False),
    sa.Column('duration_minutes', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('archived_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_archived_available_slots_archived_at'), 'archived_available_slots', ['archived_at'], unique=False)
    op.create_index(op.f('ix_archived_available_slots_date'), 'archived_available_slots', ['date'], unique=False)
    op.create_index(op.f('ix_archived_available_slots_doctor_id'), 'archived_available_slots', ['doctor_id'], unique=False)
    op.create_index(op.f('ix_archived_available_slots_status'), 'archived_available_slots', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_archived_available_slots_status'), table_name='archived_available_slots')
    op.drop_index(op.f('ix_archived_available_slots_doctor_id'), table_name='archived_available_slots')
    op.drop_index(op.f('ix_archived_available_slots_date'), table_name='archived_available_slots')
    op.drop_index(op.f('ix_archived_available_slots_archived_at'), table_name='archived_available_slots')
    op.drop_table('archived_available_slots')
    op.drop_index(op.f('ix_archived_appointments_status'), table_name='archived_appointments')
    op.drop_index(op.f('ix_archived_appointments_slot_id'), table_name='archived_appointments')
    op.drop_index(op.f('ix_archived_appointments_requested_datetime'), table_name='archived_appointments')
    op.drop_index(op.f('ix_archived_appointments_patient_id'), table_name='archived_appointments')
    op.drop_index(op.f('ix_archived_appointments_doctor_id'), table_name='archived_appointments')
    op.drop_index(op.f('ix_archived_appointments_archived_at'), table_name='archived_appointments')
    op.drop_table('archived_appointments')

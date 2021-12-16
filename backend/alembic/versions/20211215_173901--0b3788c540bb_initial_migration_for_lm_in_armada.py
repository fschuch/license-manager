"""Initial migration for LM in Armada

Revision ID: 0b3788c540bb
Revises:
Create Date: 2021-12-15 17:39:01.067270

"""
import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op

# revision identifiers, used by Alembic.
revision = "0b3788c540bb"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "config",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("product", sa.String(), nullable=True),
        sa.Column("features", sa.String(), nullable=True),
        sa.Column("license_servers", sqlalchemy_utils.ScalarListType, nullable=True),
        sa.Column("license_server_type", sa.String(), nullable=True),
        sa.Column("grace_time", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "license",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_feature", sa.String(), nullable=True),
        sa.Column("used", sa.Integer(), sa.CheckConstraint("used >= 0"), nullable=True),
        sa.Column("total", sa.Integer(), sa.CheckConstraint("total >= 0"), nullable=True),
        sa.CheckConstraint("used<=total"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_feature"),
    )
    op.create_table(
        "booking",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.String(), nullable=True),
        sa.Column("product_feature", sa.String(), nullable=True),
        sa.Column("booked", sa.Integer(), nullable=True),
        sa.Column("lead_host", sa.String(), nullable=True),
        sa.Column("user_name", sa.String(), nullable=True),
        sa.Column("cluster_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("config_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["config_id"],
            ["config.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("booking")
    op.drop_table("license")
    op.drop_table("config")
    # ### end Alembic commands ###

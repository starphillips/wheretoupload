# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Comment(db.Model):
    __tablename__ = "comments"                 # <-- match your table name
    __table_args__ = {"schema": "website"}     # <-- be explicit about your schema

    id = db.Column(db.Integer, primary_key=True)

    thread = db.Column(db.String(120), index=True, nullable=False)

    # Note: because we’ve set __tablename__ to "comments", the FK should point to "comments.id"
    parent_id = db.Column(db.Integer, db.ForeignKey('website.comments.id'), nullable=True)

    children = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy='joined'
    )

    # Align lengths/types with your DBeaver table
    name = db.Column(db.String(100), nullable=False)      # table has 100
    social_url = db.Column(db.Text, nullable=True)        # table uses TEXT
    text = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, nullable=False, default=True)  # see step 2

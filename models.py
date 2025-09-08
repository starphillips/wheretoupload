from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    thread = db.Column(db.String(120), index=True, nullable=False)

    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)

    children = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy='joined'
    )

    name = db.Column(db.String(100), nullable=False)
    social_url = db.Column(db.Text, nullable=True)
    text = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, nullable=False, default=True)

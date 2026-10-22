from sqlalchemy import func
from sqlalchemy.orm import joinedload

from config.settings import Settings
from database import db
from utils.helpers import utcnow


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')
    priority = db.Column(db.Integer, default=Settings.DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref=db.backref('tasks', cascade='all, delete-orphan'))
    category = db.relationship('Category', backref='tasks')

    def to_dict(self, include_overdue=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
        }
        if include_overdue:
            data['overdue'] = self.is_overdue()
        return data

    def to_summary_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': str(self.created_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'overdue': self.is_overdue(),
        }

    def is_overdue(self):
        return bool(
            self.due_date
            and self.due_date < utcnow()
            and self.status not in Settings.CLOSED_STATUSES
        )

    # --- consultas (toda a persistência fica no model) ---

    @classmethod
    def list_with_relations(cls):
        stmt = db.select(cls).options(joinedload(cls.user), joinedload(cls.category))
        return db.session.scalars(stmt).unique().all()

    @classmethod
    def search(cls, text='', status='', priority=None, user_id=None):
        stmt = db.select(cls)
        if text:
            stmt = stmt.where(db.or_(cls.title.like(f'%{text}%'), cls.description.like(f'%{text}%')))
        if status:
            stmt = stmt.where(cls.status == status)
        if priority is not None:
            stmt = stmt.where(cls.priority == priority)
        if user_id is not None:
            stmt = stmt.where(cls.user_id == user_id)
        return db.session.scalars(stmt).all()

    @classmethod
    def for_user(cls, user_id):
        return db.session.scalars(db.select(cls).where(cls.user_id == user_id)).all()

    @classmethod
    def total(cls):
        return db.session.scalar(db.select(func.count(cls.id)))

    @classmethod
    def count_by_status(cls):
        rows = db.session.execute(db.select(cls.status, func.count()).group_by(cls.status)).all()
        return dict(rows)

    @classmethod
    def count_by_priority(cls):
        rows = db.session.execute(db.select(cls.priority, func.count()).group_by(cls.priority)).all()
        return dict(rows)

    @classmethod
    def count_by_user(cls):
        """{user_id: (total, concluídas)} em uma única query."""
        done = func.sum(db.case((cls.status == 'done', 1), else_=0))
        rows = db.session.execute(
            db.select(cls.user_id, func.count(), done).where(cls.user_id.is_not(None)).group_by(cls.user_id)
        ).all()
        return {user_id: (total, int(completed)) for user_id, total, completed in rows}

    @classmethod
    def count_by_category(cls):
        rows = db.session.execute(
            db.select(cls.category_id, func.count()).where(cls.category_id.is_not(None)).group_by(cls.category_id)
        ).all()
        return dict(rows)

    @classmethod
    def overdue(cls):
        stmt = db.select(cls).where(
            cls.due_date < utcnow(),
            cls.status.not_in(Settings.CLOSED_STATUSES),
        )
        return db.session.scalars(stmt).all()

    @classmethod
    def created_since(cls, moment):
        return db.session.scalar(db.select(func.count(cls.id)).where(cls.created_at >= moment))

    @classmethod
    def done_since(cls, moment):
        return db.session.scalar(
            db.select(func.count(cls.id)).where(cls.status == 'done', cls.updated_at >= moment)
        )

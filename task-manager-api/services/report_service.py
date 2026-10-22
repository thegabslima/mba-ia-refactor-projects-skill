from collections import Counter
from datetime import timedelta

from config.settings import Settings
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import calculate_percentage, utcnow


def summary():
    now = utcnow()
    by_status = Task.count_by_status()
    by_priority = Task.count_by_priority()
    since = now - timedelta(days=Settings.RECENT_DAYS)

    overdue_tasks = Task.overdue()
    overdue_list = [
        {
            'id': t.id,
            'title': t.title,
            'due_date': str(t.due_date),
            'days_overdue': (now - t.due_date).days,
        }
        for t in overdue_tasks
    ]

    totals_by_user = Task.count_by_user()
    users = User.list_all()
    user_stats = []
    for user in users:
        total, completed = totals_by_user.get(user.id, (0, 0))
        user_stats.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': calculate_percentage(completed, total),
        })

    return {
        'generated_at': str(now),
        'overview': {
            'total_tasks': Task.total(),
            'total_users': len(users),
            'total_categories': len(Category.list_all()),
        },
        'tasks_by_status': {s: by_status.get(s, 0) for s in Settings.VALID_STATUSES},
        'tasks_by_priority': {
            'critical': by_priority.get(1, 0),
            'high': by_priority.get(2, 0),
            'medium': by_priority.get(3, 0),
            'low': by_priority.get(4, 0),
            'minimal': by_priority.get(5, 0),
        },
        'overdue': {'count': len(overdue_list), 'tasks': overdue_list},
        'recent_activity': {
            'tasks_created_last_7_days': Task.created_since(since),
            'tasks_completed_last_7_days': Task.done_since(since),
        },
        'user_productivity': user_stats,
    }


def user_report(user):
    tasks = Task.for_user(user.id)
    statuses = Counter(t.status for t in tasks)
    total = len(tasks)
    done = statuses['done']

    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': statuses['pending'],
            'in_progress': statuses['in_progress'],
            'cancelled': statuses['cancelled'],
            'overdue': sum(1 for t in tasks if t.is_overdue()),
            'high_priority': sum(1 for t in tasks if t.priority <= Settings.HIGH_PRIORITY_MAX),
            'completion_rate': calculate_percentage(done, total),
        },
    }

# Contains all database query functions

import sqlite3
from datetime import datetime, timezone
from app.database import get_db

def row_to_dict(row):
    if row is None:
        return None
    return dict(row)

def rows_to_list(row):
    return [dict(row) for row in row]

def get_user_by_email(email):
    db = get_db()
    row = db.execute(
        'SELECT * FROM users WHERE email = ?',
        (email.lower().strip(),),
    ).fetchone()
    return row_to_dict(row)

def get_user_by_id (user_id):
    db = get_db()
    row = db.execute(
        'SELECT id, email, username, created_at FROM users WHERE id = ?',
        (user_id,)
    ).fetchone()
    return row_to_dict(row)

def create_user(email, username, hashed_password):
    db = get_db()

    try:
        cursor = db.execute(
            'INSERT INTO users (email, username, password) VALUES (?, ?, ?)',
            (email.lower().strip(), username.strip(), hashed_password)
        )
        db.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    
def get_categories (user_id):
    db = get_db()
    rows = db.execute(
        'SELECT * FROM categories WHERE user_id = ? ORDER BY name ASC',
        (user_id,)
    ).fetchall()
    return rows_to_list(rows)

def create_category (user_id, name, color = '#6366f1'):
    db = get_db()
    cursor = db.execute(
        'INSERT INTO categories (user_id, name, color) VALUES (?, ?, ?)',
        (user_id, name.strip(), color)
    )
    db.commit()
    row = db.execute(
        'SELECT * FROM categories WHERE id = ?',
        (cursor.lastrowid,)
    ).fetchone()
    return row_to_dict(row)

def delete_category (category_id, user_id):
    db = get_db()
    cursor = db.execute(
        'DELETE FROM categories WHERE user_id = ? AND category_id = ?',
        (category_id, user_id)
    )
    db.commit()
    return cursor.rowcount > 0

def seed_default_categories(user_id):
    defaults = [
         ('Work',     '#6366f1'),   
        ('Personal', '#10b981'),  
        ('Health',   '#f59e0b'), 
        ('Learning', '#3b82f6'),   
    ]
    db = get_db()
    for name, color in defaults:
        db.execute(
            'INSERT INTO categories (user_id, name, color) VALUES (?, ?, ?)',
            (user_id, name, color)
        )
    db.commit()

def get_tasks (user_id, filters = None):
    filters = filters or {}

    query = '''
        SELECT 
            t.*,
            c.name  AS category_name,
            c.color AS category_color
        FROM tasks t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
    '''
    params = [user_id]
 
    if 'date' in filters and filters['date']:
        query += ' AND t.due_date = ?'
        params.append(filters['date'])

    if 'week_start' in filters and filters['week_start']: 
        query += " AND t.due_date >= ? AND t.due_date < date(?, '+7 days')"
        params.append(filters['week_start'])
        params.append(filters['week_start'])

    if 'category' in filters and filters['category']:
        query += ' AND t.category_id = ?'
        params.append(filters['category'])

    if 'priority' in filters and filters['priority']:
        query += ' AND t.priority = ?'
        params.append(filters['priority'])

    if 'complete' in filters and filters['complete'] is not None:
        query += ' AND t.is_complete = ?'
        params.append(1 if filters['complete'] else 0)
 
    query += ' ORDER BY t.is_complete ASC, t.due_date ASC, t.created_at ASC'

    db = get_db()
    rows = db.execute(query, params).fetchall()
    return rows_to_list(rows)

def get_task_by_id (task_id, user_id):
    db = get_db()
    row = db.execute(
        '''SELECT t.*, c.name AS category_name, c.color AS category_color 
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.id = ? AND t.user_id = ?''',
        (task_id, user_id)
    ).fetchone()
    return row_to_dict(row)

def create_task(user_id, data):  
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO tasks 
           (user_id, category_id, title, description, 
            due_date, due_time, priority, reminder_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            user_id,
            data.get('category_id'),           
            data['title'].strip(),
            data.get('description', '').strip(),
            data.get('due_date'),             
            data.get('due_time'),             
            data.get('priority', 'medium'),
            data.get('reminder_at'),
        )
    )
    db.commit()
    return get_task_by_id(cursor.lastrowid, user_id)


def update_task(task_id, user_id, data): 
    db = get_db()
 
    allowed_fields = [
        'category_id', 'title', 'description',
        'due_date', 'due_time', 'priority', 'reminder_at'
    ]
 
    set_clauses = []
    params = []

    for field in allowed_fields:
        if field in data:
            set_clauses.append(f'{field} = ?')
            params.append(data[field])

    if not set_clauses: 
        return get_task_by_id(task_id, user_id)
 
    set_clauses.append('updated_at = CURRENT_TIMESTAMP')
 
    query = f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = ? AND user_id = ?"
    params.extend([task_id, user_id])

    db.execute(query, params)
    db.commit()
    return get_task_by_id(task_id, user_id)


def toggle_task(task_id, user_id): 
    db = get_db()
 
    task = get_task_by_id(task_id, user_id)
    if not task:
        return None
 
    new_state = 0 if task['is_complete'] else 1
    completed_at = datetime.now(timezone.utc).isoformat() if new_state == 1 else None

    db.execute(
        '''UPDATE tasks 
           SET is_complete = ?, completed_at = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ? AND user_id = ?''',
        (new_state, completed_at, task_id, user_id)
    )
    db.commit()
    return get_task_by_id(task_id, user_id)


def delete_task(task_id, user_id): 
    db = get_db()
    cursor = db.execute(
        'DELETE FROM tasks WHERE id = ? AND user_id = ?',
        (task_id, user_id)
    )
    db.commit()
    return cursor.rowcount > 0

def get_analytics_summary(user_id): 
    db = get_db()
    today = datetime.now().strftime('%Y-%m-%d')

    stats = db.execute(
        '''SELECT
            COUNT(*)                                         AS total_tasks,
            SUM(CASE WHEN is_complete = 1 THEN 1 ELSE 0 END) AS completed_tasks,
            SUM(CASE WHEN is_complete = 0 THEN 1 ELSE 0 END) AS pending_tasks,
            SUM(CASE WHEN is_complete = 0 
                      AND due_date = ?   THEN 1 ELSE 0 END)  AS due_today,
            SUM(CASE WHEN is_complete = 0 
                      AND due_date < ?
                      AND due_date IS NOT NULL
                      THEN 1 ELSE 0 END)                     AS overdue
           FROM tasks
           WHERE user_id = ?''',
        (today, today, user_id)
    ).fetchone()

    result = row_to_dict(stats)
 
    total = result['total_tasks'] or 0
    completed = result['completed_tasks'] or 0
    result['completion_rate'] = round((completed / total * 100), 1) if total > 0 else 0.0

    return result


def get_analytics_history(user_id, days=30): 
    db = get_db()

    rows = db.execute(
        '''SELECT 
            DATE(completed_at) AS date,
            COUNT(*)           AS count
           FROM tasks
           WHERE user_id = ?
             AND is_complete = 1
             AND completed_at >= DATE('now', ? || ' days')
           GROUP BY DATE(completed_at)
           ORDER BY date ASC''',
        (user_id, f'-{days}')
    ).fetchall()

    return rows_to_list(rows)
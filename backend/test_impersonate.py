from app import create_app
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    client = app.test_client()

    # ensure admin exists (username=admin, password=admin123) - tests assume this
    from models import Admin, Teacher
    from app import db

    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin()
        admin.username = 'admin'
        admin.email = 'admin@example.com'
        admin.password_hash = generate_password_hash('admin123')
        admin.active = True
        db.session.add(admin)
        db.session.commit()

    # ensure a teacher exists
    teacher = Teacher.query.filter_by(userid='t1').first()
    if not teacher:
        teacher = Teacher()
        teacher.name = 'Test Teacher'
        teacher.userid = 't1'
        teacher.email = 't1@example.com'
        teacher.password_hash = generate_password_hash('teach123')
        teacher.active = True
        db.session.add(teacher)
        db.session.commit()

    # admin login to get token
    res = client.post('/admin/login', json={'userid':'admin', 'password':'admin123'})
    print('admin login status', res.status_code, res.get_data(as_text=True))
    if res.status_code != 200:
        raise SystemExit('admin login failed')
    data = res.get_json()
    token = data.get('token')

    # call impersonate
    headers = {'Authorization': f'Bearer {token}'}
    res2 = client.post(f'/admin/teachers/{teacher.teacher_id}/impersonate', headers=headers)
    print('impersonate status', res2.status_code, res2.get_data(as_text=True))

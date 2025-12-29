from app import create_app

app = create_app()
with app.app_context():
    client = app.test_client()
    res = client.post('/auth/login', json={'userid':'admin','password':'admin123'})
    print('STATUS:', res.status_code)
    print(res.get_data(as_text=True))

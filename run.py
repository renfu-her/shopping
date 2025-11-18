from app import create_app, db
from app.database import init_db
import os

app = create_app()

with app.app_context():
    db.create_all()
    init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


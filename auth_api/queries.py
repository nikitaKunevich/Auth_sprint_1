from db import db_session
from db_models import User

# Insert-запросы
admin = User('admin', 'password')
db_session.add(admin)
db_session.commit()

# Select-запросы
User.query.all()
User.query.filter_by(login='admin').first()

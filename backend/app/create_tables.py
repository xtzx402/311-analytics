from database import engine, Base
from models import Complaint

Base.metadata.create_all(bind=engine)
print("Tables created.")
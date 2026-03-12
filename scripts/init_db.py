from app.db.session import engine
from app.models.models import Base

def init_db():
    print("Creating all tables in the database...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    init_db()

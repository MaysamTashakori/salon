from bot.database.database import Base, engine
from bot.database.models import User, Service, Appointment, Review

def create_tables():
    Base.metadata.drop_all(engine)  # This will drop existing tables
    Base.metadata.create_all(engine)
    print("✅ Tables created successfully!")

if __name__ == "__main__":
    create_tables()

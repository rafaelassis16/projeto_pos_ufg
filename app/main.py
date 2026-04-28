from app.database.db import Base, engine

Base.metadata.create_all(bind=engine)
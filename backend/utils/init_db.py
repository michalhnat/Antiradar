from backend.app.db.database import engine
from backend.app.db import models

models.Base.metadata.create_all(engine)

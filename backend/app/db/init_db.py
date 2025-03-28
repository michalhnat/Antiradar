# import logging
# import time

# from sqlalchemy import text
# from sqlalchemy.exc import OperationalError

# from . import Models
# from .Database import Base, engine

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# def init_db():
#     max_retries = 5
#     retry_count = 0

#     while retry_count < max_retries:
#         try:
#             with engine.connect() as conn:
#                 conn.execute(text("SELECT 1"))
#                 logger.info("Database connection successful")

#             logger.info("Creating database tables")
#             Base.metadata.create_all(bind=engine)
#             logger.info("Database tables created successfully")
#             return

#         except OperationalError as e:
#             retry_count += 1
#             wait_time = 2**retry_count
#             logger.warning(
#                 f"Database connection failed (attempt {retry_count}/{max_retries}): {e}"
#             )
#             logger.info(f"Waiting {wait_time} seconds before retrying...")
#             time.sleep(wait_time)

#     logger.error("Failed to initialize database after multiple attempts")
#     raise RuntimeError("Database initialization failed")


# if __name__ == "__main__":
#     logger.info("Starting database initialization")
#     init_db()

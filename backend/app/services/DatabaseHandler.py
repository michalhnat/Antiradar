import logging


class DatabaseHandler:
    def __init__(self, db):
        self.db = db

    # def get_all(self, table):
    #     return self.db[table].all()

    # def get_one(self, table, id):
    #     return self.db[table].get(id=id)

    def add(self, table, record):
        try:
            self.db.add(record)
            self.db.commit()
            return record
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error: {e}")
            return None

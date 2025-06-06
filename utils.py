import models
import app
import flask

import models.db

if __name__ == "__main__":
    db = models.db.BillDataBase(app.app, models.data.db)
    db.show_tables()
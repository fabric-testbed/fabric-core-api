from flask_sqlalchemy import SQLAlchemy


class MySQLAlchemy(SQLAlchemy):
    ...


# PY-44557 workaround, replace: db = SQLAlchemy()
db = MySQLAlchemy()
# db = SQLAlchemy()

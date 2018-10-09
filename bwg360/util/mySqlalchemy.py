# coding:utf-8
from flask_sqlalchemy import SQLAlchemy


class UnlockedReadAlchemy(SQLAlchemy):
    def apply_driver_hacks(self, app, info, options):
        if "isolation_level" not in options:
            options["isolation_level"] = "READ UNCOMMITTED"

        return super(UnlockedReadAlchemy, self).apply_driver_hacks(app, info, options)


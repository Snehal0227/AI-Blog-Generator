from app import app
from models import db
from sqlalchemy import inspect, text


with app.app_context():

    inspector = inspect(db.engine)

    # Check blogs table
    if "blogs" not in inspector.get_table_names():

        print("ERROR: blogs table not found!")

    else:

        columns = [
            column["name"]
            for column in inspector.get_columns("blogs")
        ]

        print("Existing columns:", columns)

        # Add views column only if it does not already exist
        if "views" not in columns:

            with db.engine.begin() as connection:

                connection.execute(
                    text(
                        "ALTER TABLE blogs "
                        "ADD COLUMN views INTEGER DEFAULT 0"
                    )
                )

            print("SUCCESS: views column added!")

        else:

            print("views column already exists!")

        print("Database update completed.")
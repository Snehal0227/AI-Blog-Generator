from app import app
from models import db
from sqlalchemy import inspect, text


with app.app_context():

    # Database tables create
    db.create_all()

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

        # Add views column if missing
        if "views" not in columns:

            with db.engine.connect() as connection:

                connection.execute(
                    text(
                        "ALTER TABLE blogs "
                        "ADD COLUMN views INTEGER DEFAULT 0"
                    )
                )

                connection.commit()

            print("SUCCESS: views column added!")

        else:

            print("views column already exists!")

        print("Database update completed successfully!")
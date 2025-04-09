import hashlib
import datetime
import os
from sqlalchemy import create_engine, Table, MetaData, delete, insert, Column, String, inspect, select, func
from sqlalchemy.orm import sessionmaker

user_db_file_location = "database_file/users.db"
note_db_file_location = "database_file/notes.db"
image_db_file_location = "database_file/images.db"

if os.getenv('ENVIRONMENT') == 'development':
    database_uri = 'sqlite:///database_file/flask.db'
elif os.getenv('ENVIRONMENT') == 'staging':
    db_username = os.getenv('STAGING_DB_USERNAME')
    db_password = os.getenv('STAGING_DB_PASSWORD')
    db_host = os.getenv('STAGING_DB_HOST')
    db_name = os.getenv('STAGING_DB_NAME')
    database_uri = f'postgresql://{db_username}:{db_password}@{db_host}/{db_name}'
elif os.getenv('ENVIRONMENT') == 'production':
    db_username = os.getenv('PRODUCTION_DB_USERNAME')
    db_password = os.getenv('PRODUCTION_DB_PASSWORD')
    db_host = os.getenv('PRODUCTION_DB_HOST')
    db_name = os.getenv('PRODUCTION_DB_NAME')
    database_uri = f'postgresql://{db_username}:{db_password}@{db_host}/{db_name}'
else:
    database_uri = 'sqlite:///database_file/flask.db'

engine = create_engine(database_uri, echo=True)
metadata = MetaData()
metadata.bind = engine
Session = sessionmaker(bind=engine)
print("Database type:", engine.dialect.name)
inspector = inspect(engine)
tables = inspector.get_table_names()

def migrate_data():
    print("Starting data migration...")

    # Table declarations
    global users_table, notes_table, images_table

    # Check existing tables
    existing_tables = set(inspect(engine).get_table_names())

    if 'users' in existing_tables:
        users_table = Table('users', metadata, autoload_with=engine)
    else:
        print("Creating users table...")
        users_table = Table('users', metadata,
                            Column('id', String, primary_key=True),
                            Column('pw', String)
                            )

    if 'notes' in existing_tables:
        notes_table = Table('notes', metadata, autoload_with=engine)
    else:
        print("Creating notes table...")
        notes_table = Table('notes', metadata,
                            Column('user', String),
                            Column('timestamp', String),
                            Column('note', String),
                            Column('note_id', String)
                            )

    if 'images' in existing_tables:
        images_table = Table('images', metadata, autoload_with=engine)
    else:
        print("Creating images table...")
        images_table = Table('images', metadata,
                            Column('uid', String, primary_key=True),
                            Column('owner', String),
                            Column('name', String),
                            Column('timestamp', String)
                            )

    # Create tables that didn't already exist
    metadata.create_all(engine)
    print("Tables verified and created as needed.")

    # Source SQLite databases
    users_engine = create_engine(f'sqlite:///{user_db_file_location}')
    notes_engine = create_engine(f'sqlite:///{note_db_file_location}')
    images_engine = create_engine(f'sqlite:///{image_db_file_location}')

    # Reflect source tables
    users_source_table = Table('users', MetaData(), autoload_with=users_engine)
    notes_source_table = Table('notes', MetaData(), autoload_with=notes_engine)
    images_source_table = Table('images', MetaData(), autoload_with=images_engine)

    # Begin target session
    session = Session()

    # Migrate users
    users_count = session.execute(select(func.count()).select_from(users_table)).scalar()
    if users_count == 0:
        print("Migrating users...")
        with users_engine.connect() as conn:
            users_data = conn.execute(select(users_source_table)).mappings().all()
            session.execute(users_table.insert(), users_data)

    # Migrate notes
    notes_count = session.execute(select(func.count()).select_from(notes_table)).scalar()
    if notes_count == 0:
        print("Migrating notes...")
        with notes_engine.connect() as conn:
            notes_data = conn.execute(select(notes_source_table)).mappings().all()
            session.execute(notes_table.insert(), notes_data)

    # Migrate images
    images_count = session.execute(select(func.count()).select_from(images_table)).scalar()
    if images_count == 0:
        print("Migrating images...")
        with images_engine.connect() as conn:
            images_data = conn.execute(select(images_source_table)).mappings().all()
            session.execute(images_table.insert(), images_data)

    session.commit()
    session.close()
    print("Data migration completed successfully!")



# List all users in the database
def list_users():
    session = Session()
    users_table = Table('users', metadata, autoload_with=engine)
    result = [x.id for x in session.query(users_table).all()]
    session.close()
    return result


# Verify the user's credentials
def verify(id, pw):
    session = Session()
    users_table = Table('users', metadata, autoload_with=engine)
    user = session.query(users_table).filter_by(id=id).first()
    session.close()
    if user:
        return user.pw == hashlib.sha256(pw.encode()).hexdigest()
    return False


# Delete a user from the database
def delete_user_from_db(id):
    session = Session()
    users_table = Table('users', metadata, autoload_with=engine)
    session.execute(delete(users_table).where(users_table.c.id.__eq__(id.upper())))
    session.commit()
    session.close()


# Add a user to the database
def add_user(id, pw):
    session = Session()
    users_table = Table('users', metadata, autoload_with=engine)
    session.execute(users_table.insert().values(id=id.upper(), pw=hashlib.sha256(pw.encode()).hexdigest()))
    session.commit()
    session.close()


# Update a user's password
def read_note_from_db(id):
    session = Session()
    notes_table = Table('notes', metadata, autoload_with=engine)
    result = session.query(notes_table.c.note_id, notes_table.c.timestamp, notes_table.c.note).filter(
        notes_table.c.user.__eq__(id.upper())).all()
    session.close()
    return result


# Read a note from the database
def match_user_id_with_note_id(note_id):
    session = Session()
    notes_table = Table('notes', metadata, autoload_with=engine)
    result = session.query(notes_table.c.user).filter(notes_table.c.note_id.__eq__(note_id)).scalar()
    session.close()
    return result


# Write a note to the database
def write_note_into_db(id, note_to_write):
    session = Session()
    notes_table = Table('notes', metadata, autoload_with=engine)
    current_timestamp = str(datetime.datetime.now())
    session.execute(insert(notes_table).values(user=id.upper(), timestamp=current_timestamp, note=note_to_write,
                                               note_id=hashlib.sha1(
                                                   (id.upper() + current_timestamp).encode()).hexdigest()))
    session.commit()
    session.close()


# Update a note in the database
def delete_note_from_db(note_id):
    session = Session()
    notes_table = Table('notes', metadata, autoload_with=engine)
    session.execute(delete(notes_table).where(notes_table.c.note_id.__eq__(note_id)))
    session.commit()
    session.close()


# Update a note in the database
def image_upload_record(uid, owner, image_name, timestamp):
    session = Session()
    images_table = Table('images', metadata, autoload_with=engine)
    session.execute(insert(images_table).values(uid=uid, owner=owner, name=image_name, timestamp=timestamp))
    session.commit()
    session.close()


# List all images for a user
def list_images_for_user(owner):
    session = Session()
    images_table = Table('images', metadata, autoload_with=engine)
    result = (session.query(images_table.c.uid, images_table.c.timestamp, images_table.c.name)
              .filter(images_table.c.owner.__eq__(owner.upper())).all())
    session.close()
    return result


# Match a user ID with an image UID
def match_user_id_with_image_uid(image_uid):
    session = Session()
    images_table = Table('images', metadata, autoload_with=engine)
    result = session.query(images_table.c.owner).filter(images_table.c.uid.__eq__(image_uid)).scalar()
    session.close()
    return result


# Delete an image from the database
def delete_image_from_db(image_uid):
    session = Session()
    images_table = Table('images', metadata, autoload_with=engine)
    session.query(images_table).filter(images_table.c.uid.__eq__(image_uid)).delete()
    session.commit()
    session.close()


if __name__ == "__main__":
    migrate_data()
    print(list_users())

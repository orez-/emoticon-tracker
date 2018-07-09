import getpass

import sqlalchemy


def connect(user, db, host='localhost', port=5432):
    """Returns a connection and a metadata object"""
    url = f'postgresql://{user}@{host}:{port}/{db}'

    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(url, client_encoding='utf8')

    # We then bind the connection to MetaData()
    meta = sqlalchemy.MetaData(bind=con)

    return con, meta


def default_connect():
    user = getpass.getuser()
    return connect(user, user)


connection, metadata = default_connect()

emoticon_table = sqlalchemy.Table(
    'emoticon', metadata,
    sqlalchemy.Column('id'),
    sqlalchemy.Column('name'),
    sqlalchemy.Column('url'),
    sqlalchemy.Column('_row_created'),
    sqlalchemy.Column('added'),
    sqlalchemy.Column('removed'),
    sqlalchemy.Column('image'),
    schema='wp_hipchat',
)

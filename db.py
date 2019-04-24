import getpass
import itertools

import sqlalchemy

import model

MANY_ADDED_THRESHOLD = 10


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
    sqlalchemy.Column('added_by'),
    schema='wp_slack',
)


def _to_row(emoticon):
    row = {
        'name': emoticon.name,
        'url': emoticon.url,
        'added_by': emoticon.added_by,
    }

    if emoticon.url.startswith('http'):
        image = model.get_image(emoticon.url)
        row.update({
            'image': image.raw_data,
            'added': image.created,
        })

    return row


def add_emoticons(emoticons):
    if len(emoticons) >= MANY_ADDED_THRESHOLD:
        print("Fetching a LOT of images; this may take some time.")
    emoticon_rows = [_to_row(emoticon) for emoticon in emoticons]
    if emoticon_rows:
        query = emoticon_table.insert().values(emoticon_rows)
        connection.execute(query)
    return [emoticon.name for emoticon in emoticons]


def remove_emoticons(emoticons):
    emoticon_ids = [emoticon.id for emoticon in emoticons]
    if emoticon_ids:
        query = (
            emoticon_table.update()
            .values({'removed': sqlalchemy.func.now()})
            .where(sqlalchemy.and_(
                emoticon_table.c.id.in_(emoticon_ids),
                emoticon_table.c.removed.is_(None),
            ))
        )
        connection.execute(query)
    return [emoticon.name for emoticon in emoticons]


def fetch_emoticons():
    query = sqlalchemy.select([
        emoticon_table.c.id,
        emoticon_table.c.name,
        emoticon_table.c.url,
        emoticon_table.c.added_by,
    ]).where(emoticon_table.c.removed.is_(None))
    return (
        model.ComparableEmoticon(
            id=row.id,
            name=row.name,
            url=row.url,
            added_by=row.added_by,
        ) for row in connection.execute(query)
    )


def get_changes_since(since_date):
    query = sqlalchemy.select([
        emoticon_table.c.removed.isnot(None).label('removed'),
        emoticon_table.c.id,
        emoticon_table.c.name,
        emoticon_table.c.url,
        emoticon_table.c.added_by,
    ]).where(sqlalchemy.or_(
        emoticon_table.c.added > since_date,
        emoticon_table.c.removed > since_date,
    )).order_by(emoticon_table.c.removed.is_(None))

    return {
        removed: [
            model.ComparableEmoticon(
                id=row.id,
                name=row.name,
                url=row.url,
                added_by=row.added_by,
            ) for row in rows
        ]
        for removed, rows in itertools.groupby(connection.execute(query), lambda row: row.removed)
    }


def get_image(name):
    query = (
        sqlalchemy.select([emoticon_table.c.image])
        .where(emoticon_table.c.name == name)
        .order_by(emoticon_table.c.added.desc())
        .limit(1)
    )
    return connection.execute(query).scalar()

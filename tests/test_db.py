from yo import db
import json
import os

import pytest
from sqlalchemy import MetaData

from yo import db
from yo import mock_notifications
from yo import mock_settings
from yo.db_utils import init_db



def test_schema_sqlite(sqlite_db):
    """Test init_schema creates empty tables"""
    yo_db = sqlite_db
    m = MetaData()
    m.create_all(bind=yo_db.engine)
    for table in m.tables.values():
        with yo_db.acquire_conn() as conn:
            query = table.select().where(True)
            response = conn.execute(query).fetchall()
            assert len(response) == 0, '%s should have 0 rows' % table

def test_wwwpoll_notification(sqlite_db):
    """Test making a wwwpoll notification and retrieving it"""
    vote_data = {
        'author': 'testuser1336',
        'weight': 100,
        'item': {
            'author': 'testuser1337',
            'permlink': 'test-post-1',
            'summary': 'A test post',
            'category': 'test',
            'depth': 0
        }
    }
    test_data = {
        'json_data': json.dumps(vote_data),
        'to_username': 'testuser1337',
        'from_username': 'testuser1336',
        'notify_type': 'vote'
    }

    yo_db = sqlite_db
    retval = yo_db.create_wwwpoll_notification(**test_data)
    assert retval is True
    get_resp = yo_db.get_wwwpoll_notifications(to_username='testuser1337', limit=2).fetchall()
    assert len(get_resp) == 1
    assert get_resp[0]['read'] == False
    assert get_resp[0]['shown'] == False
    assert get_resp[0]['to_username'] == 'testuser1337'
    assert json.loads(get_resp[0]['json_data']) == vote_data

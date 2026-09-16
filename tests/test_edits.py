"""forward_edits and num_threads in bots.json."""
import logging
import time

from fastapi.testclient import TestClient

from conftest import TOKEN, message, server_module, update


def test_edits_are_forwarded_when_enabled(make_bot, posts):
    bot = make_bot(forward_edits=1, num_threads=8)
    assert bot.worker_pool.num_threads == 8

    edited = message(5001, 10, 'fixed text', edit_date=1758000100)
    bot.process_new_updates([update('edited_message', edited)])
    calls = posts.wait(1)

    assert len(calls) == 1
    call = calls[0]
    assert call.url == 'http://localhost:4221/edited_message'
    assert call.json == edited
    assert call.headers == {'Authorization': f'Bearer {TOKEN}'}
    assert call.timeout == 10


def test_edits_are_dropped_by_default(make_bot, posts):
    bot = make_bot()
    assert bot.worker_pool.num_threads == 2
    assert bot.edited_message_handlers == []

    bot.process_new_updates([update('edited_message', message(5001, 10, 'fixed', edit_date=1))])
    time.sleep(0.3)
    assert posts.calls == []


def test_forward_edits_zero_is_off(make_bot):
    assert make_bot(forward_edits=0).edited_message_handlers == []
    assert make_bot(forward_edits='0').edited_message_handlers == []


def test_message_path_is_unchanged(make_bot, posts):
    bot = make_bot(forward_edits=1, num_threads=8, bot_url_prefix='http://127.0.0.1')
    new = message(5001, 11, 'hello')
    bot.process_new_updates([update('message', new)])
    calls = posts.wait(1)

    assert len(calls) == 1
    call = calls[0]
    assert call.url == 'http://127.0.0.1:4221/message'
    assert call.json == new
    assert call.headers == {'Authorization': f'Bearer {TOKEN}'}
    assert not hasattr(call, 'timeout')


def test_group_starters_apply_to_edited_captions(make_bot, posts):
    bot = make_bot(forward_edits=1, group_starters=['/cl'])
    bot.process_new_updates([update('edited_message', message(-100, 1, caption='hello', edit_date=1))])
    bot.process_new_updates([update('edited_message', message(-100, 2, text='hello', edit_date=1))])
    bot.process_new_updates([update('edited_message', message(-100, 3, caption='/cl 2+2', edit_date=1))])
    bot.process_new_updates([update('edited_message', message(5001, 4, caption='hello', edit_date=1))])
    time.sleep(0.3)
    assert sorted(c.json['message_id'] for c in posts.wait(2)) == [3, 4]


def test_edit_through_the_webhook(make_bot, posts, monkeypatch):
    bot = make_bot(forward_edits=1)
    monkeypatch.setitem(server_module.bots, TOKEN, bot)
    client = TestClient(server_module.app)     # no lifespan: nothing registers webhooks

    edited = message(-100, 7, 'edited in the group', edit_date=1758000100)
    response = client.post(f'/{TOKEN}/', json={'update_id': 99, 'edited_message': edited})
    assert response.status_code == 200
    calls = posts.wait(1)
    assert [c.url for c in calls] == ['http://localhost:4221/edited_message']
    assert calls[0].json == edited


def test_failed_forward_is_logged_without_the_text(make_bot, posts, caplog):
    caplog.set_level(logging.INFO)
    posts.error = ConnectionError('connection refused')
    bot = make_bot(forward_edits=1)
    bot.process_new_updates([update('edited_message', message(5001, 12, 'secret words', edit_date=1))])
    posts.wait(1)
    time.sleep(0.2)
    errors = [r.getMessage() for r in caplog.records if r.levelno >= logging.ERROR]
    assert any('chat 5001, message 12' in e and 'connection refused' in e for e in errors)
    assert not any('secret words' in r.getMessage() for r in caplog.records)

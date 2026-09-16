"""Test harness for the relay: no Telegram, no bots behind it.

server.py configures logging from ./logging.ini and reads ./config.json, so the
tests run from a temp directory holding copies of them. Webhook calls are
stubbed and requests.post is recorded.

Run from the repo root with a venv that has server/requirements.txt, pytest
and httpx (Python 3.9, like the image):
    python -m pytest tests -q
"""
import asyncio
import json
import logging.config  # server.py uses logging.config without importing it
import os
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[1]

_boot = tempfile.mkdtemp(prefix='relay-tests-')
shutil.copy(REPO / 'logging.ini', _boot)
shutil.copy(REPO / 'config.json', _boot)
_cwd = os.getcwd()
os.chdir(_boot)
sys.path.insert(0, str(REPO / 'server'))
try:
    import server as server_module  # noqa: E402
finally:
    os.chdir(_cwd)

import telebot  # noqa: E402

TOKEN = '123456:TEST-TOKEN'


class Posts:
    """Stands in for requests.post and records every call."""

    def __init__(self):
        self.calls = []
        self.error = None
        self.condition = threading.Condition()

    def __call__(self, url, **kwargs):
        with self.condition:
            self.calls.append(SimpleNamespace(url=url, **kwargs))
            self.condition.notify_all()
        if self.error is not None:
            raise self.error
        return SimpleNamespace(status_code=200, headers={'Content-Type': 'application/json'},
                               text=json.dumps({'type': 'empty', 'body': ''}), content=b'')

    def wait(self, n, timeout=5):
        with self.condition:
            self.condition.wait_for(lambda: len(self.calls) >= n, timeout)
        return self.calls


@pytest.fixture
def posts(monkeypatch):
    recorder = Posts()
    monkeypatch.setattr(server_module.requests, 'post', recorder)
    monkeypatch.setattr(telebot.TeleBot, 'remove_webhook', lambda self, *a, **k: True)
    monkeypatch.setattr(telebot.TeleBot, 'set_webhook', lambda self, *a, **k: True)
    return recorder


@pytest.fixture
def make_bot(posts):
    bots = []

    def make(**config):
        bot_config = {'TOKEN': TOKEN, 'PORT': 4221, 'bot': '', 'active': 1}
        bot_config.update(config)
        cwd = os.getcwd()
        os.chdir(_boot)
        try:
            bot = asyncio.run(server_module.init_bot(bot_config))
        finally:
            os.chdir(cwd)
        bots.append(bot)
        return bot

    yield make
    for bot in bots:
        bot.worker_pool.close()


def update(kind, message):
    return telebot.types.Update.de_json({'update_id': int(time.time()), kind: message})


def message(chat_id, message_id, text=None, caption=None, chat_type=None, edit_date=None):
    chat_type = chat_type or ('private' if chat_id > 0 else 'supergroup')
    msg = {
        'message_id': message_id,
        'from': {'id': 5001, 'is_bot': False, 'first_name': 'Alice'},
        'chat': {'id': chat_id, 'type': chat_type},
        'date': 1758000000,
    }
    if text is not None:
        msg['text'] = text
    if caption is not None:
        msg['caption'] = caption
        msg['photo'] = [{'file_id': 'f', 'file_unique_id': 'u', 'width': 1, 'height': 1}]
    if edit_date is not None:
        msg['edit_date'] = edit_date
    return msg

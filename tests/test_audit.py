"""Tests for envault.audit module."""

import os
import pytest
from pathlib import Path

from envault.audit import record_event, read_events, clear_log


@pytest.fixture(autouse=True)
def isolated_audit_dir(tmp_path, monkeypatch):
    """Redirect ENVAULT_DIR to a temp directory for each test."""
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    yield tmp_path


def test_record_creates_log_file(isolated_audit_dir):
    record_event("set", "dev")
    log_file = isolated_audit_dir / "audit.log"
    assert log_file.exists()


def test_record_event_fields():
    record_event("inject", "staging", success=True, details="3 vars injected")
    events = read_events()
    assert len(events) == 1
    ev = events[0]
    assert ev["action"] == "inject"
    assert ev["profile"] == "staging"
    assert ev["success"] is True
    assert ev["details"] == "3 vars injected"
    assert "timestamp" in ev


def test_record_failure_event():
    record_event("delete", "prod", success=False, details="profile not found")
    events = read_events()
    assert events[0]["success"] is False


def test_multiple_events_appended():
    for i in range(5):
        record_event("set", f"profile_{i}")
    events = read_events()
    assert len(events) == 5


def test_read_events_filter_by_profile():
    record_event("set", "dev")
    record_event("inject", "prod")
    record_event("export", "dev")
    dev_events = read_events(profile="dev")
    assert len(dev_events) == 2
    assert all(e["profile"] == "dev" for e in dev_events)


def test_read_events_limit():
    for i in range(20):
        record_event("set", "dev")
    events = read_events(limit=10)
    assert len(events) == 10


def test_read_events_empty_log():
    events = read_events()
    assert events == []


def test_clear_log():
    record_event("set", "dev")
    record_event("inject", "dev")
    clear_log()
    events = read_events()
    assert events == []


def test_clear_log_no_file_does_not_raise():
    # Should not raise even if log does not exist yet
    clear_log()

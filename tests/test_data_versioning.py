from data_versioning import create_data_versioning, create_audit_trail
import pytest

def test_add_version():
    data_versioning = create_data_versioning()
    data = {"key": "value"}
    data_versioning.add_version(data)
    assert len(data_versioning.get_audit_trail()) == 1
    assert data_versioning.get_version(1).data == data

def test_get_version():
    data_versioning = create_data_versioning()
    data = {"key": "value"}
    data_versioning.add_version(data)
    version = data_versioning.get_version(1)
    assert version.version == 1
    assert version.data == data

def test_get_audit_trail():
    data_versioning = create_data_versioning()
    data = {"key": "value"}
    data_versioning.add_version(data)
    audit_trail = data_versioning.get_audit_trail()
    assert len(audit_trail) == 1
    assert audit_trail[0].data == data

def test_log_event():
    audit_trail = create_audit_trail()
    event = "Test event"
    audit_trail.log_event(event)
    assert len(audit_trail.get_log()) == 1
    assert audit_trail.get_log()[0] == event

def test_get_log():
    audit_trail = create_audit_trail()
    event = "Test event"
    audit_trail.log_event(event)
    log = audit_trail.get_log()
    assert len(log) == 1
    assert log[0] == event

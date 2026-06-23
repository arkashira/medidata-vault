import pytest
from medidata_vault import MedidataVault, Version, AuditLog

def test_create_version():
    vault = MedidataVault()
    creator = "test_creator"
    data = {"key": "value"}
    version = vault.create_version(creator, data)
    assert version.id == "1"
    assert version.creator == creator
    assert version.timestamp is not None
    assert version.data == data

def test_get_versions():
    vault = MedidataVault()
    creator = "test_creator"
    data = {"key": "value"}
    vault.create_version(creator, data)
    versions = vault.get_versions()
    assert len(versions) == 1
    assert versions[0].id == "1"
    assert versions[0].creator == creator
    assert versions[0].timestamp is not None
    assert versions[0].data == data

def test_revert_to_version():
    vault = MedidataVault()
    creator = "test_creator"
    data = {"key": "value"}
    version = vault.create_version(creator, data)
    new_version = vault.revert_to_version(version.id)
    assert new_version.id == "2"
    assert new_version.creator == "system"
    assert new_version.timestamp is not None
    assert new_version.data == data

def test_get_audit_log():
    vault = MedidataVault()
    creator = "test_creator"
    data = {"key": "value"}
    vault.create_version(creator, data)
    audit_log = vault.get_audit_log()
    assert len(audit_log) == 1
    assert audit_log[0].version_id == "1"
    assert audit_log[0].action == "create"
    assert audit_log[0].timestamp is not None

def test_revert_to_non_existent_version():
    vault = MedidataVault()
    with pytest.raises(ValueError):
        vault.revert_to_version("1")

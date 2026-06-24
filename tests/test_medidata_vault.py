import pytest
from datetime import datetime
from medidata_vault import MedidataVault, ShareLink

def test_share_dataset():
    vault = MedidataVault()
    vault.add_dataset("dataset1")
    share_link = vault.share_dataset("dataset1", "viewer")
    assert share_link.role == "viewer"
    assert share_link.expires_at > datetime.now()
    assert share_link.token in vault.share_links

def test_revoke_share_link():
    vault = MedidataVault()
    vault.add_dataset("dataset1")
    share_link = vault.share_dataset("dataset1", "viewer")
    vault.revoke_share_link(share_link.token)
    assert share_link.token not in vault.share_links

def test_get_share_link():
    vault = MedidataVault()
    vault.add_dataset("dataset1")
    share_link = vault.share_dataset("dataset1", "viewer")
    retrieved_share_link = vault.get_share_link(share_link.token)
    assert retrieved_share_link == share_link

def test_send_email():
    vault = MedidataVault()
    vault.add_dataset("dataset1")
    share_link = vault.share_dataset("dataset1", "viewer")
    vault.send_email("test@example.com", share_link.token)
    # No assertion, just checking it runs without error

def test_share_dataset_dataset_not_found():
    vault = MedidataVault()
    with pytest.raises(ValueError):
        vault.share_dataset("dataset1", "viewer")

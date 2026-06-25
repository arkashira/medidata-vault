from medi_data_vault import MedidataVault, Query, User, Role

def test_check_query_phi_leakage():
    vault = MedidataVault()
    user = User(1, Role.RESEARCHER)
    query = Query(1, user, ['name', 'age'], ['name'])
    assert not vault.check_query(query)
    assert len(vault.get_audit_logs()) == 1
    assert vault.get_audit_logs()[0]['decision'] == 'BLOCKED'

def test_check_query_no_phi_leakage():
    vault = MedidataVault()
    user = User(1, Role.RESEARCHER)
    query = Query(1, user, ['age', 'height'], ['name'])
    assert vault.check_query(query)
    assert len(vault.get_audit_logs()) == 1
    assert vault.get_audit_logs()[0]['decision'] == 'ALLOWED'

def test_check_query_phi_access_role():
    vault = MedidataVault()
    user = User(1, Role.PHI_ACCESS)
    query = Query(1, user, ['name', 'age'], ['name'])
    assert vault.check_query(query)
    assert len(vault.get_audit_logs()) == 1
    assert vault.get_audit_logs()[0]['decision'] == 'ALLOWED'

import pytest
from medidata_vault import MedidataVault, QueryResult

def test_add_dataset():
    vault = MedidataVault()
    uuid = "123"
    data = [{"name": "John", "age": "30"}, {"name": "Jane", "age": "25"}]
    vault.add_dataset(uuid, data)
    assert uuid in vault.datasets

def test_query():
    vault = MedidataVault()
    uuid = "123"
    data = [{"name": "John", "age": "30"}, {"name": "Jane", "age": "25"}]
    vault.add_dataset(uuid, data)
    query = "SELECT * FROM dataset"
    query_result = vault.query(uuid, query)
    assert isinstance(query_result, QueryResult)
    assert query_result.columns == ["name", "age"]
    assert query_result.rows == [["John", "30"], ["Jane", "25"]]

def test_query_dataset_not_found():
    vault = MedidataVault()
    uuid = "123"
    query = "SELECT * FROM dataset"
    with pytest.raises(ValueError):
        vault.query(uuid, query)

def test_to_json():
    vault = MedidataVault()
    query_result = QueryResult(["name", "age"], [["John", "30"], ["Jane", "25"]])
    json_result = vault.to_json(query_result)
    assert json_result == '{"columns": ["name", "age"], "rows": [["John", "30"], ["Jane", "25"]]}'

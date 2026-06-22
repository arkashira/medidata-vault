import json
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class QueryResult:
    columns: List[str]
    rows: List[List[str]]

class MedidataVault:
    def __init__(self):
        self.datasets = {}

    def add_dataset(self, uuid: str, data: List[Dict[str, str]]):
        self.datasets[uuid] = data

    def query(self, uuid: str, query: str) -> QueryResult:
        if uuid not in self.datasets:
            raise ValueError("Dataset not found")

        data = self.datasets[uuid]
        columns = list(data[0].keys())
        rows = [[row[column] for column in columns] for row in data]

        # Simulate query execution
        query_result = QueryResult(columns, rows)
        return query_result

    def to_json(self, query_result: QueryResult) -> str:
        return json.dumps({
            "columns": query_result.columns,
            "rows": query_result.rows
        })

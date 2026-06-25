import json
from dataclasses import dataclass
from enum import Enum
from typing import List

class Role(Enum):
    RESEARCHER = 1
    PHI_ACCESS = 2

@dataclass
class User:
    id: int
    role: Role

@dataclass
class Query:
    id: int
    user: User
    select_columns: List[str]
    phi_columns: List[str]

class MedidataVault:
    def __init__(self):
        self.audit_logs = []
        self.phi_columns = ['name', 'email', 'phone']

    def check_query(self, query: Query):
        if any(column in query.select_columns for column in query.phi_columns):
            if query.user.role != Role.PHI_ACCESS:
                self.audit_logs.append({
                    'query_id': query.id,
                    'decision': 'BLOCKED',
                    'reason': 'PHI leakage detected and user does not have PHI Access role'
                })
                return False
            else:
                self.audit_logs.append({
                    'query_id': query.id,
                    'decision': 'ALLOWED',
                    'reason': 'PHI leakage detected but user has PHI Access role'
                })
        else:
            self.audit_logs.append({
                'query_id': query.id,
                'decision': 'ALLOWED',
                'reason': 'No PHI leakage detected'
            })
        return True

    def get_audit_logs(self):
        return self.audit_logs

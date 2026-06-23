import json
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

@dataclass
class Version:
    id: str
    creator: str
    timestamp: str
    data: Dict

@dataclass
class AuditLog:
    version_id: str
    action: str
    timestamp: str

class MedidataVault:
    def __init__(self):
        self.versions = []
        self.audit_log = []

    def create_version(self, creator: str, data: Dict) -> Version:
        version_id = str(len(self.versions) + 1)
        version = Version(version_id, creator, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data)
        self.versions.append(version)
        self.audit_log.append(AuditLog(version_id, "create", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        return version

    def get_versions(self) -> List[Version]:
        return self.versions

    def revert_to_version(self, version_id: str) -> Version:
        for version in self.versions:
            if version.id == version_id:
                new_version_id = str(len(self.versions) + 1)
                new_version = Version(new_version_id, "system", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), version.data)
                self.versions.append(new_version)
                self.audit_log.append(AuditLog(new_version_id, "revert", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                return new_version
        raise ValueError("Version not found")

    def get_audit_log(self) -> List[AuditLog]:
        return self.audit_log

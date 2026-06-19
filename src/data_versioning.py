import json
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DataVersion:
    version: int
    data: dict
    timestamp: str

class DataVersioning:
    def __init__(self):
        self.versions = []

    def add_version(self, data):
        version = len(self.versions) + 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.versions.append(DataVersion(version, data, timestamp))

    def get_version(self, version_number):
        for version in self.versions:
            if version.version == version_number:
                return version
        return None

    def get_audit_trail(self):
        return self.versions

class AuditTrail:
    def __init__(self):
        self.log = []

    def log_event(self, event):
        self.log.append(event)

    def get_log(self):
        return self.log

def create_data_versioning():
    return DataVersioning()

def create_audit_trail():
    return AuditTrail()

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class ShareLink:
    role: str
    expires_at: datetime
    token: str

class MedidataVault:
    def __init__(self):
        self.datasets = {}
        self.share_links = {}

    def share_dataset(self, dataset_id: str, role: str) -> ShareLink:
        if dataset_id not in self.datasets:
            raise ValueError("Dataset not found")
        token = self.generate_token()
        expires_at = datetime.now() + timedelta(days=30)
        share_link = ShareLink(role, expires_at, token)
        self.share_links[token] = share_link
        return share_link

    def generate_token(self) -> str:
        import secrets
        return secrets.token_urlsafe(16)

    def revoke_share_link(self, token: str) -> None:
        if token in self.share_links:
            del self.share_links[token]

    def get_share_link(self, token: str) -> Optional[ShareLink]:
        return self.share_links.get(token)

    def send_email(self, email: str, token: str) -> None:
        # Simulate sending an email
        print(f"Sending email to {email} with token {token}")

    def add_dataset(self, dataset_id: str) -> None:
        self.datasets[dataset_id] = True

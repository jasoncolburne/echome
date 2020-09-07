import time
import logging
import hvac
from backend.config import AppConfig

class Vault:
    client = None

    def __init__(self):
        config = AppConfig()
        self.client = hvac.Client(
            url=config.Vault().addr, 
            token=config.Vault().token
        )
    
    def store_sshkey(self, mount_point:str, path_name:str, key:str):

        self.client.secrets.kv.v2.create_or_update_secret(
            mount_point=mount_point,
            path=path_name,
            secret={
                "private_key": key
            },
        )
    
    def create_policy(self, policy:str, name:str):
        return self.client.sys.create_or_update_policy(
            name=name,
            policy=policy,
        )
    
    def generate_temp_token(self, policies:list, lease='1h'):
        return self.client.create_token(
            policies=policies, 
            lease=lease, 
            renewable=False
        )
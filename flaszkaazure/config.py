import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://flaszkadb.documents.azure.com:443/'),
    'master_key': os.environ.get("database_master_key", "dev"),
    'database_id': os.environ.get('COSMOS_DATABASE', 'flaszkaDb'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'links'),
}
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
class AzureBlobClient:
    def __init__(self) -> None:
        self.account_url = "https://<storageaccountname>.blob.core.windows.net" 
        self.default_credential = DefaultAzureCredential()

    # def auth(self):
    #     account_url = "https://<storageaccountname>.blob.core.windows.net"
    #     default_credential = DefaultAzureCredential()

    #     # Create the BlobServiceClient object
    #     blob_service_client = BlobServiceClient(account_url, credential=default_credential)
    #     pass

    def write_to_blob(self, path, data):
        blob_service_client = BlobServiceClient(self.account_url, credential=self.default_credential)
        blob_client = blob_service_client.get_blob_client(container="container_name", blob=path)
        blob_client.upload_blob(data)

        pass

    def save_on_local(self, name, data):
        
        if type(data) == str:
            with open(f"files/{name}", 'w') as file:
                file.write(data)
        else:
            with open(f"files/{name}", 'wb') as file:
                file.write(data)

    


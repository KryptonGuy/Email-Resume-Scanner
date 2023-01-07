# import logging
# import os
# from azure_storage_logging.handlers import BlobStorageRotatingFileHandler

# azure_storage = os.environ.get('AZURE_STORAGE_NAME', None)
# azure_storage_key = os.environ.get('AZURE_STORAGE_KEY', None)

# if azure_storage is not None:
#     lg.info('Azure storage configured. Logging to Azure storage location ' + os.environ['AZURE_STORAGE_NAME'])
#     azure_blob_handler = BlobStorageRotatingFileHandler(
#        filename='service.log', 
#        account_name=azure_storage,
#        account_key=azure_storage_key,
#        maxBytes=5,
#        container=name+'-log')
#     azure_blob_handler.setLevel(logging.INFO)
#     azure_blob_handler.setFormatter(log_formatter)
#     lg.addHandler(azure_blob_handler)
# else:
#     lg.info('Azure storage not configured. Logging to default location')


import logging

def getLogger(name):

    logger = logging.getLogger(name)

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(message)s')
    file_handler = logging.FileHandler('email_processing.log')

    # add formatter to handler
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # add handler to logger
    logger.addHandler(handler)
    logger.addHandler(file_handler)

    return logger
# import logging
# import os
# removed due to issue with azure-storage dependency
# https://github.com/michiya/azure-storage-logging/issues/6
# from azure_storage_logging.handlers import BlobStorageRotatingFileHandler

# name = 'ms-calendar' # azure storgate container name = name + '-log'

# lg = logging.getLogger('service_logger')
# logging.basicConfig(filename='email_processing.log', encoding='utf-8', level=logging.INFO)

# lg.setLevel(logging.INFO)
# log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(message)s')

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

# def log(level, msg):
#     log_function = {
#         'DEBUG': lg.debug,
#         'INFO': lg.info,
#         'WARNING': lg.warn,
#         'ERROR': lg.error
#     }
#     if level not in log_function.keys():
#         raise ValueError('Logging level ' + level + ' not defined; use "DEBUG", "INFO", "WARNING" or "ERROR".')
#     log_function[level](msg)


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
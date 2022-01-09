## Stepik client

This module contains Stepik client ``StepikClient`` implementation.

### Supported requests

Implementation was based on open [API](https://stepik.org/api/docs/) provided by Stepik.

#### Usage

1. Create application in https://stepik.org/oauth2/applications/
2. Set your client id and secret to environment variables `STEPIK_CLIENT_ID` and `STEPIK_CLIENT_SECRET`
3. Run [run_data_collection.py](../run_data_collection.py) setting platform parameter to `stepik` (before make sure you 
   have become familiar with [README.md](../README.md))

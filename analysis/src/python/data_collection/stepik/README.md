## Stepik client

This module contains Stepik client ``StepikClient`` implementation.

### Supported requests

Implementation was based on open [API](https://stepik.org/api/docs/) provided by Stepik.

#### Usage
1. Create application in https://stepik.org/oauth2/applications/
2. Set your client id and secret to environment variables `STEPIK_CLIENT_ID` and `STEPIK_CLIENT_SECRET`
3. Run `python3 stepik_client.py` with following arguments:
```
usage: stepik_client.py [-h] --object {course,search-result} [--query QUERY] [--ids IDS [IDS ...]]

required arguments:
--object {course,search-result} 
                        requested objects' type

optional arguments:
  -h, --help            show this help message and exit
  --query QUERY         query for search-results request
  --ids IDS [IDS ...]   id of required objects
```

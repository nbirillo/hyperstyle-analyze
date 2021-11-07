## Stepik client

This module contains Stepik client ``StepikClient`` implementation.

### Supported requests

Implementation was based on open [API](https://stepik.org/api/docs/) provided by Stepik.

#### Usage

1. Create application in https://stepik.org/oauth2/applications/
2. Set your client id and secret to environment variables `STEPIK_CLIENT_ID` and `STEPIK_CLIENT_SECRET`
3. Run `python3 stepik_client.py` with following arguments:

```
usage: stepik_client.py [-h] --object OBJECT [--ids [IDS ...]] [--count COUNT] [--output OUTPUT]

required arguments:
  --object OBJECT  objects to request from stepik platform (can be defaults like `step`, `user` of custom like `java`)
  
optional arguments:
  -h, --help       show this help message and exit
  --ids [IDS ...]  ids of requested objects
  --count COUNT    count of requested objects
  --output OUTPUT  path to directory where to save the results
```

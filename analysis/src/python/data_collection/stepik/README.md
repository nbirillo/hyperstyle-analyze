## Stepik client

This module contains Stepik client ``StepikClient`` implementation.

### Supported requests

Implementation was based on open [API](https://stepik.org/api/docs/) provided by Stepik.

#### Usage

1. Create application in https://stepik.org/oauth2/applications/
2. Set your client id and secret to environment variables `STEPIK_CLIENT_ID` and `STEPIK_CLIENT_SECRET`
3. Run `python3 run_data_collection.py --platform stepik` with following arguments:

```
usage: run_data_collection.py [-h] --platform stepik --object OBJECT [--ids [IDS ...]] [--ids_from_file IDS_FROM_FILE] [--ids_from_column IDS_FROM_COLUMN]
                              [--count COUNT] [--output OUTPUT]
                              
required arguments:
  --platform PLATFORM, -p PLATFORM
                        platform to collect data from
  --object OBJECT, -o OBJECT
                        objects to request from platform (can be defaults like `step`, `user` of custom like `java`)

optional arguments:
  -h, --help            show this help message and exit
  --ids [IDS ...], -i [IDS ...]
                        ids of requested objects
  --ids_from_file IDS_FROM_FILE, -f IDS_FROM_FILE
                        csv file to get ids from
  --ids_from_column IDS_FROM_COLUMN, -c IDS_FROM_COLUMN
                        column in csv file to get ids from
  --count COUNT, -cnt COUNT
                        count of requested objects
  --output OUTPUT, -out OUTPUT
                        path to directory where to save the results


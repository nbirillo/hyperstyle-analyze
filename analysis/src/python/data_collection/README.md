## Stepik and Hyperskill data collection

This module contains client for Stepik and Hyperskill. This educational platforms provides open APIs with information
about platforms' objects such as steps, courses, tracks, projects, etc.

```shell
usage: run_data_collection.py [-h] --platform PLATFORM --object OBJECT [--ids [IDS ...]] [--ids_from_file IDS_FROM_FILE] [--ids_from_column IDS_FROM_COLUMN]
                              [--count COUNT] [--output OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  --platform PLATFORM, -p PLATFORM
                        platform to collect data from (`hyperskill` or `stepik`)
  --object OBJECT, -o OBJECT
                        objects to request from platform (can be defaults like `step`, `user` of custom like `java`)
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

```
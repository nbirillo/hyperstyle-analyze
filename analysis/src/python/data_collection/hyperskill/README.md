## Hyperskill client

This module contains Hyperskill client ``HyperskillClient`` implementation.

### Supported requests

Implementation was based on open [API](https://hyperskill.org/api/docs/) provided by Hyperskill.

#### Usage

1. Create application in https://hyperskill.org/oauth2/applications/
2. Set your client id and secret to environment variables `HYPERSKILL_CLIENT_ID` and `HYPERSKILL_CLIENT_SECRET`
3. Run `python3 hyperskill_client.py` with following arguments:

```
usage: hyperskill_client.py [-h] --object OBJECT [--ids [IDS ...]] [--count COUNT] [--output OUTPUT]

required arguments:
  --object OBJECT  object name or query to get from hyperskill

optional arguments:
  -h, --help       show this help message and exit
  --object OBJECT  object name or query to get from hyperskill
  --ids [IDS ...]  ids of requested objects
  --count COUNT    count of requested objects
  --output OUTPUT  path to directory where to save the results

```

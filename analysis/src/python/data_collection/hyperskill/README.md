## Hyperskill client

This module contains Hyperskill client ``HyperskillClient`` implementation.

### Supported requests

Implementation was based on open [API](https://hyperskill.org/api/docs/) provided by Hyperskill.

#### Usage

1. Create application in https://hyperskill.org/oauth2/applications/
2. Set your client id and secret to environment variables `HYPERSKILL_CLIENT_ID` and `HYPERSKILL_CLIENT_SECRET`
3. Run [run_data_collection.py](../run_data_collection.py) setting platform parameter to `hyperskill`

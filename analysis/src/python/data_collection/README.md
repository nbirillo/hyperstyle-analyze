## Stepik and Hyperskill data collection

This module contains client for Stepik and Hyperskill. This educational platforms provides open APIs with information
about platforms' objects such as steps, courses, tracks, projects, etc.

To get data from the education platforms, configure and run [run_data_collection.py](run_data_collection.py) 
from command line with following arguments:
### Configure:

1. For platforms api usage you need to create authorize. Create an application in [https://hyperskill.org/oauth2/applications/](https://hyperskill.org/oauth2/applications/) for 
   hyperskill client usage and in [https://stepik.org/oauth2/applications/](https://stepik.org/oauth2/applications/) for stepik:
   * `Client type` --`Confidentional`
   * `Authorization grant type` --`Authorization Code`
   * `Authorization grant type` --`http://localhost:8000`
2. After application created you will see your `Client id` and `Client secret`. Set them to environment variables 
   `HYPERSKILL_CLIENT_ID` and `HYPERSKILL_CLIENT_SECRET` for hyperskill or `STEPIK_CLIENT_ID` and `STEPIK_CLIENT_SECRET`.
   
For more information about api go to [hyperskill api documentation](https://hyperskill.org/api/docs/) or [stepik api documentation](https://stepik.org/api/docs/).
   
### Run:

**Required arguments:**

| Argument | Description |
|----------|-------------|
|**platform**| Platform to collect data from (can be `hyperskill` or `stepik`). |
|**object**| Objects to request from platform (can be defaults or custom. Custom is any string you want to find. Default objects for `hyperskill` client are `step`, `track`, `project`, `topic`, `user`, `submission` and for `stepik` client are `step`, `lesson`, `course`, `user`, `submission`. |

**Optional arguments:**

| Argument | Description |
|----------|-------------|
| **&#8209;&#8209;ids** | List of ids of requested objects. |
| **&#8209;&#8209;ids_from_file** | File with `.csv` extension to get ids from it's column, which name is defined using **&#8209;&#8209;ids_from_column** flag. |
| **&#8209;&#8209;ids_from_column** | Column in `.csv` file defined by **&#8209;&#8209;ids_from_file** to get ids from. |
| **&#8209;&#8209;count** | Count of requested objects. |
| **&#8209;o**, **&#8209;&#8209;output** | Path to directory where to save the results. |

For using API you need to be authorized in Hyperskill/Stepik. When the information gathering will start, you will see the authorization page.
Check your `name` and `user id` and press `Authorize` button. 

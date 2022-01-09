## Stepik and Hyperskill data collection

This module contains client for Stepik and Hyperskill. This educational platforms provides open APIs with information
about platforms' objects.
This module use platforms' APIs to extract information about following entities from educational platforms:

[Hyperskill](https://hyperskill.org/api/docs/): 

| Entity | Description |
|----------|-------------|
| step | Task where user needs to solve a problem or answer a question. |
| topic | Theme or knowledge area of steps. Several steps can be related to one topic. Topics have hierarchy (every topic have several prerequisite topics) and form the topics tree. |
| track | Series of steps to get knowledge on some specific theme (programming language, data analysis, ect.). |
| project | Big task with supportive steps to reach the final result and learn how to implement it. |  
| user | Registered people on platform. |
| submission | User's attempt to solve the step's task and platform's feedback on this solution. |

[Stepik](https://stepik.org/api/docs/):

| Entity | Description |
|----------|-------------|
| step | Task where user needs to solve a problem or answer a question. |
| lesson | Series os steps grouped in one section. |
| course | Series os lessons. | 
| user | Registered people on platform. |
| submission | User's attempt to solve the step's task and platform's feedback on this solution. |

To get data from the education platforms, configure and run [run_data_collection.py](run_data_collection.py) 
from command line with following arguments:
### Configure:

1. For platforms api usage you need to create authorize. Create an application in [https://hyperskill.org/oauth2/applications/](https://hyperskill.org/oauth2/applications/) for 
   hyperskill client usage and in [https://stepik.org/oauth2/applications/](https://stepik.org/oauth2/applications/) for stepik:
   * `Client type` --`Confidentional`
   * `Authorization grant type` --`Authorization Code`
   * `Authorization grant type` --`http://localhost:{port}` (by default port 8000, but you can put any and not forget to set it in arguments of run script)
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
| **&#8209;&#8209;port** | Port to run authorization server on (must be the same as you have put to your application information in second step of Configure section). |

For using API you need to be authorized in Hyperskill/Stepik. When the information gathering will start, you will see the authorization page.
Check your `name` and `user id` and press `Authorize` button. 

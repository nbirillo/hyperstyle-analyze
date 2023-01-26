## Stepik and Hyperskill data collection

This module contains the client for Stepik and Hyperskill. These educational platforms provide open APIs with information
about platforms' objects.
This module uses platforms' APIs to extract the information about the following entities from educational platforms:

[Hyperskill](https://hyperskill.org/api/docs/): 

| Entity | Description                                                                                                                                                                |
|----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| step | Task where a user needs to solve a problem or answer a question.                                                                                                           |
| topic | Theme or knowledge area of steps. Several steps can be related to one topic. Topics have hierarchy (every topic has several prerequisite topics) and form the topics tree. |
| track | Series of steps to get knowledge on some specific theme (programming language, data analysis, ect.).                                                                       |
| project | Big task with supportive steps to reach the final result and learn how to implement it.                                                                                    |  
| user | Registered people on platform.                                                                                                                                             |
| submission | User's attempt to solve the step's task and platform's feedback on this solution.                                                                                          |

[Stepik](https://stepik.org/api/docs/):

| Entity | Description                                                                       |
|----------|-----------------------------------------------------------------------------------|
| step | Task where a user needs to solve a problem or answer a question.                  |
| lesson | Series of steps grouped in one section.                                           |
| course | Series of lessons.                                                                | 
| user | Registered people on platform.                                                    |
| submission | User's attempt to solve the step's task and platform's feedback on this solution. |

To get the data from the education platforms, configure and run [run_data_collection.py](run_data_collection.py) 
from command line with following arguments:
### Configure:

1. For platforms API usage, you need to create authorization. Create an application in [https://hyperskill.org/oauth2/applications/](https://hyperskill.org/oauth2/applications/) for 
   using the hyperskill client and in [https://stepik.org/oauth2/applications/](https://stepik.org/oauth2/applications/) to use stepik:
   * `Client type` --`Confidentional`
   * `Authorization grant type` --`Authorization Code`
   * `Authorization grant type` --`http://localhost:{port}` (by default, port 8000, but you can put any and not forget to set it in arguments of the `run` script)
2. After the application is created, you will see your `Client id` and `Client secret`. Set them to environment variables 
   `HYPERSKILL_CLIENT_ID` and `HYPERSKILL_CLIENT_SECRET` for hyperskill or `STEPIK_CLIENT_ID` and `STEPIK_CLIENT_SECRET`.
   
For more information about the API, go to [hyperskill API documentation](https://hyperskill.org/api/docs/) or [stepik API documentation](https://stepik.org/api/docs/).
   
### Run:

**Required arguments:**

| Argument | Description                                                                                                                                                                                                                                                                                  |
|----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|**platform**| Platform to collect the data from (can be `hyperskill` or `stepik`).                                                                                                                                                                                                                         |
|**object**| Objects to request from the platform (can be defaults or custom). Custom is any string you want to find. Default objects for `hyperskill` client are `step`, `track`, `project`, `topic`, `user`, `submission` and for `stepik` client are `step`, `lesson`, `course`, `user`, `submission`. |

**Optional arguments:**

| Argument | Description                                                                                                                                         |
|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| **&#8209;&#8209;ids** | List of ids of requested objects.                                                                                                                   |
| **&#8209;&#8209;ids_from_file** | File with a `.csv` extension to get ids from its column, the name of which is defined using the **&#8209;&#8209;ids_from_column** flag.             |
| **&#8209;&#8209;ids_from_column** | Column in the`.csv` file defined by **&#8209;&#8209;ids_from_file**, to get ids from.                                                               |
| **&#8209;&#8209;count** | Count of requested objects.                                                                                                                         |
| **&#8209;o**, **&#8209;&#8209;output** | Path to the directory to save the results to.                                                                                                       |
| **&#8209;&#8209;port** | Port to run the authorization server on (must be the same as you have put in your application information in the second step of Configure section). |

To use the API, you need to be authorized in Hyperskill/Stepik. When the information gathering starts, you will see the authorization page.
Check your `name` and `user id` and press the `Authorize` button. 

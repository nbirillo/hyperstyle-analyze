## Hyperskill client

This module contains Hyperskill client ``HyperskillClient`` implementation.

### Supported requests

Implementation was based on open [API](https://hyperskill.org/api/docs/) provided by Hyperskill.

#### Usage
1. Run `python3 hyperskill_client.py` with following arguments:
```
usage: hyperskill_client.py [-h] --object {project,topic,step,search-result,track} [--query QUERY] [--topic-id TOPIC_ID] [--ids [IDS ...]]

required arguments:
  --object {project,topic,step,search-result,track}
                        path to output dir with result
                        
optional arguments:
  -h, --help            show this help message and exit
  --object {project,topic,step,search-result,track}
                        path to output dir with result
  --query QUERY         query for search_results request
  --topic-id TOPIC_ID   topic id for steps request
  --ids [IDS ...]       topic id for steps request

```

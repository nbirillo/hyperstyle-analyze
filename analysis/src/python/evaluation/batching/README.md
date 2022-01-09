# Module for batching dataset processing

Module for batching hyperstyle processing of large code base.
To batch hyperstyle run you need to:
1. Create yaml configuration file where set:
    * project_path -- path to project root directory 
    * script_path -- path to script from project root, which perform data pressing
    * script_args -- script arguments to run with
    * script_flags -- script flags to run with
    Example:
    ```yaml
    project_path:
        path/to/project
    script_path:
        path/to/script
    script_args:
        - arg1
        - arg2
    script_flags:
      flag1: value1
      flag2: value2
    ```
2. Run [batch_processing.py](batch_processing.py) with arguments
   
   Positional arguments:
   
   | Argument | Description |
   |--- | --- |
   |**input**| Path to the csv file with data to process. |
   |**output**| Path to the output directory. |
   |**config**| Path to the script config to run under batching. |

   Optional arguments:
   
   | Argument | Description |
   |--- | --- |
   |**&#8209;&#8209;batch-size**| Batch size for data processing (1000 by default). |
   |**&#8209;&#8209;start-from**| Index of batch to start processing from (0 by default). |

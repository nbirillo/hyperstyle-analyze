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
2. Run batch_processing.py 
   ```shell
   python3 batch_processing.py [-h] [--batch-size [BATCH_SIZE]] [--start-from [START_FROM]] input output config
   
   positional arguments:
     input                 path to the csv file with data to process
     output                path to the output directory
     config                path to the script config to run under batching
   
   optional arguments:
     -h, --help            show this help message and exit
     --batch-size [BATCH_SIZE]
                           batch size for data
     --start-from [START_FROM]
                           index of batch to start processing from
   
   ```
         
# Qodana evaluation

This module allows running the [Qodana](https://github.com/JetBrains/Qodana) tool on a `xlsx` or `csv` table to get code quality for all code fragments. 
The dataset must contain at least three columns: 
- `id` - is a unique solution number
- `code` - solution code
- `lang`- language in which the code is written in the `code` column. Must belong to one of the following values: `java7`, `java8`, `java9`, `java11`, `java15`, `java17`, `python3`.

- For this evaluation you need to download docker images `jetbrains/qodana` and `jetbrains/qodana-python:2022.1-eap` (with qodana tool):
```shell
docker pull jetbrains/qodana
docker pull jetbrains/qodana-python:2022.2-eap
```
As qodana for python is eap, please check [here](https://www.jetbrains.com/help/qodana/qodana-python.html) dockers current version.

Output file is a new `xlsx` or `csv` file with the all columns from the input file and one additional:
- `qodana_issues` - json string with full traceback of [Qodana](https://github.com/JetBrains/Qodana) code quality analysis tool.

- For example `qodana_issues` field on solution with id=2637248 looks like:

```json
{
  "version": "3",
  "listProblem": [
    {
      "tool": "Code Inspection",
      "category": "Resource management",
      "type": "I/O resource opened but not safely closed",
      "severity": "High",
      "comment": "'Scanner' should be opened in front of a 'try' block and closed in the corresponding 'finally' block",
      "detailsInfo": "Reports I/O resources that are not safely closed. I/O resources checked by this inspection include `java.io.InputStream`, `java.io.OutputStream`, `java.io.Reader`, `java.io.Writer`, `java.util.zip.ZipFile`, `java.io.Closeable` and `java.io.RandomAccessFile`.\n\n\nI/O resources wrapped by other I/O resources are not reported, as the wrapped resource will be closed by the wrapping resource.\n\n\nBy default, the inspection assumes that the resources can be closed by any method with\n'close' or 'cleanup' in its name.\n\n**Example:**\n\n\n      void save() throws IOException {\n        FileWriter writer = new FileWriter(\"filename.txt\"); //warning\n        writer.write(\"sample\");\n      }\n\n\nUse the following options to configure the inspection:\n\n* List I/O resource classes that do not need to be closed and should be ignored by this inspection.\n* Whether an I/O resource is allowed to be opened inside a `try`block. This style is less desirable because it is more verbose than opening a resource in front of a `try` block.\n* Whether the resource can be closed by any method call with the resource passed as argument.",
      "sources": [
        {
          "type": "file",
          "path": "src/main/java/solution_2637248/Main.java",
          "language": "JAVA",
          "line": 5,
          "offset": 31,
          "length": 7,
          "code": {
            "startLine": 3,
            "length": 7,
            "offset": 88,
            "surroundingCode": "class Main {\n    public static void main(String[] args) {\n        Scanner scanner = new Scanner(System.in);\n        double num1 = scanner.nextDouble()/scanner.nextDouble();\n        System.out.print(num1);"
          }
        }
      ],
      "attributes": {
        "inspectionName": "IOResource"
      }
    },
    ...
  ]
}
```

# Usage
Run the [evaluate.py](evaluate.py) with the arguments from command line.

### Required arguments

`solutions_file_path` — path to xlsx-file or csv-file with code samples to inspect.

Optional arguments:

| Argument                                             | Description                                                                                                             |
|------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| **&#8209;o**, **&#8209;&#8209;output**               | Path to the directory where to save evaluation results. Use parent directory of `solutions_file_path` if not specified. |
| **&#8209;td**, **&#8209;&#8209;tmp&#8209;directory** | Path to the directory where to save temporary created files results. Use default if not specified.                      |
| **&#8209;&#8209;with&#8209;custom&#8209;profile**    | Run qodana only in inspections listed in language specific profile.xml.                                                 |


# dumpsearch

A tool for parsing datadumps.

## Install

Install with `pip` using:
```
pip install -r requirements.txt
```
Install with `pipenv` using:
```
pipenv install
```

## Usage

To parse a datadump you need a format file describing the format of the dump. The program can guess the format of the dump given the dump file. It's best to double check if the format is correct before starting to parse.

```
./dumpsearch.py guess dump.txt -f format.json
```

The format file has the following fields:

| Field           | Sample Value       | Explanation |
| --------------- | ------------------ | ----------- |
| `prefixjunk`    | `"prefixend\n"`    | The last chars before the data starts, `""` if the data starts directly.           |
| `suffixjunk`    | `"suffixstart"`    | The first chars after the data ends, `""` if the data ends at the end of the file. |
| `delimiter`     | `":"`              | Delimiter between dump fields.                                                     |
| `linedelimiter` | `"\n"` or `"\r\n"` | Line endings.                                                                      |
| `parseformat`   | `"ueJJJJJJJJhs"`   | Specifies which fields contain which data.                                         |

The `parseformat` field has the following parameters:

| Parameter | Value |
| --------- | ----- |
| e | **E**mail |
| u | **U**sername |
| p | **P**assword |
| h | **H**ash |
| s | **S**alt |
| t | hash**T**ype |
| f | **F**irstname |
| l | **L**astname |
| n | pho**n**e |
| d | **D**umpsource |
| J | **J**unk |

To parse a dump run:

```
./dumpsearch.py parse format.json dump.txt outfile.txt
```

The program will currently dump the data to `outfile.txt` in the following format:

```
e:u:p:h:s:t:f:l:n:d\n
```

TODO: describe mysqlconfig.json

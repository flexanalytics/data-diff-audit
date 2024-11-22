
# Datadiff and Process Validation

## This tool is useful for finding full table differences between a source and a target. In order to utilize the tool:

### Set up your development environment

- clone this repo
- update `.env.template` to `.env` and add the proper source and target URIs in the format provided (specifically the databases and schemas). Make sure to either use the `Password` format or `SSO` format and delete the other one which is not used.

> [!NOTE]
> You will have to urlencode your email address, replacing `name@domain.com` with `name%40domain.com`. If using password auth, you will have to do the same with your password. There are many tools online to do this such as [urlencoder.org](https://www.urlencoder.org/)
- install required libraries with `python -m pip install -r requirements.txt`
   - a virtual environment is recommended prior to installing the project's required packages, and can be created with the following commands

```bash
python -m venv venv
source venv/bin/activate  #(or source venv/Scripts/activate on Windows)
```

- update `config.yml` to include:
   - the tables to compare
   - the key column shared between the tables
   - any where clauses to properly filter the tables
   - the additional columns to compare

> [!NOTE]
> Excluding additional columns in the config will currently only check if the key column is found in both tables, but not if there are different values in any columns between the two tables for each key.
> To compare column values you must add additional columns to the config in the `columns` entry, and their names must match across both tables.

### Run the tool

- run the comparison with `python -m diff`
   - this will compare the 2 tables and output the results to `diff_report.txt`

> [!IMPORTANT]
> Make sure to take a copy of the initial report, as it may be overwritten as you develop.

#### These results can be read as follows:

```sql
{KEY_COLUMN} {COLUMN_VALUE} changes in {TABLE}: {COLUMN1}: -{LEFT_VALUE} +{RIGHT_VALUE}, {COLUMN2}: -{LEFT_VALUE} +{RIGHT_VALUE}
```

For example, in the below where `MY_TABLE` is the table being compared:

```sql
ID 12345 changes in MY_TABLE: COLUMN_1: -670 +'', COLUMN_2: -F1 +''
```

> ID 12345 has a value of 670 in the `COLUMN_1` column in the source table, and a value of `''` in the target table, and a value of `F1` in the `COLUMN_2` column in the source table, and a value of `''` in the target table.

This project would not be possible without [reladiff](https://github.com/erezsh/reladiff)

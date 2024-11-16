
# Datadiff and Process Validation

## This tool is useful for finding full table differences between a source and a target. In order to utilize the tool:

### Set up your development environment

- clone this repo

[Github](https://github.com/flexanalytics/data-diff-audit)

- update `.env.template` to `.env` and add the proper source and target URIs in the format provided (specifically the databases and schemas)
- install required libraries with `python3 -m pip install -r requirements.txt`
   - a virtual environment is recommended prior to installing the project's required packages, and can be created with the following commands

```bash
python3 -m venv venv
source venv/bin/activate  #(or source venv/Scripts/activate on Windows)
```

- update `config.yml` to include:
   - the tables to compare
   - the key column shared between the tables
   - any where clauses to properly filter the tables
   - the additional columns to compare

### Run the tool

- run the comparison with `python3 -m diff`
   - this will compare the 2 tables and output the results to `diff_report.txt`

! Make sure to take a copy of the initial report, as it may be overwritten as you develop.

#### These results can be read as follows:

```sql
{KEY_COLUMN} {COLUMN_VALUE} changes in {TABLE}: {COLUMN1}: -670 +'', {COLUMN2}: -{LEFT_VALUE} +{RIGHT_VALUE}
```

For example, in the below where P`S_SCR_UCOP_EXTR` is the table being compared:

```sql
EMPLID 12345 changes in PS_SCR_UCOP_EXTR: SCR_H050: -670 +'', SCR_H060: -F1 +''
```

> EMPLID 12345 has a value of 670 in the `SCR_H050` column in the source table, and a value of `''` in the target table, and a value of `F1` in the `SCR_H060` column in the source table, and a value of `''` in the target table.

### Verify the results and fine-tune the dbt project logic

- check schema definition file for certification status on any mismatched columns
   - any `meta.certification` with a value of `invalid` is a known issue that needs correcting, and any with either no status or a status of `certified` should be investigated further

```yaml
meta:
    certification:
      status: invalid
      note: Source has 187 rows with a value of 'ABC' that differs from Target value of 'DEF' for 2248
      date: 2024-10-25
```

- check the excel data dictionary for definitions and schema
- verify the difference one id example in both databases
- take a look through the `ais_sqr` codebase to find what logic is used to create the columns
- make changes in dbt code to match the logic found in the source database
- re-build the updated dbt model(s)
- re-run the diff, making sure to only include the updated column(s) in the `config.yml` file
- update the certification status to either note where known issues are occurring (status invalid) or fixes have been applied (status certified)

Continue this process until the diff report is empty!

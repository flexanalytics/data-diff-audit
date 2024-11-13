from __future__ import annotations

import os

import yaml
from dotenv import load_dotenv
from reladiff import connect_to_table
from reladiff import diff_tables

load_dotenv()

SAVE_AS_FILE = "./diff_report.txt"


def replace_env_vars_in_yaml(yaml_data: dict | list | str) -> dict | list | str:
    if isinstance(yaml_data, dict):
        return {k: replace_env_vars_in_yaml(v) for k, v in yaml_data.items()}
    elif isinstance(yaml_data, list):
        return [replace_env_vars_in_yaml(item) for item in yaml_data]
    elif (
        isinstance(yaml_data, str)
        and yaml_data.startswith("${")
        and yaml_data.endswith("}")
    ):
        env_var = yaml_data[2:-1]
        return os.getenv(env_var, yaml_data)
    return yaml_data


with open("config.yml", "r") as file:
    config_data = yaml.safe_load(file)

config = replace_env_vars_in_yaml(config_data)


def generate_diff_report(
    left_conn: str,
    right_conn: str,
    left_table: str,
    right_table: str,
    keys: tuple[str],
    left_where: str = "",
    right_where: str = "",
    extra_columns: tuple[str] = ("",),
) -> dict:
    result: dict[str, list[dict[str, str]]] = {}
    out = {}
    seen = set()

    table1 = connect_to_table(
        left_conn,
        left_table,
        key_columns=keys,
        where=left_where,
        extra_columns=extra_columns,
    )

    table2 = connect_to_table(
        right_conn,
        right_table,
        key_columns=keys,
        where=right_where,
        extra_columns=extra_columns,
    )

    diff = diff_tables(
        table1,
        table2,
        key_columns=keys,
        extra_columns=extra_columns,
        validate_unique_key=False,
    )
    try:
        for k, v in diff:
            if v not in seen:
                seen.add(v)
                result.setdefault(k, []).append(
                    {
                        keys[0]: v[0],
                        **{
                            extra_columns[i]: "''"
                            if v[i + 1] is None
                            else "''"
                            if v[i + 1].strip() == ""
                            else v[i + 1].strip()
                            for i in range(len(extra_columns))
                        },
                    },
                )
    except Exception as e:
        raise e
    out[left_table] = result
    return out


def generate_diff_summary(data) -> str:
    summary = []
    column_totals = {}

    for item in data:
        for key, changes in item.items():
            minus_list = changes.get("-")
            plus_list = changes.get("+")

            if not minus_list and not plus_list:
                return "no differences found!"

            minus_dicts = {list(d.items())[0]: d for d in minus_list}
            plus_dicts = {list(d.items())[0]: d for d in plus_list}

            common_keys = set(minus_dicts.keys()) & set(plus_dicts.keys())
            only_in_minus = set(minus_dicts.keys()) - set(plus_dicts.keys())
            only_in_plus = set(plus_dicts.keys()) - set(minus_dicts.keys())

            for identifier in common_keys:
                minus_dict = minus_dicts[identifier]
                plus_dict = plus_dicts[identifier]

                differences = []
                for col_name in minus_dict.keys():
                    if minus_dict[col_name] != plus_dict[col_name]:
                        differences.append(
                            f"{col_name}: -{minus_dict[col_name]} +{plus_dict[col_name]}",
                        )
                        column_totals[col_name] = column_totals.get(col_name, 0) + 1

                if differences:
                    identifier_key, identifier_value = identifier
                    summary.append(
                        f"{identifier_key} {identifier_value} changes in {key}: "
                        + ", ".join(differences),
                    )

            for identifier in only_in_minus:
                identifier_key, identifier_value = identifier
                summary.append(
                    f"{identifier_key} {identifier_value} removed from {key}: "
                    + ", ".join(
                        f"{col_name}: {value}"
                        for col_name, value in minus_dicts[identifier].items()
                    ),
                )
                for col_name in minus_dicts[identifier].keys():
                    column_totals[col_name] = column_totals.get(col_name, 0) + 1

            for identifier in only_in_plus:
                identifier_key, identifier_value = identifier
                summary.append(
                    f"{identifier_key} {identifier_value} added to {key}: "
                    + ", ".join(
                        f"{col_name}: {value}"
                        for col_name, value in plus_dicts[identifier].items()
                    ),
                )
                for col_name in plus_dicts[identifier].keys():
                    column_totals[col_name] = column_totals.get(col_name, 0) + 1

    # Generate the summary header
    summary_header = "Summary of differences by column:\n"
    summary_header += "\n".join(
        f"{col_name}: {count}" for col_name, count in column_totals.items()
    )
    summary_header += "\n\nDetailed report:\n"

    return summary_header + "\n".join(summary)


def main() -> int:
    final = []
    for t in config["config"]:
        keys = tuple(t["keys"])
        try:
            columns = tuple(t["columns"])
        except KeyError:
            columns = ()
        try:
            left_where = t["left_where"]
        except KeyError:
            left_where = ""
        try:
            right_where = t["right_where"]
        except KeyError:
            right_where = ""
        print(f'diffing {t["left_table"]} and {t["right_table"]}')
        final.append(
            generate_diff_report(
                t["left_conn"],
                t["right_conn"],
                t["left_table"],
                t["right_table"],
                keys,
                left_where,
                right_where,
                columns,
            ),
        )
    report = generate_diff_summary(final)

    with open(SAVE_AS_FILE, "w") as f:
        f.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

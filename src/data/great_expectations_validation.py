import great_expectations as ge
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.core import ExpectationConfiguration
import json
import os


SUITE_NAME = "credit_card_data_suite"


def create_expectation_suite() -> None:
    expectations = []

    context = ge.get_context()
    suite = ExpectationSuite(expectation_suite_name=SUITE_NAME)

    columns_to_exist = [
        "LIMIT_BAL",
        "SEX",
        "EDUCATION",
        "MARRIAGE",
        "AGE",
        "PAY_0",
        "PAY_2",
        "PAY_3",
        "PAY_4",
        "PAY_5",
        "PAY_6",
        "BILL_AMT1",
        "BILL_AMT2",
        "BILL_AMT3",
        "BILL_AMT4",
        "BILL_AMT5",
        "BILL_AMT6",
        "PAY_AMT1",
        "PAY_AMT2",
        "PAY_AMT3",
        "PAY_AMT4",
        "PAY_AMT5",
        "PAY_AMT6",
        "default.payment.next.month",
    ]

    not_null_columns = [
        "LIMIT_BAL",
        "SEX",
        "EDUCATION",
        "MARRIAGE",
        "AGE",
        "default.payment.next.month",
    ]

    int_columns_types = [
        "SEX",
        "EDUCATION",
        "MARRIAGE",
        "AGE",
        "PAY_0",
        "PAY_2",
        "PAY_3",
        "PAY_4",
        "PAY_5",
        "PAY_6",
        "default.payment.next.month",
    ]

    float_columns_types = [
        "LIMIT_BAL",
        "BILL_AMT1",
        "BILL_AMT2",
        "BILL_AMT3",
        "BILL_AMT4",
        "BILL_AMT5",
        "BILL_AMT6",
        "PAY_AMT1",
        "PAY_AMT2",
        "PAY_AMT3",
        "PAY_AMT4",
        "PAY_AMT5",
        "PAY_AMT6",
    ]

    for column in columns_to_exist:
        expectations.append(
            ExpectationConfiguration(
                expectation_type="expect_column_to_exist",
                kwargs={"column": column},
            )
        )

    for column in not_null_columns:
        expectations.append(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_not_be_null",
                kwargs={"column": column},
            )
        )

    for column in int_columns_types:
        expectations.append(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_in_type_list",
                kwargs={"column": column, "type_list": ["int64", "int32", "int16"]},
            )
        )

    for column in float_columns_types:
        expectations.append(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_in_type_list",
                kwargs={"column": column, "type_list": ["float64", "float32"]},
            )
        )

    # Диапазоны
    expectations.append(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={"column": "AGE", "min_value": 18, "max_value": 100},
        )
    )
    expectations.append(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={"column": "LIMIT_BAL", "min_value": 1},
        )
    )
    # Таргет 0/1
    expectations.append(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_in_set",
            kwargs={
                "column": "default.payment.next.month",
                "value_set": [0, 1],
                "result_format": "SUMMARY",
            },
        )
    )
    for exp in expectations:
        suite.add_expectation(exp)

    context.save_expectation_suite(suite, SUITE_NAME)
    return suite


def suite_to_file() -> ExpectationSuite:
    suite = create_expectation_suite()
    context = ge.get_context()
    context.save_expectation_suite(suite, SUITE_NAME)
    
    suite_dir = "gx/expectations"
    os.makedirs(suite_dir, exist_ok=True)
    
    with open(f"{suite_dir}/{SUITE_NAME}.json", "w") as file:
        json.dump(suite.to_json_dict(), file, indent=2)
    
    print(f"Suite сохранён: {suite_dir}/{SUITE_NAME}.json")
    return suite

suite_to_file()

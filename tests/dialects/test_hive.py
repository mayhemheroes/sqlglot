from tests.dialects.test_dialect import Validator


class TestHive(Validator):
    dialect = "hive"

    def test_bits(self):
        self.validate_all(
            "x & 1",
            write={
                "duckdb": "x & 1",
                "presto": "BITWISE_AND(x, 1)",
                "hive": "x & 1",
                "spark": "x & 1",
            },
        )
        self.validate_all(
            "~x",
            write={
                "duckdb": "~x",
                "presto": "BITWISE_NOT(x)",
                "hive": "~x",
                "spark": "~x",
            },
        )
        self.validate_all(
            "x | 1",
            write={
                "duckdb": "x | 1",
                "presto": "BITWISE_OR(x, 1)",
                "hive": "x | 1",
                "spark": "x | 1",
            },
        )
        self.validate_all(
            "x << 1",
            write={
                "duckdb": "x << 1",
                "presto": "BITWISE_ARITHMETIC_SHIFT_LEFT(x, 1)",
                "hive": "x << 1",
                "spark": "SHIFTLEFT(x, 1)",
            },
        )
        self.validate_all(
            "x >> 1",
            write={
                "duckdb": "x >> 1",
                "presto": "BITWISE_ARITHMETIC_SHIFT_RIGHT(x, 1)",
                "hive": "x >> 1",
                "spark": "SHIFTRIGHT(x, 1)",
            },
        )
        self.validate_all(
            "x & 1 > 0",
            write={
                "duckdb": "x & 1 > 0",
                "presto": "BITWISE_AND(x, 1) > 0",
                "hive": "x & 1 > 0",
                "spark": "x & 1 > 0",
            },
        )

    def test_cast(self):
        self.validate_all(
            "1s",
            write={
                "duckdb": "CAST(1 AS SMALLINT)",
                "presto": "CAST(1 AS SMALLINT)",
                "hive": "CAST(1 AS SMALLINT)",
                "spark": "CAST(1 AS SHORT)",
            },
        )
        self.validate_all(
            "1S",
            write={
                "duckdb": "CAST(1 AS SMALLINT)",
                "presto": "CAST(1 AS SMALLINT)",
                "hive": "CAST(1 AS SMALLINT)",
                "spark": "CAST(1 AS SHORT)",
            },
        )
        self.validate_all(
            "1Y",
            write={
                "duckdb": "CAST(1 AS TINYINT)",
                "presto": "CAST(1 AS TINYINT)",
                "hive": "CAST(1 AS TINYINT)",
                "spark": "CAST(1 AS BYTE)",
            },
        )
        self.validate_all(
            "1L",
            write={
                "duckdb": "CAST(1 AS BIGINT)",
                "presto": "CAST(1 AS BIGINT)",
                "hive": "CAST(1 AS BIGINT)",
                "spark": "CAST(1 AS LONG)",
            },
        )
        self.validate_all(
            "1.0bd",
            write={
                "duckdb": "CAST(1.0 AS DECIMAL)",
                "presto": "CAST(1.0 AS DECIMAL)",
                "hive": "CAST(1.0 AS DECIMAL)",
                "spark": "CAST(1.0 AS DECIMAL)",
            },
        )
        self.validate_all(
            "CAST(1 AS INT)",
            read={
                "presto": "TRY_CAST(1 AS INT)",
            },
            write={
                "duckdb": "TRY_CAST(1 AS INT)",
                "presto": "TRY_CAST(1 AS INTEGER)",
                "hive": "CAST(1 AS INT)",
                "spark": "CAST(1 AS INT)",
            },
        )

    def test_ddl(self):
        self.validate_all(
            "CREATE TABLE test STORED AS parquet TBLPROPERTIES ('x' = '1', 'Z' = '2') AS SELECT 1",
            write={
                "presto": "CREATE TABLE test WITH (FORMAT = 'parquet', x = '1', Z = '2') AS SELECT 1",
                "hive": "CREATE TABLE test STORED AS PARQUET TBLPROPERTIES ('x' = '1', 'Z' = '2') AS SELECT 1",
                "spark": "CREATE TABLE test STORED AS PARQUET TBLPROPERTIES ('x' = '1', 'Z' = '2') AS SELECT 1",
            },
        )
        self.validate_all(
            "CREATE TABLE x (w STRING) PARTITIONED BY (y INT, z INT)",
            write={
                "presto": "CREATE TABLE x (w VARCHAR, y INTEGER, z INTEGER) WITH (PARTITIONED_BY = ARRAY['y', 'z'])",
                "hive": "CREATE TABLE x (w STRING) PARTITIONED BY (y INT, z INT)",
                "spark": "CREATE TABLE x (w STRING) PARTITIONED BY (y INT, z INT)",
            },
        )

    def test_lateral_view(self):
        self.validate_all(
            "SELECT a, b FROM x LATERAL VIEW EXPLODE(y) t AS a LATERAL VIEW EXPLODE(z) u AS b",
            write={
                "presto": "SELECT a, b FROM x CROSS JOIN UNNEST(y) AS t(a) CROSS JOIN UNNEST(z) AS u(b)",
                "hive": "SELECT a, b FROM x LATERAL VIEW EXPLODE(y) t AS a LATERAL VIEW EXPLODE(z) u AS b",
                "spark": "SELECT a, b FROM x LATERAL VIEW EXPLODE(y) t AS a LATERAL VIEW EXPLODE(z) u AS b",
            },
        )
        self.validate_all(
            "SELECT a FROM x LATERAL VIEW EXPLODE(y) t AS a",
            write={
                "presto": "SELECT a FROM x CROSS JOIN UNNEST(y) AS t(a)",
                "hive": "SELECT a FROM x LATERAL VIEW EXPLODE(y) t AS a",
                "spark": "SELECT a FROM x LATERAL VIEW EXPLODE(y) t AS a",
            },
        )
        self.validate_all(
            "SELECT a FROM x LATERAL VIEW POSEXPLODE(y) t AS a",
            write={
                "presto": "SELECT a FROM x CROSS JOIN UNNEST(y) WITH ORDINALITY AS t(a)",
                "hive": "SELECT a FROM x LATERAL VIEW POSEXPLODE(y) t AS a",
                "spark": "SELECT a FROM x LATERAL VIEW POSEXPLODE(y) t AS a",
            },
        )
        self.validate_all(
            "SELECT a FROM x LATERAL VIEW EXPLODE(ARRAY(y)) t AS a",
            write={
                "presto": "SELECT a FROM x CROSS JOIN UNNEST(ARRAY[y]) AS t(a)",
                "hive": "SELECT a FROM x LATERAL VIEW EXPLODE(ARRAY(y)) t AS a",
                "spark": "SELECT a FROM x LATERAL VIEW EXPLODE(ARRAY(y)) t AS a",
            },
        )

    def test_quotes(self):
        self.validate_all(
            "'\\''",
            write={
                "duckdb": "''''",
                "presto": "''''",
                "hive": "'\\''",
                "spark": "'\\''",
            },
        )
        self.validate_all(
            "'\"x\"'",
            write={
                "duckdb": "'\"x\"'",
                "presto": "'\"x\"'",
                "hive": "'\"x\"'",
                "spark": "'\"x\"'",
            },
        )
        self.validate_all(
            "\"'x'\"",
            write={
                "duckdb": "'''x'''",
                "presto": "'''x'''",
                "hive": "'\\'x\\''",
                "spark": "'\\'x\\''",
            },
        )
        self.validate_all(
            "'\\\\a'",
            read={
                "presto": "'\\a'",
            },
            write={
                "duckdb": "'\\a'",
                "presto": "'\\a'",
                "hive": "'\\\\a'",
                "spark": "'\\\\a'",
            },
        )

    def test_regex(self):
        self.validate_all(
            "a RLIKE 'x'",
            write={
                "duckdb": "REGEXP_MATCHES(a, 'x')",
                "presto": "REGEXP_LIKE(a, 'x')",
                "hive": "a RLIKE 'x'",
                "spark": "a RLIKE 'x'",
            },
        )

        self.validate_all(
            "a REGEXP 'x'",
            write={
                "duckdb": "REGEXP_MATCHES(a, 'x')",
                "presto": "REGEXP_LIKE(a, 'x')",
                "hive": "a RLIKE 'x'",
                "spark": "a RLIKE 'x'",
            },
        )

    def test_time(self):
        self.validate_all(
            "DATEDIFF(a, b)",
            write={
                "duckdb": "DATE_DIFF('day', CAST(b AS DATE), CAST(a AS DATE))",
                "presto": "DATE_DIFF('day', CAST(SUBSTR(CAST(b AS VARCHAR), 1, 10) AS DATE), CAST(SUBSTR(CAST(a AS VARCHAR), 1, 10) AS DATE))",
                "hive": "DATEDIFF(TO_DATE(a), TO_DATE(b))",
                "spark": "DATEDIFF(TO_DATE(a), TO_DATE(b))",
                "": "DATE_DIFF(TS_OR_DS_TO_DATE(a), TS_OR_DS_TO_DATE(b))",
            },
        )
        self.validate_all(
            """from_unixtime(x, "yyyy-MM-dd'T'HH")""",
            write={
                "duckdb": "STRFTIME(TO_TIMESTAMP(CAST(x AS BIGINT)), '%Y-%m-%d''T''%H')",
                "presto": "DATE_FORMAT(FROM_UNIXTIME(x), '%Y-%m-%d''T''%H')",
                "hive": "FROM_UNIXTIME(x, 'yyyy-MM-dd\\'T\\'HH')",
                "spark": "FROM_UNIXTIME(x, 'yyyy-MM-dd\\'T\\'HH')",
            },
        )
        self.validate_all(
            "DATE_FORMAT('2020-01-01', 'yyyy-MM-dd HH:mm:ss')",
            write={
                "duckdb": "STRFTIME('2020-01-01', '%Y-%m-%d %H:%M:%S')",
                "presto": "DATE_FORMAT('2020-01-01', '%Y-%m-%d %H:%i:%S')",
                "hive": "DATE_FORMAT('2020-01-01', 'yyyy-MM-dd HH:mm:ss')",
                "spark": "DATE_FORMAT('2020-01-01', 'yyyy-MM-dd HH:mm:ss')",
            },
        )
        self.validate_all(
            "DATE_ADD('2020-01-01', 1)",
            write={
                "duckdb": "CAST('2020-01-01' AS DATE) + INTERVAL 1 DAY",
                "presto": "DATE_ADD('DAY', 1, DATE_PARSE(SUBSTR('2020-01-01', 1, 10), '%Y-%m-%d'))",
                "hive": "DATE_ADD('2020-01-01', 1)",
                "spark": "DATE_ADD('2020-01-01', 1)",
                "": "TS_OR_DS_ADD('2020-01-01', 1, 'DAY')",
            },
        )
        self.validate_all(
            "DATE_SUB('2020-01-01', 1)",
            write={
                "duckdb": "CAST('2020-01-01' AS DATE) + INTERVAL 1 * -1 DAY",
                "presto": "DATE_ADD('DAY', 1 * -1, DATE_PARSE(SUBSTR('2020-01-01', 1, 10), '%Y-%m-%d'))",
                "hive": "DATE_ADD('2020-01-01', 1 * -1)",
                "spark": "DATE_ADD('2020-01-01', 1 * -1)",
                "": "TS_OR_DS_ADD('2020-01-01', 1 * -1, 'DAY')",
            },
        )
        self.validate_all(
            "DATEDIFF(TO_DATE(y), x)",
            write={
                "duckdb": "DATE_DIFF('day', CAST(x AS DATE), CAST(CAST(y AS DATE) AS DATE))",
                "presto": "DATE_DIFF('day', CAST(SUBSTR(CAST(x AS VARCHAR), 1, 10) AS DATE), CAST(SUBSTR(CAST(CAST(SUBSTR(CAST(y AS VARCHAR), 1, 10) AS DATE) AS VARCHAR), 1, 10) AS DATE))",
                "hive": "DATEDIFF(TO_DATE(TO_DATE(y)), TO_DATE(x))",
                "spark": "DATEDIFF(TO_DATE(TO_DATE(y)), TO_DATE(x))",
                "": "DATE_DIFF(TS_OR_DS_TO_DATE(TS_OR_DS_TO_DATE(y)), TS_OR_DS_TO_DATE(x))",
            },
        )
        self.validate_all(
            "UNIX_TIMESTAMP(x)",
            write={
                "duckdb": "EPOCH(STRPTIME(x, '%Y-%m-%d %H:%M:%S'))",
                "presto": "TO_UNIXTIME(DATE_PARSE(x, '%Y-%m-%d %H:%i:%S'))",
                "hive": "UNIX_TIMESTAMP(x)",
                "spark": "UNIX_TIMESTAMP(x)",
                "": "STR_TO_UNIX(x, '%Y-%m-%d %H:%M:%S')",
            },
        )

        for unit in ("DAY", "MONTH", "YEAR"):
            self.validate_all(
                f"{unit}(x)",
                write={
                    "duckdb": f"{unit}(CAST(x AS DATE))",
                    "presto": f"{unit}(CAST(SUBSTR(CAST(x AS VARCHAR), 1, 10) AS DATE))",
                    "hive": f"{unit}(TO_DATE(x))",
                    "spark": f"{unit}(TO_DATE(x))",
                },
            )

    def test_order_by(self):
        self.validate_all(
            "SELECT fname, lname, age FROM person ORDER BY age DESC NULLS FIRST, fname ASC NULLS LAST, lname",
            write={
                "duckdb": "SELECT fname, lname, age FROM person ORDER BY age DESC NULLS FIRST, fname NULLS LAST, lname",
                "presto": "SELECT fname, lname, age FROM person ORDER BY age DESC NULLS FIRST, fname, lname NULLS FIRST",
                "hive": "SELECT fname, lname, age FROM person ORDER BY age DESC NULLS FIRST, fname NULLS LAST, lname",
                "spark": "SELECT fname, lname, age FROM person ORDER BY age DESC NULLS FIRST, fname NULLS LAST, lname",
            },
        )

    def test_hive(self):
        self.validate_all(
            "PERCENTILE(x, 0.5)",
            write={
                "duckdb": "QUANTILE(x, 0.5)",
                "presto": "APPROX_PERCENTILE(x, 0.5)",
                "hive": "PERCENTILE(x, 0.5)",
                "spark": "PERCENTILE(x, 0.5)",
            },
        )
        self.validate_all(
            "APPROX_COUNT_DISTINCT(a)",
            write={
                "duckdb": "APPROX_COUNT_DISTINCT(a)",
                "presto": "APPROX_DISTINCT(a)",
                "hive": "APPROX_COUNT_DISTINCT(a)",
                "spark": "APPROX_COUNT_DISTINCT(a)",
            },
        )
        self.validate_all(
            "ARRAY_CONTAINS(x, 1)",
            write={
                "duckdb": "ARRAY_CONTAINS(x, 1)",
                "presto": "CONTAINS(x, 1)",
                "hive": "ARRAY_CONTAINS(x, 1)",
                "spark": "ARRAY_CONTAINS(x, 1)",
            },
        )
        self.validate_all(
            "SIZE(x)",
            write={
                "duckdb": "ARRAY_LENGTH(x)",
                "presto": "CARDINALITY(x)",
                "hive": "SIZE(x)",
                "spark": "SIZE(x)",
            },
        )
        self.validate_all(
            "LOCATE('a', x)",
            write={
                "duckdb": "STRPOS(x, 'a')",
                "presto": "STRPOS(x, 'a')",
                "hive": "LOCATE('a', x)",
                "spark": "LOCATE('a', x)",
            },
        )
        self.validate_all(
            "LOCATE('a', x, 3)",
            write={
                "duckdb": "STRPOS(SUBSTR(x, 3), 'a') + 3 - 1",
                "presto": "STRPOS(SUBSTR(x, 3), 'a') + 3 - 1",
                "hive": "LOCATE('a', x, 3)",
                "spark": "LOCATE('a', x, 3)",
            },
        )
        # pylint: disable=anomalous-backslash-in-string
        self.validate_all(
            "INITCAP('new york')",
            write={
                "duckdb": "INITCAP('new york')",
                "presto": "REGEXP_REPLACE('new york', '(\w)(\w*)', x -> UPPER(x[1]) || LOWER(x[2]))",
                "hive": "INITCAP('new york')",
                "spark": "INITCAP('new york')",
            },
        )
        self.validate_all(
            "SELECT * FROM x TABLESAMPLE(10) y",
            write={
                "presto": "SELECT * FROM x AS y TABLESAMPLE(10)",
                "hive": "SELECT * FROM x TABLESAMPLE(10) AS y",
                "spark": "SELECT * FROM x TABLESAMPLE(10) AS y",
            },
        )
        self.validate_all(
            "SELECT SORT_ARRAY(x)",
            write={
                "duckdb": "SELECT ARRAY_SORT(x)",
                "presto": "SELECT ARRAY_SORT(x)",
                "hive": "SELECT SORT_ARRAY(x)",
                "spark": "SELECT SORT_ARRAY(x)",
            },
        )
        self.validate_all(
            "SELECT SORT_ARRAY(x, False)",
            write={
                "duckdb": "SELECT ARRAY_REVERSE_SORT(x)",
                "presto": "SELECT ARRAY_SORT(x, (a, b) -> CASE WHEN a < b THEN 1 WHEN a > b THEN -1 ELSE 0 END)",
                "hive": "SELECT SORT_ARRAY(x, FALSE)",
                "spark": "SELECT SORT_ARRAY(x, FALSE)",
            },
        )
        self.validate_all(
            "GET_JSON_OBJECT(x, '$.name')",
            write={
                "presto": "JSON_EXTRACT_SCALAR(x, '$.name')",
                "hive": "GET_JSON_OBJECT(x, '$.name')",
                "spark": "GET_JSON_OBJECT(x, '$.name')",
            },
        )
        self.validate_all(
            "MAP(a, b, c, d)",
            write={
                "duckdb": "MAP(LIST_VALUE(a, c), LIST_VALUE(b, d))",
                "presto": "MAP(ARRAY[a, c], ARRAY[b, d])",
                "hive": "MAP(a, b, c, d)",
                "spark": "MAP_FROM_ARRAYS(ARRAY(a, c), ARRAY(b, d))",
            },
        )
        self.validate_all(
            "MAP(a, b)",
            write={
                "duckdb": "MAP(LIST_VALUE(a), LIST_VALUE(b))",
                "presto": "MAP(ARRAY[a], ARRAY[b])",
                "hive": "MAP(a, b)",
                "spark": "MAP_FROM_ARRAYS(ARRAY(a), ARRAY(b))",
            },
        )
        self.validate_all(
            "LOG(10)",
            write={
                "duckdb": "LN(10)",
                "presto": "LN(10)",
                "hive": "LN(10)",
                "spark": "LN(10)",
            },
        )
        self.validate_all(
            "LOG(10, 2)",
            write={
                "duckdb": "LOG(10, 2)",
                "presto": "LOG(10, 2)",
                "hive": "LOG(10, 2)",
                "spark": "LOG(10, 2)",
            },
        )
        self.validate_all(
            'ds = "2020-01-01"',
            write={
                "duckdb": "ds = '2020-01-01'",
                "presto": "ds = '2020-01-01'",
                "hive": "ds = '2020-01-01'",
                "spark": "ds = '2020-01-01'",
            },
        )
        self.validate_all(
            "ds = \"1''2\"",
            write={
                "duckdb": "ds = '1''''2'",
                "presto": "ds = '1''''2'",
                "hive": "ds = '1\\'\\'2'",
                "spark": "ds = '1\\'\\'2'",
            },
        )
        self.validate_all(
            "x == 1",
            write={
                "duckdb": "x = 1",
                "presto": "x = 1",
                "hive": "x = 1",
                "spark": "x = 1",
            },
        )
        self.validate_all(
            "x div y",
            write={
                "duckdb": "CAST(x / y AS INT)",
                "presto": "CAST(x / y AS INTEGER)",
                "hive": "CAST(x / y AS INT)",
                "spark": "CAST(x / y AS INT)",
            },
        )
        self.validate_all(
            "COLLECT_LIST(x)",
            read={
                "presto": "ARRAY_AGG(x)",
            },
            write={
                "duckdb": "ARRAY_AGG(x)",
                "presto": "ARRAY_AGG(x)",
                "hive": "COLLECT_LIST(x)",
                "spark": "COLLECT_LIST(x)",
            },
        )
        self.validate_all(
            "COLLECT_SET(x)",
            read={
                "presto": "SET_AGG(x)",
            },
            write={
                "presto": "SET_AGG(x)",
                "hive": "COLLECT_SET(x)",
                "spark": "COLLECT_SET(x)",
            },
        )
        self.validate_all(
            "SELECT * FROM x TABLESAMPLE(1) AS foo",
            read={
                "presto": "SELECT * FROM x AS foo TABLESAMPLE(1)",
            },
            write={
                "presto": "SELECT * FROM x AS foo TABLESAMPLE(1)",
                "hive": "SELECT * FROM x TABLESAMPLE(1) AS foo",
                "spark": "SELECT * FROM x TABLESAMPLE(1) AS foo",
            },
        )
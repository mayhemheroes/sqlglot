"""
## Dialects

While there is a SQL standard, no database vendor fully implements it. Most SQL engines support a variation of
that standard, which has led to a plethora of similar, yet different SQL dialects, each of them existing for its
own special purposes. Under these circumstances, it's usually very difficult to write portable SQL code, as the
syntax may vary from dialect to dialect. One common example is the usage of date/time functions, which can be
especially hard to deal with.

SQLGlot aims to bridge all these dialects, by providing an extendible SQL transpilation framework. It achieves
this by using a `Dialect` class hierarchy, where each `Dialect` implements a specific dialect. The base `Dialect`
class itself implements a "SQLGlot" dialect that aims to be as generic and ANSI-compliant as possible. For this
reason, it relies on the base `Tokenizer`, `Parser` and `Generator` classes, so these need to be very lenient when
it comes to consuming SQL code. New dialects can thus be supported very easily, simply by subclassing from `Dialect`
and overriding its various components (e.g. the `Parser` class), in order to implement the target behavior.

### Implementing a custom Dialect

Consider the following example:

```python
from sqlglot import exp
from sqlglot.dialects.dialect import Dialect
from sqlglot.generator import Generator
from sqlglot.tokens import Tokenizer, TokenType


class Custom(Dialect):
    class Tokenizer(Tokenizer):
        QUOTES = ["'", '"']
        IDENTIFIERS = ["`"]

        KEYWORDS = {
            **Tokenizer.KEYWORDS,
            "INT64": TokenType.BIGINT,
            "FLOAT64": TokenType.DOUBLE,
        }

    class Generator(Generator):
        TRANSFORMS = {exp.Array: lambda self, e: f"[{self.expressions(e)}]"}

        TYPE_MAPPING = {
            exp.DataType.Type.TINYINT: "INT64",
            exp.DataType.Type.SMALLINT: "INT64",
            exp.DataType.Type.INT: "INT64",
            exp.DataType.Type.BIGINT: "INT64",
            exp.DataType.Type.DECIMAL: "NUMERIC",
            exp.DataType.Type.FLOAT: "FLOAT64",
            exp.DataType.Type.DOUBLE: "FLOAT64",
            exp.DataType.Type.BOOLEAN: "BOOL",
            exp.DataType.Type.TEXT: "STRING",
        }
```

This is a typical example of adding a new dialect implementation in SQLGlot: we specify its identifier and string
delimiters, as well as what tokens it uses for its types and how they're associated with SQLGlot types. Since
the `Expression` classes are common for each dialect supported in SQLGlot, we may also need to override the generation
logic for some expressions; this is usually done by adding new entries to the `TRANSFORMS` mapping.

----
"""

from sqlglot.dialects.bigquery import BigQuery
from sqlglot.dialects.clickhouse import ClickHouse
from sqlglot.dialects.databricks import Databricks
from sqlglot.dialects.dialect import Dialect, Dialects
from sqlglot.dialects.drill import Drill
from sqlglot.dialects.duckdb import DuckDB
from sqlglot.dialects.hive import Hive
from sqlglot.dialects.mysql import MySQL
from sqlglot.dialects.oracle import Oracle
from sqlglot.dialects.postgres import Postgres
from sqlglot.dialects.presto import Presto
from sqlglot.dialects.redshift import Redshift
from sqlglot.dialects.snowflake import Snowflake
from sqlglot.dialects.spark import Spark
from sqlglot.dialects.sqlite import SQLite
from sqlglot.dialects.starrocks import StarRocks
from sqlglot.dialects.tableau import Tableau
from sqlglot.dialects.teradata import Teradata
from sqlglot.dialects.trino import Trino
from sqlglot.dialects.tsql import TSQL

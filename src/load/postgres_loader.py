from uuid import uuid4

from sqlalchemy import create_engine, text


def get_engine(database_url):
    return create_engine(database_url)


CONFLICT_KEYS = {
    "fact_weather_hourly": ["country_code", "timestamp_utc"],
    "fact_energy_load_hourly": ["country_code", "timestamp_utc"],
    "fact_energy_price_hourly": ["country_code", "timestamp_utc"],
    "fact_generation_hourly": ["country_code", "timestamp_utc", "energy_source"],
}


def quote_identifier(identifier):
    return '"' + identifier.replace('"', '""') + '"'


def load_dataframe(df, table_name, database_url, schema="public"):
    if df.empty:
        return

    engine = get_engine(database_url)

    conflict_columns = CONFLICT_KEYS.get(table_name)
    if not conflict_columns:
        with engine.begin() as connection:
            df.to_sql(
                table_name,
                connection,
                schema=schema,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=1000,
            )
        return

    staging_table = f"_stg_{table_name}_{uuid4().hex}"
    quoted_columns = [quote_identifier(column) for column in df.columns]
    insert_columns = ", ".join(quoted_columns)
    select_columns = ", ".join(quoted_columns)
    conflict_target = ", ".join(quote_identifier(column) for column in conflict_columns)
    update_columns = [column for column in df.columns if column not in conflict_columns]
    update_set = ", ".join(
        f"{quote_identifier(column)} = EXCLUDED.{quote_identifier(column)}"
        for column in update_columns
    )

    if update_set:
        conflict_action = f"DO UPDATE SET {update_set}"
    else:
        conflict_action = "DO NOTHING"

    upsert_sql = f"""
        INSERT INTO {quote_identifier(schema)}.{quote_identifier(table_name)} ({insert_columns})
        SELECT {select_columns}
        FROM {quote_identifier(schema)}.{quote_identifier(staging_table)}
        ON CONFLICT ({conflict_target}) {conflict_action}
    """

    with engine.begin() as connection:
        df.to_sql(
            staging_table,
            connection,
            schema=schema,
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=1000,
        )
        connection.execute(text(upsert_sql))
        connection.execute(
            text(f"DROP TABLE IF EXISTS {quote_identifier(schema)}.{quote_identifier(staging_table)}")
        )


def refresh_daily_mart(database_url):
    engine = get_engine(database_url)
    with engine.begin() as connection:
        connection.execute(text("REFRESH MATERIALIZED VIEW mart_daily_country_energy_weather"))

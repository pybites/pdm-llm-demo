import json
from typing import Any

import duckdb
import pyarrow as pa
from modelsmith import Forge, Prompt, VertexAIGenerativeModel
from vertexai.generative_models import GenerativeModel

from prompts import (
    DATA_CHAT_PROMPT,
    GENERATE_SQL_PROMPT,
    INVALID_QUERY_PROMPT,
    VALIDATE_SQL_PROMPT,
)


def data_chat(
    user_input: str,
    source_data: list[dict[str, Any]],
    chat_history: str | None = None,
) -> str:
    """
    Answer the user based on SQL queries run against the data in the context.
    """
    if not source_data:
        raise ValueError("source_data must be provided.")

    data_table = pa.Table.from_pylist(source_data)

    sql_query = generate_sql(
        user_input=user_input,
        table_schema=data_table.schema.to_string(),
        chat_history=chat_history,
    )

    # Set overall model and settings
    model_settings = {
        "temperature": 0.2,
        "max_output_tokens": 8192,
        "top_p": 0.95,
    }

    model = GenerativeModel("gemini-1.5-flash")

    # Validate the user input and return a response telling the user
    # their query was invalid if they asked to update or delete records
    is_valid_query = validate_user_input(user_input=user_input)
    if not is_valid_query:
        invalid_query_prompt = Prompt(prompt=INVALID_QUERY_PROMPT).render(
            user_input=user_input, chat_history=chat_history
        )
        invalid_query_response = model.generate_content(
            contents=invalid_query_prompt,
            generation_config=model_settings,
        )

        return invalid_query_response.text

    data = json.dumps(duckdb.sql(sql_query).fetch_arrow_table().to_pylist())
    prompt = Prompt(prompt=DATA_CHAT_PROMPT).render(
        user_input=user_input, data=data, chat_history=chat_history
    )

    response = model.generate_content(contents=prompt, generation_config=model_settings)

    return response.text


def generate_sql(
    user_input: str, table_schema: str, chat_history: str | None = None
) -> str:
    """
    Build the SQL Query that needs to be executed against the data table.
    """
    prompt = Prompt(GENERATE_SQL_PROMPT).render(
        user_input=user_input,
        table_schema=table_schema,
        table_name="data_table",
        chat_history=chat_history,
    )

    model_settings = {
        "temperature": 0.2,
        "max_output_tokens": 8192,
        "top_p": 0.95,
    }

    model = GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(contents=prompt, generation_config=model_settings)

    return response.text.replace("```sql", "").replace("```", "")


def validate_user_input(user_input: str) -> bool:
    """
    Validate that the SQL statement is a SELECT statement and not a DELETE or UPDATE.
    """
    model_settings = {
        "temperature": 0.2,
        "max_output_tokens": 10,
        "top_p": 0.95,
    }

    forge = Forge(
        model=VertexAIGenerativeModel("gemini-1.5-flash"),
        response_model=bool,
        prompt=VALIDATE_SQL_PROMPT,
    )

    response = forge.generate(user_input=user_input, model_settings=model_settings)

    return response

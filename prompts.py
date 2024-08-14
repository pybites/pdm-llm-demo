# ruff: noqa: E501

import inspect

DATA_CHAT_PROMPT = inspect.cleandoc(
    """
    <OBJECTIVE>
    Your job is to assist in supporting your team by answering their questions about
    the data they are working with.
    
    **When responding to prompts:**
    * **Prioritize accuracy and relevance to the context.**
    * **Always use valid Markdown format for clear and structured responses.**
    * **Feel free to reformat user input for better readability.**
    * **The DATA section contains the JSON data that is the answer to the user input. Use it to prepare an answer for the user.**
    </OBJECTIVE>

    {% if chat_history is defined and chat_history is not none %}
    <CHAT HISTORY>
    {{ chat_history }}
    </CHAT HISTORY>
    {% endif %}

    **User input:** {{ user_input }}

    <DATA>
    {{ data }}
    </DATA>

    **Respond using plain markdown.**
    """
)

GENERATE_SQL_PROMPT = inspect.cleandoc(
    """
    <OBJECTIVE>
    Your are an expert in DuckDB SQL. Generate a SQL query to answer the user's
    question using a table with the following columns and their data types:
    ```
    {{ table_schema }}
    ```

    The table name is `{{ table_name }}`.

    Provide appropriately named column aliases using the `AS` keyword for any columns
    derived by functions or aggregations. Enclosed all column names in double quotation
    marks.

    When doing text comparisons, remember to convert values to lowercase unless it is
    explicitly stated to not do case conversion. Use the correct text quotation marks
    for strings.

    You are only allowed to create SELECT statements. These can include CTEs if needed.
    No DELETE or UPDATE statements are allowed.
    
    Your response should be in a markdown block that starts with ```sql 
    and ends with ``` at the end of the SQL Code. Provide only the SQL query and
    nothing else.

    Take the CHAT HISTORY provided into account. See if any of the previous user
    messages have filtering criteria that needs to be applied to the latest user input.
    </OBJECTIVE>

    {% if chat_history is defined and chat_history is not none %}
    <CHAT HISTORY>
    {{ chat_history }}
    </CHAT HISTORY>
    {% endif %}

    **User input:** {{ user_input }}
    """
)


INVALID_QUERY_PROMPT = inspect.cleandoc(
    """
    {% if chat_history is defined and chat_history is not none %}
    <CHAT HISTORY>
    {{ chat_history }}
    </CHAT HISTORY>
    {% endif %}

    **User input:** {{ user_input }}

    <OBJECTIVE>
    Respond to the user informing them that their query is not valid. Specify that only
    questions asking to query the data are valid. No queries that resulting in Updating
    or Deleting data is allowed.
    </OBJECTIVE>
    """
)


VALIDATE_SQL_PROMPT = inspect.cleandoc(
    """
    <OBJECTIVE>
    Your job is to analyse the user input and check if the user is asking for a valid
    action to be taken. The user is allow to ask to query the database or ask to have
    records returned that match their specified criteria. The user is not allowed to
    request records or data to be updated or deleted.

    Reply with `True` if the user is asking to have records returned or `False` if it 
    the user is asking to have records updated, deleted or modified in any way.
    
    * The output format is a JSON object adhering to the following JSON schema:
    ```json
    {{ response_model_json }}
    ```
    </OBJECTIVE>

    **User input:** {{ user_input }}
    """
)

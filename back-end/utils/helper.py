from core.database import get_db_connection
from typing import Any


def execute_fetch_query(query: str, params: tuple = ()) -> Any:
    """
    Execute a SQL query with the provided parameters.
    
    Args:
        query (str): The SQL query to execute.
        params (tuple): The parameters to bind to the query.
    
    Returns:
        Any: The result of the query execution.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result

def execute_insert_or_update_query(query: str, params: tuple = ()) -> bool:
    """
    Execute an insert SQL query with the provided parameters.
    
    Args:
        query (str): The SQL insert query to execute.
        params (tuple): The parameters to bind to the query.
    
    Returns:
        bool: True if the insert was successful, False otherwise.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0
    
def add_data_to_vector_store(user_id: str, file_id:str, file_name: str, file_content: bytes) -> bool:
    pass

def remove_data_to_vector_store(user_id: str, file_id:str, file_name: str, file_content: bytes) -> bool:
    pass


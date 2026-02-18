"""
Database utilities for SQL Server connections
"""
from typing import List, Dict, Any
import sys
from pathlib import Path

try:
    import pyodbc
    PYODBC_IMPORT_ERROR = None
except Exception as import_error:
    pyodbc = None
    PYODBC_IMPORT_ERROR = import_error

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import settings


class DatabaseDriverError(RuntimeError):
    """Raised when database driver dependencies are unavailable."""


def _get_pyodbc_module():
    """Return pyodbc module or raise actionable error when unavailable."""
    if pyodbc is None:
        raise DatabaseDriverError(
            "pyodbc failed to load. On macOS, install ODBC runtime dependencies "
            "(e.g., unixODBC and Microsoft ODBC Driver for SQL Server) and reinstall pyodbc."
        ) from PYODBC_IMPORT_ERROR

    return pyodbc

def get_connection_string() -> str:
    """Build connection string from environment variables"""
    db_server = settings.DB_SERVER
    db_name = settings.DB_NAME
    db_user = settings.DB_USER
    db_password = settings.DB_PASSWORD
    db_odbc_driver = settings.DB_ODBC_DRIVER
    
    if not all([db_server, db_name, db_user, db_password]):
        raise ValueError("Missing database configuration in environment variables")
    
    return f"Driver={{{db_odbc_driver}}};Server=tcp:{db_server},1433;Database={db_name};Uid={db_user};Pwd={db_password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return results as list of dicts"""
    conn = None

    try:
        pyodbc_module = _get_pyodbc_module()
        conn_str = get_connection_string()
        conn = pyodbc_module.connect(conn_str)
        cursor = conn.cursor()
        
        cursor.execute(query, params)

        if cursor.description is None:
            conn.commit()
            return []

        columns = [desc[0] for desc in cursor.description]
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        conn.commit()
        
        return results
    except Exception as e:
        raise Exception(f"Database query failed: {str(e)}")
    finally:
        if conn is not None:
            conn.close()

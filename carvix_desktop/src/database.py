import psycopg2
from psycopg2 import pool
from config import DB_CONFIG, DATABASE_URL
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    _connection_pool = None
    
    @classmethod
    def initialize_pool(cls):
        try:
            # Use DATABASE_URL if available (cloud databases), otherwise use individual config
            if DATABASE_URL:
                # DATABASE_URL already contains SSL parameters
                cls._connection_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=DATABASE_URL
                )
            else:
                # SSL configuration for local databases
                use_ssl = os.getenv('PGSSL', 'false').lower() == 'true'
                ssl_config = {'sslmode': 'require'} if use_ssl else {}
                
                cls._connection_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    host=DB_CONFIG['host'],
                    port=DB_CONFIG['port'],
                    database=DB_CONFIG['database'],
                    user=DB_CONFIG['user'],
                    password=DB_CONFIG['password'],
                    **ssl_config
                )
            if cls._connection_pool:
                logger.info("Connection pool created successfully")
                return True
        except Exception as e:
            logger.error(f"Error creating connection pool: {e}")
            return False
    
    @classmethod
    def get_connection(cls):
        if cls._connection_pool:
            return cls._connection_pool.getconn()
        return None
    
    @classmethod
    def release_connection(cls, connection):
        if cls._connection_pool and connection:
            cls._connection_pool.putconn(connection)
    
    @classmethod
    def close_all_connections(cls):
        if cls._connection_pool:
            cls._connection_pool.closeall()
            logger.info("All connections closed")
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=True):
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            if not connection:
                raise Exception("No connection available")
            
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            
            if fetch:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [dict(zip(columns, row)) for row in rows]
            else:
                connection.commit()
                result = cursor.rowcount
            
            return result
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                cls.release_connection(connection)
    
    @classmethod
    def execute_transaction(cls, queries):
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            if not connection:
                raise Exception("No connection available")
            
            cursor = connection.cursor()
            results = []
            
            for query_data in queries:
                if isinstance(query_data, tuple):
                    query, params = query_data
                else:
                    query, params = query_data, ()
                
                cursor.execute(query, params or ())
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    results.append([dict(zip(columns, row)) for row in rows])
                else:
                    results.append(cursor.rowcount)
            
            connection.commit()
            return results
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Error executing transaction: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                cls.release_connection(connection)

# Initialize connection pool on import
Database.initialize_pool()

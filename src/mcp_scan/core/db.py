import json
import logging
from typing import Optional, Dict, Any
from uuid import UUID
import mysql.connector
from mysql.connector import pooling

from mcp_scan.config import get_config
from mcp_scan.core.models import Job

logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None

    def __init__(self):
        config = get_config().database
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="mcp_scan_pool",
                pool_size=5,
                host=config.host,
                port=config.port,
                user=config.user,
                password=config.password,
                database=config.database
            )
            logger.info("Database connection pool created")
            self._ensure_schema()
        except mysql.connector.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            self.pool = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _ensure_schema(self):
        """Ensure the status column exists (simple migration check)."""
        if not self.pool:
            return
        
        conn = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            # Check if status column exists
            cursor.execute("SHOW COLUMNS FROM job_results LIKE 'status'")
            result = cursor.fetchone()
            if not result:
                logger.info("Adding 'status' column to job_results table")
                cursor.execute("ALTER TABLE job_results ADD COLUMN status VARCHAR(20) DEFAULT 'pending' AFTER job_id")
                conn.commit()
        except mysql.connector.Error as e:
            logger.warning(f"Schema check failed: {e}")
        finally:
            if conn:
                conn.close()

    def save_job(self, job: Job):
        """Upsert a job record."""
        if not self.pool:
            return

        conn = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            
            job_id = str(job.id)
            status = job.status.value
            result_data = job.model_dump_json()

            query = """
                INSERT INTO job_results (job_id, status, result_data, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
                ON DUPLICATE KEY UPDATE
                    status = VALUES(status),
                    result_data = VALUES(result_data),
                    updated_at = NOW()
            """
            cursor.execute(query, (job_id, status, result_data))
            conn.commit()
            logger.debug(f"Job {job_id} saved to DB")
        except mysql.connector.Error as e:
            logger.error(f"Failed to save job {job.id}: {e}")
        finally:
            if conn:
                conn.close()

    def update_status(self, job_id: UUID, status: str):
        """Update job status only."""
        if not self.pool:
            return

        conn = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            
            query = "UPDATE job_results SET status = %s, updated_at = NOW() WHERE job_id = %s"
            cursor.execute(query, (status, str(job_id)))
            conn.commit()
        except mysql.connector.Error as e:
            logger.error(f"Failed to update status for job {job_id}: {e}")
        finally:
            if conn:
                conn.close()

    def get_job(self, job_id: UUID) -> Optional[Job]:
        """Fetch a job from DB."""
        if not self.pool:
            return None

        conn = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT result_data FROM job_results WHERE job_id = %s"
            cursor.execute(query, (str(job_id),))
            row = cursor.fetchone()
            
            if row and row['result_data']:
                data = json.loads(row['result_data'])
                return Job(**data)
            return None
        except mysql.connector.Error as e:
            logger.error(f"Failed to fetch job {job_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to deserialize job {job_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()

def get_db():
    return DatabaseManager.get_instance()

const mysql = require('mysql2/promise');

const pool = mysql.createPool({
    host: process.env.DB_HOST || 'db',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || 'root',
    database: process.env.DB_NAME || 'job_result_db',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0,
    acquireTimeout: 30000,
    timeout: 60000
});

const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function executeTransaction(callback, retries = 3, delay = 200) {
    let connection;
    for (let i = 0; i <= retries; i++) {
        try {
            connection = await pool.getConnection();
            await connection.beginTransaction();
            const result = await callback(connection);
            await connection.commit();
            return result;
        } catch (err) {
            if (connection) await connection.rollback();
            
            // Retry only on connection errors or deadlocks
            const isRetryable = err.code === 'ECONNREFUSED' || err.code === 'ETIMEDOUT' || err.code === 'ER_LOCK_DEADLOCK';
            if (i < retries && isRetryable) {
                console.warn(`Transaction failed (attempt ${i + 1}/${retries + 1}), retrying in ${delay}ms...`, err.message);
                await wait(delay);
                delay *= 2; // Exponential backoff
                continue;
            }
            throw err;
        } finally {
            if (connection) connection.release();
        }
    }
}

module.exports = { pool, executeTransaction };

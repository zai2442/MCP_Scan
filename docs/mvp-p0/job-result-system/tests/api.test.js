const request = require('supertest');
const { MySqlContainer } = require('@testcontainers/mysql');
const fs = require('fs');
const path = require('path');

jest.setTimeout(60000);

describe('Job Result Export API', () => {
    let container;
    let app;
    let pool;
    let exportDir;

    beforeAll(async () => {
        // Start MySQL container
        container = await new MySqlContainer('mysql:8.0')
            .withDatabase('job_result_db')
            .withRootPassword('root')
            .start();

        // Set env vars
        process.env.DB_HOST = container.getHost();
        process.env.DB_PORT = container.getPort();
        process.env.DB_USER = 'root';
        process.env.DB_PASSWORD = 'root';
        process.env.DB_NAME = 'job_result_db';
        
        // Setup temporary exports dir
        exportDir = path.join(__dirname, 'temp_exports');
        if (!fs.existsSync(exportDir)) {
            fs.mkdirSync(exportDir);
        }
        process.env.EXPORTS_DIR = exportDir;

        // Re-import app and db to use new env
        jest.resetModules();
        const dbModule = require('../src/db');
        pool = dbModule.pool;
        app = require('../src/app');

        // Create table
        const connection = await pool.getConnection();
        await connection.query(`
            CREATE TABLE IF NOT EXISTS job_results (
                job_id VARCHAR(64) PRIMARY KEY,
                result_data JSON NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        `);
        connection.release();
    });

    afterAll(async () => {
        if (pool) await pool.end();
        if (container) await container.stop();
        // Cleanup exports
        if (fs.existsSync(exportDir)) {
            fs.rmSync(exportDir, { recursive: true, force: true });
        }
    });

    test('should export valid job_id successfully', async () => {
        const jobId = 'valid-job-1';
        const data = { status: 'success', findings: ['vuln1'] };

        // Insert data
        const connection = await pool.getConnection();
        await connection.query('INSERT INTO job_results (job_id, result_data) VALUES (?, ?)', [jobId, JSON.stringify(data)]);
        connection.release();

        const res = await request(app).get(`/api/v1/jobs/${jobId}/export`);
        
        expect(res.statusCode).toBe(200);
        expect(res.body).toHaveProperty('file', `${jobId}_result.json`);
        
        // Verify file content
        const filePath = path.join(exportDir, `${jobId}_result.json`);
        expect(fs.existsSync(filePath)).toBe(true);
        const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        expect(content).toEqual(data);
    });

    test('should return 400 for invalid job_id format', async () => {
        const invalidIds = ['job$1', 'job space', 'job/1', '', 'a'.repeat(65)];
        
        for (const id of invalidIds) {
            const res = await request(app).get(`/api/v1/jobs/${encodeURIComponent(id)}/export`);
            expect(res.statusCode).toBe(400);
            expect(res.body).toEqual({ error: "Invalid job_id format" });
        }
    });

    test('should return 404 for non-existent job_id', async () => {
        const jobId = 'non-existent-job';
        const res = await request(app).get(`/api/v1/jobs/${jobId}/export`);
        
        expect(res.statusCode).toBe(404);
        expect(res.body).toEqual({ error: "Job not found" });
        
        const filePath = path.join(exportDir, `${jobId}_result.json`);
        expect(fs.existsSync(filePath)).toBe(false);
    });

    test('should handle concurrent exports without deadlock', async () => {
        const jobId = 'concurrent-job';
        const data = { status: 'concurrent' };
        
        const connection = await pool.getConnection();
        await connection.query('INSERT INTO job_results (job_id, result_data) VALUES (?, ?)', [jobId, JSON.stringify(data)]);
        connection.release();

        const requests = Array(50).fill().map(() => request(app).get(`/api/v1/jobs/${jobId}/export`));
        const responses = await Promise.all(requests);
        
        responses.forEach(res => {
            expect(res.statusCode).toBe(200);
        });
    });
});

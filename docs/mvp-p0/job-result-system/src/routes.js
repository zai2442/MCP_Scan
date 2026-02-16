const express = require('express');
const fs = require('fs');
const path = require('path');
const { executeTransaction } = require('./db');

const router = express.Router();

const EXPORTS_DIR = process.env.EXPORTS_DIR || '/exports';

// Job ID validation regex: Alphanumeric, hyphen, underscore, 1-64 chars
const JOB_ID_REGEX = /^[a-zA-Z0-9_-]{1,64}$/;

router.get('/jobs/:job_id/export', async (req, res) => {
    const { job_id } = req.params;

    // 3.2 Validate job_id format
    if (!JOB_ID_REGEX.test(job_id)) {
        return res.status(400).json({ error: "Invalid job_id format" });
    }

    try {
        const result = await executeTransaction(async (connection) => {
            // 4.1 Transaction read
            const [rows] = await connection.execute(
                'SELECT result_data FROM job_results WHERE job_id = ?',
                [job_id]
            );

            if (rows.length === 0) {
                return null; // Job not found
            }

            const resultData = rows[0].result_data;
            const fileName = `${job_id}_result.json`;
            const filePath = path.join(EXPORTS_DIR, fileName);

            // Synchronously write to file
            // result_data is JSON type in DB, mysql2 returns it as object or string?
            // Usually object if JSON type.
            const content = typeof resultData === 'string' ? resultData : JSON.stringify(resultData, null, 2);
            
            try {
                fs.writeFileSync(filePath, content);
            } catch (writeErr) {
                console.error("File write error:", writeErr);
                throw new Error("Failed to write export file");
            }

            return fileName;
        });

        if (!result) {
            return res.status(404).json({ error: "Job not found" });
        }

        return res.status(200).json({ file: result });

    } catch (err) {
        console.error("Export error:", err);
        return res.status(500).json({ error: "Internal server error" });
    }
});

module.exports = router;

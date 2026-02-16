const express = require('express');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

// 5.2 Security: Helmet
app.use(helmet());

// 5.2 Security: Rate Limit (10 req/s/IP, max 100 concurrent/burst logic handled by leaky bucket usually, but express-rate-limit is window based)
// Requirement: "Single IP max 10 req/s, peak protection 100 concurrent".
// express-rate-limit uses windowMs. 1 second window, max 10 requests.
const limiter = rateLimit({
    windowMs: 1000, // 1 second
    max: 10, // Limit each IP to 10 requests per windowMs
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: "Too many requests, please try again later." }
});
app.use(limiter);

app.use(express.json());

const exportRoutes = require('./routes');
app.use('/api/v1', exportRoutes);

// Health check
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok' });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Internal Server Error' });
});

if (require.main === module) {
    app.listen(port, () => {
        console.log(`Server running on port ${port}`);
    });
}

module.exports = app;

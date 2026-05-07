import express from 'express';
import { Client } from './clients';
import { Model } from './models';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Example route
app.get('/api', (req, res) => {
    res.send('AI Interview System API');
});

// Initialize clients and models
const client = new Client();
const model = new Model();

app.listen(PORT, () => {
    console.log(`AI services running on http://localhost:${PORT}`);
});
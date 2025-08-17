import express from 'express';
import bodyParser from 'body-parser';
const app = express();
app.use(bodyParser.json());
const PORT = process.env.PORT || 8081;
app.get('/health', (_req, res) => res.send('ok'));
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
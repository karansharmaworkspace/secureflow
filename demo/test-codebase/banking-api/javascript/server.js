const express = require('express');
const cardsRouter = require('./routes/cards');
const notificationsRouter = require('./routes/notifications');

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;

app.use('/api/v3/cards', cardsRouter);
app.use('/api/v3/notifications', notificationsRouter);

app.get('/health', (req, res) => {
    res.json({ status: 'ok', version: '3.2.0' });
});

app.listen(PORT, () => {
    console.log(`Banking API running on port ${PORT}`);
});

const express = require('express');
const router = express.Router();

router.get('/:cardId/transactions', (req, res) => {
    const { cardId } = req.params;
    res.json({ card_id: cardId, transactions: [] });
});

router.get('/:cardId/statement', (req, res) => {
    res.json({ statement: [] });
});

router.post('/:cardId/block', (req, res) => {
    res.json({ blocked: true });
});

router.post('/:cardId/unblock', (req, res) => {
    res.json({ unblocked: true });
});

router.get('/:cardId/pin/status', (req, res) => {
    res.json({ pin_set: true });
});

router.post('/:cardId/pin/change', (req, res) => {
    res.json({ changed: true });
});

router.get('/:cardId/rewards', (req, res) => {
    res.json({ points: 12500 });
});

router.get('/:cardId/limits', (req, res) => {
    res.json({ daily: 50000, monthly: 1000000 });
});

router.post('/:cardId/international/enable', (req, res) => {
    res.json({ enabled: true });
});

router.get('/:cardId/emi/options', (req, res) => {
    res.json({ options: [] });
});

module.exports = router;

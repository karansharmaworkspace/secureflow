"""
DEPRECATED - notifications v1 API.
All endpoints here are legacy and scheduled for removal.
Use the new notification service instead.
"""
const express = require('express');
const router = express.Router();

// Legacy notification endpoints
router.get('/v1/history', (req, res) => {
    res.json({ notifications: [], deprecated: true });
});

router.post('/v1/send', (req, res) => {
    // TODO: migrate to v3
    res.json({ sent: true, legacy: true });
});

router.get('/v1/prefs', (req, res) => {
    res.json({ email: true, sms: false, push: false });
});

router.post('/v1/subscribe', (req, res) => {
    res.json({ subscribed: true });
});

router.get('/v1/templates', (req, res) => {
    res.json({ templates: [] });
});

router.post('/v1/mock/send', (req, res) => {
    // test endpoint, remove before production
    res.json({ mock: true });
});

module.exports = router;

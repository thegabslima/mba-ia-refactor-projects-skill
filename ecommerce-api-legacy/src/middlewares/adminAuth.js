const crypto = require('crypto');
const { adminToken } = require('../config/settings');

/** Exige o header X-Admin-Token; sem ADMIN_TOKEN configurado as rotas ficam desativadas. */
function adminAuth(req, res, next) {
    const sent = Buffer.from(req.get('X-Admin-Token') || '');
    const expected = Buffer.from(adminToken);
    const valid = expected.length > 0 && sent.length === expected.length && crypto.timingSafeEqual(sent, expected);
    if (!valid) return res.status(403).send('Acesso negado');
    return next();
}

module.exports = adminAuth;

const logger = require('../services/logger');

/** Evita repetir try/catch: rejeições de handlers async chegam ao errorHandler. */
const asyncHandler = (handler) => (req, res, next) => Promise.resolve(handler(req, res, next)).catch(next);

// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
    logger.error(err.stack || String(err));
    if (err.type === 'entity.parse.failed') return res.status(400).send('Bad Request');
    return res.status(500).send('Erro interno');
}

module.exports = { asyncHandler, errorHandler };

const { approvedCardPrefix, paymentStatus } = require('../config/settings');
const logger = require('./logger');

/** Simula o gateway: cartões que começam com o prefixo aprovado são pagos. */
function charge(cardNumber, amount) {
    logger.info(`Processando cartão final ${cardNumber.slice(-4)} no valor de ${amount}`);
    return cardNumber.startsWith(approvedCardPrefix) ? paymentStatus.PAID : paymentStatus.DENIED;
}

module.exports = { charge };

const crypto = require('crypto');

const KEY_LENGTH = 64;

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.scryptSync(password, salt, KEY_LENGTH).toString('hex');
    return `${salt}:${hash}`;
}

function verifyPassword(password, stored) {
    const [salt, hash] = stored.split(':');
    const candidate = crypto.scryptSync(password, salt, KEY_LENGTH);
    return crypto.timingSafeEqual(candidate, Buffer.from(hash, 'hex'));
}

module.exports = { hashPassword, verifyPassword };

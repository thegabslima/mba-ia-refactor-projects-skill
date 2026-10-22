function log(level, message) {
    console.log(`${new Date().toISOString()} [${level}] ${message}`);
}

module.exports = {
    info: (message) => log('INFO', message),
    error: (message) => log('ERROR', message),
};

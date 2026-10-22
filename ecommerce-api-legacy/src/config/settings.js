module.exports = {
    port: Number(process.env.PORT) || 3000,
    dbFile: process.env.DB_FILE || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    adminToken: process.env.ADMIN_TOKEN || '',
    paymentStatus: { PAID: 'PAID', DENIED: 'DENIED' },
    approvedCardPrefix: '4',
};

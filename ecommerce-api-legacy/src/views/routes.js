const express = require('express');
const adminAuth = require('../middlewares/adminAuth');
const { asyncHandler } = require('../middlewares/errorHandler');

function buildRoutes({ checkoutController, adminController, userController }) {
    const router = express.Router();

    router.post('/api/checkout', asyncHandler((req, res) => checkoutController.checkout(req, res)));
    router.get('/api/admin/financial-report', adminAuth, asyncHandler((req, res) => adminController.financialReport(req, res)));
    router.delete('/api/users/:id', adminAuth, asyncHandler((req, res) => userController.remove(req, res)));

    return router;
}

module.exports = buildRoutes;

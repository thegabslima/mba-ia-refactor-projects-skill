const express = require('express');
const settings = require('./config/settings');
const Database = require('./models/database');
const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const AuditLogModel = require('./models/auditLogModel');
const ReportModel = require('./models/reportModel');
const CheckoutController = require('./controllers/checkoutController');
const AdminController = require('./controllers/adminController');
const UserController = require('./controllers/userController');
const buildRoutes = require('./views/routes');
const { errorHandler } = require('./middlewares/errorHandler');
const logger = require('./services/logger');

async function createApp() {
    const database = new Database(settings.dbFile);
    await database.init();

    const userModel = new UserModel(database);
    const models = {
        userModel,
        courseModel: new CourseModel(database),
        enrollmentModel: new EnrollmentModel(database),
        paymentModel: new PaymentModel(database),
        auditLogModel: new AuditLogModel(database),
        reportModel: new ReportModel(database),
    };

    const app = express();
    app.use(express.json());
    app.use(buildRoutes({
        checkoutController: new CheckoutController(models),
        adminController: new AdminController(models),
        userController: new UserController(models),
    }));
    app.use(errorHandler);
    return app;
}

createApp()
    .then((app) => app.listen(settings.port, () => {
        logger.info(`Frankenstein LMS rodando na porta ${settings.port}...`);
    }))
    .catch((err) => {
        logger.error(err.stack || String(err));
        process.exit(1);
    });

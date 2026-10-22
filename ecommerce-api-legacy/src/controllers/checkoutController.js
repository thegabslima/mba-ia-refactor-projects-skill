const crypto = require('crypto');
const { paymentStatus } = require('../config/settings');
const { hashPassword } = require('../services/passwordHasher');
const paymentGateway = require('../services/paymentGateway');
const logger = require('../services/logger');

class CheckoutController {
    constructor({ courseModel, userModel, enrollmentModel, paymentModel, auditLogModel }) {
        this.courseModel = courseModel;
        this.userModel = userModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
        this.auditLogModel = auditLogModel;
    }

    // Os nomes curtos do payload (usr, eml, pwd, c_id, card) fazem parte do contrato público.
    async checkout(req, res) {
        const { usr: name, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body || {};

        if (!name || !email || !courseId || typeof cardNumber !== 'string' || !cardNumber) {
            return res.status(400).send('Bad Request');
        }

        const course = await this.courseModel.findActiveById(courseId);
        if (!course) return res.status(404).send('Curso não encontrado');

        const status = paymentGateway.charge(cardNumber, course.price);
        if (status === paymentStatus.DENIED) return res.status(400).send('Pagamento recusado');

        let user = await this.userModel.findByEmail(email);
        let userId = user ? user.id : null;
        if (!userId) {
            const initialPassword = password || crypto.randomBytes(12).toString('hex');
            userId = await this.userModel.create(name, email, hashPassword(initialPassword));
        }

        const enrollmentId = await this.enrollmentModel.create(userId, courseId);
        await this.paymentModel.create(enrollmentId, course.price, status);
        await this.auditLogModel.record(`Checkout curso ${courseId} por ${userId}`);

        logger.info(`Checkout concluído: curso ${courseId}, usuário ${userId}`);
        return res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
    }
}

module.exports = CheckoutController;

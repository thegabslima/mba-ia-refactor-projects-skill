const logger = require('../services/logger');

class UserController {
    constructor({ userModel }) {
        this.userModel = userModel;
    }

    async remove(req, res) {
        const id = Number(req.params.id);
        if (!Number.isInteger(id)) return res.status(400).send('Bad Request');

        await this.userModel.remove(id);
        logger.info(`Usuário ${id} removido (matrículas e pagamentos em cascata)`);
        return res.send('Usuário deletado');
    }
}

module.exports = UserController;

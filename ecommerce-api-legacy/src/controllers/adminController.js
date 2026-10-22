class AdminController {
    constructor({ reportModel }) {
        this.reportModel = reportModel;
    }

    async financialReport(req, res) {
        const report = await this.reportModel.financialByCourse();
        res.json(report);
    }
}

module.exports = AdminController;

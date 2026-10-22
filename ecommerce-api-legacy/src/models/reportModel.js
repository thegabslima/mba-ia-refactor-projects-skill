const { paymentStatus } = require('../config/settings');

class ReportModel {
    constructor(database) {
        this.database = database;
    }

    /** Receita e alunos por curso, em uma única query (sem N+1). */
    async financialByCourse() {
        const rows = await this.database.all(`
            SELECT c.id AS course_id, c.title, e.id AS enrollment_id,
                   u.name AS student, p.amount, p.status
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u ON u.id = e.user_id
            LEFT JOIN payments p ON p.enrollment_id = e.id
            ORDER BY c.id, e.id
        `);

        const byCourse = new Map();
        for (const row of rows) {
            if (!byCourse.has(row.course_id)) {
                byCourse.set(row.course_id, { course: row.title, revenue: 0, students: [] });
            }
            if (row.enrollment_id === null) continue;

            const entry = byCourse.get(row.course_id);
            if (row.status === paymentStatus.PAID) entry.revenue += row.amount;
            entry.students.push({
                student: row.student || 'Unknown',
                paid: row.amount ?? 0,
            });
        }
        return [...byCourse.values()];
    }
}

module.exports = ReportModel;

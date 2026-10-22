class EnrollmentModel {
    constructor(database) {
        this.database = database;
    }

    async create(userId, courseId) {
        const { lastID } = await this.database.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId],
        );
        return lastID;
    }
}

module.exports = EnrollmentModel;

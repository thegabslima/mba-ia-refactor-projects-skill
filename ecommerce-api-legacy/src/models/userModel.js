class UserModel {
    constructor(database) {
        this.database = database;
    }

    findByEmail(email) {
        return this.database.get('SELECT id FROM users WHERE email = ?', [email]);
    }

    async create(name, email, passwordHash) {
        const { lastID } = await this.database.run(
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [name, email, passwordHash],
        );
        return lastID;
    }

    async remove(id) {
        const { changes } = await this.database.run('DELETE FROM users WHERE id = ?', [id]);
        return changes > 0;
    }
}

module.exports = UserModel;

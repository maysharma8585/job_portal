#include "DatabaseManager.h"

#include <QSqlError>

DatabaseManager &DatabaseManager::instance() {
    static DatabaseManager manager;
    return manager;
}

bool DatabaseManager::connect(QString *error) {
    if (db_.isOpen()) return true;
    db_ = QSqlDatabase::contains("job-portal")
        ? QSqlDatabase::database("job-portal")
        : QSqlDatabase::addDatabase("QMYSQL", "job-portal");
    db_.setHostName(qEnvironmentVariable("JOB_PORTAL_DB_HOST", "127.0.0.1"));
    db_.setPort(qEnvironmentVariableIntValue("JOB_PORTAL_DB_PORT") > 0
                    ? qEnvironmentVariableIntValue("JOB_PORTAL_DB_PORT") : 3306);
    db_.setDatabaseName(qEnvironmentVariable("JOB_PORTAL_DB_NAME", "job_portal_db"));
    db_.setUserName(qEnvironmentVariable("JOB_PORTAL_DB_USER", "root"));
    db_.setPassword(qEnvironmentVariable("JOB_PORTAL_DB_PASSWORD"));
    if (!db_.open()) {
        if (error) *error = db_.lastError().text();
        return false;
    }
    return true;
}

QSqlDatabase DatabaseManager::database() const { return db_; }

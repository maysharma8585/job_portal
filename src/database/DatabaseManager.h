#pragma once

#include <QSqlDatabase>
#include <QString>

class DatabaseManager {
public:
    static DatabaseManager &instance();
    bool connect(QString *error = nullptr);
    QSqlDatabase database() const;
private:
    DatabaseManager() = default;
    QSqlDatabase db_;
};

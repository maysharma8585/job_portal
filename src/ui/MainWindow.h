#pragma once

#include <QMainWindow>
#include <QStringList>

class QStackedWidget;
class QListWidget;

class MainWindow : public QMainWindow {
public:
    explicit MainWindow(QWidget *parent = nullptr);
private:
    QWidget *makePage(const QString &title, const QString &subtitle, const QStringList &actions = {});
    void navigate(int index);
    QStackedWidget *pages_{};
    QListWidget *navigation_{};
};

#include "app/AppController.h"

#include <QApplication>

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    QApplication::setApplicationName("Job Portal");
    QApplication::setOrganizationName("Academic Project");
    AppController controller;
    controller.show();
    return app.exec();
}

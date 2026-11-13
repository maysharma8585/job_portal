#pragma once

#include "ui/MainWindow.h"

class AppController {
public:
    AppController();
    void show();
private:
    MainWindow window_;
};

cmake_minimum_required(VERSION 3.21)
project(JobPortalManagementSystem VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

find_package(Qt6 6.2 REQUIRED COMPONENTS Widgets Sql)

qt_add_executable(job-portal
    src/main.cpp
    src/app/AppController.cpp src/app/AppController.h
    src/database/DatabaseManager.cpp src/database/DatabaseManager.h
    src/ui/MainWindow.cpp src/ui/MainWindow.h
)
target_link_libraries(job-portal PRIVATE Qt6::Widgets Qt6::Sql)
target_include_directories(job-portal PRIVATE src)

install(TARGETS job-portal RUNTIME DESTINATION bin)

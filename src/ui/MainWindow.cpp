#include "MainWindow.h"
#include "database/DatabaseManager.h"

#include <QApplication>
#include <QFrame>
#include <QHBoxLayout>
#include <QLabel>
#include <QListWidget>
#include <QMessageBox>
#include <QPushButton>
#include <QStackedWidget>
#include <QVBoxLayout>

namespace {
QLabel *label(const QString &text, const QString &style = {}) {
    auto *widget = new QLabel(text);
    if (!style.isEmpty()) widget->setStyleSheet(style);
    widget->setWordWrap(true);
    return widget;
}
}

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
    setWindowTitle("Northstar · Job Portal");
    setMinimumSize(1080, 700);
    auto *root = new QWidget;
    auto *layout = new QHBoxLayout(root);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(0);

    auto *sidebar = new QWidget;
    sidebar->setFixedWidth(235);
    sidebar->setStyleSheet("background:#10253f; color:#edf4ff;");
    auto *side = new QVBoxLayout(sidebar);
    side->setContentsMargins(18, 24, 18, 18);
    auto *brand = label("✳  NORTHSTAR\n     CAREERS", "font-size:18px;font-weight:700;color:white;padding:0 0 16px 4px;");
    side->addWidget(brand);
    side->addWidget(label("WORKSPACE", "color:#8299b5;font-size:10px;font-weight:700;letter-spacing:2px;padding:8px 4px;"));
    navigation_ = new QListWidget;
    navigation_->setFrameShape(QFrame::NoFrame);
    navigation_->setStyleSheet("QListWidget{background:transparent;color:#c8d5e5;border:0;font-size:13px} QListWidget::item{padding:11px 10px;border-radius:7px;margin:2px 0} QListWidget::item:selected{background:#254667;color:white;font-weight:600}");
    const QStringList names = {"Overview", "Find a job", "My applications", "My profile", "Employer home", "Post a job", "Manage jobs", "Applicants", "Company profile", "Admin overview", "User management", "Job moderation", "Reports & help"};
    for (const auto &name : names) navigation_->addItem(name);
    side->addWidget(navigation_, 1);
    side->addWidget(label("ACADEMIC PROJECT · LOCAL", "color:#8299b5;font-size:10px;padding:8px 4px;"));
    layout->addWidget(sidebar);

    auto *content = new QWidget;
    content->setStyleSheet("background:#f5f7fb;color:#152943;font-family:'Arial';");
    auto *column = new QVBoxLayout(content);
    column->setContentsMargins(34, 22, 34, 26);
    auto *top = new QHBoxLayout;
    top->addWidget(label("JOB PORTAL  /  WORKSPACE", "color:#73839a;font-size:11px;font-weight:700;letter-spacing:1px;"));
    top->addStretch();
    auto *signin = new QPushButton("Sign in / Register");
    signin->setStyleSheet("background:#ffffff;border:1px solid #d9e1ec;border-radius:8px;padding:9px 14px;font-weight:600;");
    top->addWidget(signin);
    column->addLayout(top);

    pages_ = new QStackedWidget;
    const QStringList titles = {"Your next move starts here", "Find your next opportunity", "My applications", "Your professional profile", "Hiring at a glance", "Create a vacancy", "Manage your jobs", "Applicants", "Company profile", "Portal overview", "User management", "Job moderation", "Reports, about & help"};
    const QStringList subtitles = {
        "A clear view of opportunities and activity across your career workspace.",
        "Search open roles by title, location, category, or employment type.",
        "Keep track of the roles you applied for and their latest status.",
        "Show employers the experience and skills you bring.",
        "Review your open roles, applicant activity, and hiring progress.",
        "Share a well-described opportunity with job seekers.",
        "Review your vacancies and update their status.",
        "Review candidates for a vacancy you own and record a decision.",
        "Keep your organization details up to date.",
        "A simple snapshot of accounts, vacancies, and applications.",
        "Review account records and access status.",
        "Review listings and close content that should no longer be public.",
        "Project information and short guides for each role."};
    for (int i = 0; i < titles.size(); ++i) {
        QStringList actions;
        if (i == 0) actions = {"Browse open jobs", "Create an account", "I’m hiring"};
        if (i == 1) actions = {"Search jobs", "Clear filters", "Open job details"};
        if (i == 2) actions = {"Refresh applications", "View application details"};
        if (i == 3) actions = {"Edit profile", "Save changes"};
        if (i == 4) actions = {"Post a job", "Review applicants", "Edit company profile"};
        if (i == 5) actions = {"Publish job", "Cancel"};
        if (i == 6) actions = {"View", "Edit", "View applicants", "Close job"};
        if (i == 7) actions = {"View application", "Shortlist", "Reject", "Mark hired"};
        if (i == 8) actions = {"Edit company details", "Save changes"};
        if (i == 9) actions = {"Manage users", "Moderate jobs", "Refresh statistics"};
        if (i == 10) actions = {"Search users", "Filter by role", "Activate / deactivate"};
        if (i == 11) actions = {"Filter open / closed", "Preview listing", "Close listing"};
        pages_->addWidget(makePage(titles[i], subtitles[i], actions));
    }
    column->addWidget(pages_, 1);
    layout->addWidget(content, 1);
    setCentralWidget(root);
    connect(navigation_, &QListWidget::currentRowChanged, this, [this](int row) { navigate(row); });
    connect(signin, &QPushButton::clicked, this, [this] { navigate(0); QMessageBox::information(this, "Accounts", "Account screens will be available after database configuration."); });
    navigation_->setCurrentRow(0);
}

QWidget *MainWindow::makePage(const QString &title, const QString &subtitle, const QStringList &actions) {
    auto *page = new QWidget;
    auto *layout = new QVBoxLayout(page);
    layout->setContentsMargins(0, 36, 0, 0);
    layout->addWidget(label(title, "font-size:30px;font-weight:700;color:#142a45;"));
    layout->addWidget(label(subtitle, "font-size:14px;color:#6f8097;padding-top:4px;"));
    auto *card = new QFrame;
    card->setStyleSheet("QFrame{background:white;border:1px solid #e1e7f0;border-radius:13px;}");
    auto *cardLayout = new QVBoxLayout(card);
    cardLayout->setContentsMargins(24, 22, 24, 22);
    cardLayout->addWidget(label("Welcome to your workspace", "font-size:16px;font-weight:700;color:#18314f;"));
    cardLayout->addWidget(label("Connect the MySQL database to load live portal records. This project starts with an empty database; sample listings are never presented as real vacancies.", "font-size:13px;color:#718198;padding-top:4px;"));
    if (!actions.isEmpty()) {
        auto *row = new QHBoxLayout;
        row->setSpacing(9);
        for (int i = 0; i < actions.size(); ++i) {
            auto *button = new QPushButton(actions[i]);
            const QString bg = i == 0 ? "#2366d1" : "#ffffff";
            const QString fg = i == 0 ? "white" : "#28415f";
            button->setStyleSheet(QString("QPushButton{background:%1;color:%2;border:1px solid #d9e1ec;border-radius:7px;padding:9px 13px;font-weight:600} QPushButton:hover{border-color:#7c9ec8}").arg(bg, fg));
            row->addWidget(button);
            connect(button, &QPushButton::clicked, this, [this, action = actions[i]] {
                if (action.contains("job", Qt::CaseInsensitive) || action.contains("vacancy", Qt::CaseInsensitive)) navigate(1);
                else if (action.contains("applicant", Qt::CaseInsensitive)) navigate(7);
                else if (action.contains("company", Qt::CaseInsensitive)) navigate(8);
                else QMessageBox::information(this, "Job Portal", action + " requires a connected database and signed-in account.");
            });
        }
        row->addStretch();
        cardLayout->addSpacing(16);
        cardLayout->addLayout(row);
    }
    layout->addSpacing(25);
    layout->addWidget(card);
    layout->addStretch();
    auto *footer = label("Northstar Job Portal  ·  C++17 / Qt Widgets / MySQL", "color:#8190a5;font-size:11px;padding-bottom:4px;");
    layout->addWidget(footer);
    return page;
}

void MainWindow::navigate(int index) {
    if (index >= 0 && index < pages_->count()) pages_->setCurrentIndex(index);
}

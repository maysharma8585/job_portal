# Job Portal Management System




```bash
python3 app.py --create-admin admin@example.com "Portal Administrator"
```

Optional settings: `JOB_PORTAL_HOST`, `JOB_PORTAL_PORT`, and
`JOB_PORTAL_DB_PATH`. For HTTPS deployments behind a trusted TLS proxy, set
`JOB_PORTAL_SECURE_COOKIE=1`. The built-in server is intended for local
academic use, not public production hosting.

### Implemented workflows

- Seeker and employer registration, login, logout, password hashing, and role-specific navigation.
- Search and filter open roles, view details, and apply once per vacancy.
- Seeker profile editing, application tracking, and withdrawal while pending or shortlisted.
- Employer company profile, vacancy publishing/editing/closing, applicant review, and status decisions.
- Admin statistics, account activation, and listing moderation with application history preserved.
- Responsive browser UI, empty states, form validation, and SQLite-backed persistence.

See [docs/user-manual.md](docs/user-manual.md) for setup and workflow details.

> A simple, student-friendly job portal where job seekers can find and apply for jobs, and employers can post and manage vacancies.

---

## 1. Project Overview

The **Job Portal Management System** is an academic software project that brings job seekers and employers together in one application.

Job seekers can create a profile, browse available jobs, search and filter listings, and submit applications. Employers can create a company profile, post vacancies, view applicants, and update application statuses. An administrator can manage basic records and monitor the portal.

The application will be built in **C++**, with a **Qt Widgets desktop interface** and a **MySQL database**. Qt is a C++ framework, so the application stays within the project guideline that specifies C/C++ as the frontend language and MySQL/MS Access as the backend database.

The goal is a clear, functional academic project—not a commercial-scale recruitment platform. We will build it in small steps, keep the code understandable, and avoid unnecessary features.

### Initial project decisions

| Item | Decision |
|---|---|
| Project title | Job Portal Management System |
| Language | C++ |
| User interface | Qt Widgets desktop GUI |
| Database | MySQL |
| Database access | Qt SQL module |
| IDE/editor | VS Code (or Qt Creator if needed for Qt Designer) |
| Compiler/build system | Compatible C++ compiler and CMake |
| Version control | Git |
| Project level | BCA academic project |
| First milestone | A working GUI shell with navigation |
| Complexity | Basic-to-intermediate; no AI, payments, or external APIs |

**Important:** Confirm with the faculty that a Qt desktop GUI is acceptable. If the college requires a console-only application or specifically requires MS Access, update this specification before implementation.

---

## 2. Problem Statement

Searching and managing job opportunities through scattered notices, messages, and spreadsheets can be inconvenient. Employers also need a simple way to publish vacancies and review applicants.

The proposed Job Portal Management System will keep job listings, user profiles, applications, and application statuses in one database-backed application. It will provide separate screens for job seekers, employers, and administrators.

---

## 3. Project Objectives

1. Create a working job portal using C++.
2. Demonstrate Object-Oriented Programming concepts.
3. Store application data in MySQL.
4. Provide a distinct, easy-to-understand screen for every main feature.
5. Allow job seekers to browse and apply for jobs.
6. Allow employers to post jobs and manage applications.
7. Provide basic administration of users and listings.
8. Validate user input and handle errors clearly.
9. Prepare the synopsis, project report, test cases, screenshots, and viva notes.
10. Keep the code simple enough for the student to explain during evaluation.

---

## 4. Users and Roles

### 4.1 Visitor

A visitor can view the welcome screen and browse public job listings. Applying for a job or using account-specific features requires signing in.

### 4.2 Job Seeker

A job seeker can:
- Register and sign in.
- Create and edit a profile.
- Browse, search, and filter jobs.
- View full job details.
- Apply for a job.
- View submitted applications and their statuses.
- Withdraw an application if it has not reached a final status, where allowed.

### 4.3 Employer

An employer can:
- Register and sign in.
- Create and edit a company profile.
- Post a job vacancy.
- View and manage their own job postings.
- View applicants for their vacancies.
- Update application statuses.
- Close a vacancy when recruitment is finished.

### 4.4 Administrator

An administrator can:
- View basic portal statistics.
- View and manage user accounts.
- Review job listings.
- Remove inappropriate or duplicate listings.
- View application records for administrative purposes.

For a manageable academic version, administrator access may be seeded through a setup script rather than a public admin-registration form. Do not hard-code real passwords in source code.

---

## 5. Scope: What We Will and Will Not Build

### Included in the initial project

- Registration and login for job seekers and employers
- Basic role-based navigation
- Job seeker profile
- Employer/company profile
- Job posting CRUD (create, read, update, delete/close)
- Job search and filters
- Job details
- Job application submission
- Application history and status
- Employer applicant management
- Basic administrator screens
- MySQL persistence
- Form validation and user-friendly errors
- Testing and project documentation

### Not included unless the faculty specifically asks

- AI-based job matching
- Online payments or subscriptions
- Real email/SMS delivery
- External authentication providers
- Live video interviews
- Complex resume parsing
- Production hosting or mobile applications
- Multi-company enterprise permissions
- Cloud storage for uploaded resumes

For the first version, a resume can be represented by a text field or an optional local file path. If file uploads are implemented, they must be handled safely and documented clearly.

---

## 6. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Programming language | C++17 or newer compatible with installed tools | Application logic |
| GUI | Qt Widgets | Desktop windows, forms, tables, dialogs |
| Database | MySQL | Persistent records |
| Database access | Qt SQL (`QSqlDatabase`, `QSqlQuery`) | Connect and execute queries |
| Build system | CMake | Configure and build the project |
| IDE/editor | VS Code; Qt Creator optional | Development and UI design |
| Version control | Git | Track changes |
| Documentation | Markdown; PDF for final report if required | Project documentation |

Use the Qt version and MySQL driver available for the development environment. Verify that the Qt SQL MySQL driver is installed and compatible before writing the database layer.

---

## 7. Application Architecture

Keep the application divided into clear responsibilities:

```text
User
 |
 v
Qt Widgets UI (screens, forms, tables, dialogs)
 |
 v
Services (validation and business rules)
 |
 v
Repositories / Database layer (parameterized SQL)
 |
 v
MySQL database
```

### UI layer
Displays screens, gathers input, and presents results. It should not contain large SQL queries or business rules.

### Service layer
Checks rules such as whether required fields are filled, whether a job is open, and whether the user is allowed to apply.

### Database/repository layer
Reads and writes records using parameterized SQL queries. It reports success or failure to the service layer.

### Database
Stores users, profiles, jobs, applications, and related records.

Keep the design simple. Do not introduce a large framework or complex architecture unless it solves a real project need.

---

## 8. UI/UX Requirement: Every Main Function Gets Its Own Screen

**Core requirement:** Each main feature must have a distinct, purpose-built UI. Do not put the entire application on one crowded screen, and do not make every screen look identical.

Use a consistent visual system (same font family, spacing, buttons, colors, and navigation) but give each feature a layout suited to its task. The following screen descriptions are the UI specification for Codex.

### Shared design system

- Desktop-first layout with a reasonable minimum window size.
- Left sidebar or top navigation with role-appropriate menu items.
- Main content area with a clear page title and short description.
- Reusable primary, secondary, and danger button styles.
- Forms with visible labels and inline validation messages.
- Tables with readable column headings and empty states.
- Confirmation dialog before destructive actions.
- Success and error feedback after important actions.
- Loading indicators where an operation may take time.
- Keyboard-friendly controls and sensible tab order.
- Do not rely on color alone to communicate status.
- Use realistic sample data only; do not present sample records as real vacancies.
- Each screen should have its own layout, content hierarchy, and relevant actions.

### Screen 1 — Welcome / Landing Screen

**Purpose:** Introduce the portal and direct the user to relevant actions.

**Unique layout:**
- Header with portal name and Sign In / Register actions.
- Main welcome panel with a short tagline.
- Prominent job-search input.
- Recent job cards or a small featured-jobs section.
- Three clear entry actions: Find Jobs, Employer Area, Sign In.

**Actions:** Search jobs, open a job detail screen, navigate to sign-in or registration.

**Empty/error states:** Show a friendly message if no public jobs are available.

### Screen 2 — Registration Screen

**Purpose:** Create a job seeker or employer account.

**Unique layout:**
- Two role-selection cards: “I’m looking for a job” and “I’m hiring”.
- Form fields change based on the selected role.
- Job seeker fields: full name, email, password, confirm password.
- Employer fields: contact name, email, password, confirm password, company name.
- Clear terms/information note if required by the college.

**Actions:** Validate fields, create the account, navigate to sign-in.

**Validation:** Required fields, valid email format, matching passwords, duplicate email handling, password minimum length.

### Screen 3 — Sign-In Screen

**Purpose:** Authenticate a registered user.

**Unique layout:**
- Focused centered sign-in panel.
- Email and password fields.
- Show/hide password control if practical.
- Sign In button and links to registration.
- Clear account-role routing after successful login.

**Actions:** Authenticate, show a helpful error for invalid credentials, route to the correct dashboard.

**Security:** Store password hashes, not plain-text passwords. Use a suitable password-hashing library or a documented secure approach; never invent your own cryptographic algorithm.

### Screen 4 — Job Seeker Dashboard

**Purpose:** Give a job seeker a summary of their activity.

**Unique layout:**
- Welcome heading.
- Summary tiles: Available Jobs, Applications Submitted, Shortlisted (if any).
- Recent job recommendations based on simple categories or newest listings; no AI.
- Recent application activity list.
- Quick actions for Search Jobs and Edit Profile.

**Actions:** Open search, profile, application history, or a job detail page.

### Screen 5 — Job Search / Browse Jobs

**Purpose:** Find suitable job vacancies.

**Unique layout:**
- Search bar at the top.
- Filter panel for keyword, location, job type, and category.
- Results displayed as clean job cards or a table with readable spacing.
- Each job card shows title, company, location, job type, and posting date.
- Sort options such as newest first.
- Clear Filters action.

**Actions:** Search, filter, reset filters, open job details.

**Validation/states:** Empty search should show available jobs; no matches should show a dedicated “No jobs found” state; database errors should be displayed clearly.

### Screen 6 — Job Details Screen

**Purpose:** Show the full information for one vacancy.

**Unique layout:**
- Large job title and company name at the top.
- Highlighted metadata row for location, job type, and salary if provided.
- Separate sections for job description, requirements, and responsibilities.
- Posting date and status.
- A visible Apply button for eligible job seekers.

**Actions:** Apply, return to search, sign in if required.

**Rules:** Closed jobs cannot be applied to. An applicant cannot apply twice to the same job.

### Screen 7 — Job Application Form

**Purpose:** Submit an application to a selected vacancy.

**Unique layout:**
- Compact job summary at the top.
- Form containing a short cover letter and optional resume path or file selection, if implemented.
- Clear Submit Application and Cancel actions.
- Confirmation step before submission.

**Actions:** Validate and submit, cancel, show application success.

**Rules:** Only signed-in job seekers can apply; the job must be open; duplicate applications must be prevented. Do not report success unless the database confirms the application was saved.

### Screen 8 — My Applications

**Purpose:** Let job seekers track their applications.

**Unique layout:**
- Summary strip for total, pending, shortlisted, and rejected applications.
- Table/list with job title, company, application date, and status.
- Status badges with text labels.
- Clicking an item opens application details.

**Actions:** View details, refresh status, withdraw if permitted.

**States:** Dedicated empty state when no applications exist. Status values should be consistent throughout the application, for example `Pending`, `Shortlisted`, `Rejected`, and `Hired`.

### Screen 9 — Job Seeker Profile

**Purpose:** Maintain the seeker's professional information.

**Unique layout:**
- Profile header with initials/avatar placeholder.
- Separate sections for contact details, skills, education, experience, and resume reference.
- Edit mode with Save and Cancel actions.
- Profile-completion indicator only if its calculation is simple and clearly explained.

**Actions:** View/edit profile, save changes.

**Validation:** Required fields and reasonable length limits. Do not require sensitive information that the project does not need.

### Screen 10 — Employer Dashboard

**Purpose:** Summarize recruitment activity for an employer.

**Unique layout:**
- Company welcome panel.
- Summary tiles: Active Jobs, Closed Jobs, Total Applicants.
- Recent applicants list.
- Quick action to Post a Job.
- Recent job postings with their current status.

**Actions:** Post a job, manage postings, review applicants, edit company profile.

**Authorization:** An employer may only manage jobs and applications associated with that employer's account.

### Screen 11 — Post a Job

**Purpose:** Create a vacancy.

**Unique layout:**
- Form divided into clear sections:
  1. Job basics
  2. Description and requirements
  3. Location and employment type
  4. Salary range (optional)
  5. Application deadline (optional)
- Preview or summary panel where practical.
- Save Draft is optional; Publish Job is the primary action.

**Fields:** Job title, category, description, requirements, location, employment type, salary range (optional), deadline (optional).

**Validation:** Required fields, sensible salary range, valid deadline, description length.

**Actions:** Publish, cancel, edit before publishing.

### Screen 12 — Manage My Jobs

**Purpose:** Allow employers to manage their own job postings.

**Unique layout:**
- Filter tabs: All, Open, Closed.
- Table with title, posting date, status, and applicant count.
- Row actions: View, Edit, View Applicants, Close Job.
- Visually distinct closed-job state.

**Actions:** Edit, close, reopen if allowed, view applicants.

**Rules:** Never allow one employer to edit another employer's vacancy. Confirm closing or deleting a job. Prefer closing over hard deletion when applications already exist.

### Screen 13 — Applicants for a Job

**Purpose:** Help an employer review applications for a selected vacancy.

**Unique layout:**
- Job summary header.
- Applicant table with applicant name, application date, and current status.
- Applicant detail panel or dialog for cover letter and profile summary.
- Status control with an explicit Save/Update action.

**Actions:** View application, shortlist, reject, mark hired, update status.

**Rules:** Only the owner of the job can manage its applicants. Record status changes consistently. Do not expose unrelated applicants or private records.

### Screen 14 — Company Profile

**Purpose:** Manage the employer's company information.

**Unique layout:**
- Company header with logo placeholder.
- Sections for company name, industry, location, website, and description.
- Editable form with Save and Cancel actions.

**Actions:** View and update company details.

**Validation:** Required company name; validate website format if supplied.

### Screen 15 — Administrator Dashboard

**Purpose:** Provide a simple overview of portal activity.

**Unique layout:**
- Summary tiles for users, employers, open jobs, and applications.
- Recent job postings.
- Small list of recent activity or flagged listings if moderation is implemented.
- Clear navigation to user and job management.

**Actions:** Navigate to management screens and refresh statistics.

### Screen 16 — User Management (Admin)

**Purpose:** View and manage accounts.

**Unique layout:**
- Searchable table with user name, email, role, and account status.
- Filter by role.
- User details dialog.
- Activate/deactivate action with confirmation.

**Rules:** Prevent an administrator from accidentally disabling their own active account if that would lock the project out. Do not display password hashes or passwords.

### Screen 17 — Job Moderation (Admin)

**Purpose:** Review public job listings.

**Unique layout:**
- Table of job postings with title, employer, date, and status.
- Filters for open and closed jobs.
- A job-preview panel.
- Remove/close action with a confirmation dialog and reason if appropriate.

**Rules:** Preserve application history. Prefer closing or marking a listing as removed instead of deleting linked records.

### Screen 18 — Reports / About / Help

**Purpose:** Provide a small amount of useful information without expanding the project too much.

**Unique layout:**
- Reports page: totals for users, active jobs, and applications, using simple tables or statistic cards.
- About page: project purpose, technologies, and academic-project note.
- Help page: brief instructions for job seekers and employers.

These can be separate pages or a single Help & About section, depending on time.

### Shared dialogs and UI states

In addition to the screens above, implement reusable but context-specific dialogs for:
- Confirm delete/close
- Confirm application submission
- Success notification
- Error notification
- Session/logout confirmation if needed
- Database connection error
- Unsaved changes warning, if practical

Dialogs may share visual styling, but their wording and actions must match the operation. Every main function should have an appropriate loading, success, empty, and error state where relevant.

---

## 9. Functional Requirements

### Account management
- Register job seeker and employer accounts.
- Sign in and sign out.
- Identify the role after successful authentication.
- Store password hashes securely.
- Validate required fields and duplicate emails.

### Job management
- Create, read, update, and close job postings.
- Search by keyword and filter by location, type, and category.
- Show full job details.
- Prevent applications to closed jobs.

### Application management
- Submit an application for an open job.
- Prevent duplicate applications by the same job seeker for the same job.
- Show application history to the applicant.
- Let the employer review applicants for their own job.
- Update and display application statuses.

### Profile management
- Create and edit job seeker profile.
- Create and edit company profile.
- Validate user-provided values.

### Administration
- View basic statistics.
- View user and job records.
- Activate/deactivate accounts and moderate listings, subject to simple authorization rules.

### Reliability
- Show clear validation and database error messages.
- Use parameterized SQL queries.
- Do not lose application data when the program closes.
- Keep linked records consistent.

---

## 10. Database Design

Use a database named `job_portal_db`. The initial design may contain these tables; Codex should refine the schema before implementation and document every change.

### 10.1 `users`

| Column | Purpose |
|---|---|
| `user_id` | Primary key |
| `full_name` | User's display name |
| `email` | Unique login email |
| `password_hash` | Secure password hash |
| `role` | `job_seeker`, `employer`, or `admin` |
| `is_active` | Whether the account is active |
| `created_at` | Registration timestamp |

### 10.2 `job_seeker_profiles`

| Column | Purpose |
|---|---|
| `profile_id` | Primary key |
| `user_id` | Foreign key to `users` |
| `phone` | Optional contact number |
| `skills` | Basic skills text |
| `education` | Education summary |
| `experience` | Experience summary |
| `resume_path` | Optional local file reference |

### 10.3 `companies`

| Column | Purpose |
|---|---|
| `company_id` | Primary key |
| `owner_user_id` | Employer account |
| `company_name` | Company name |
| `industry` | Optional industry |
| `location` | Optional location |
| `website` | Optional website |
| `description` | Company summary |

### 10.4 `jobs`

| Column | Purpose |
|---|---|
| `job_id` | Primary key |
| `company_id` | Foreign key to `companies` |
| `title` | Job title |
| `category` | Job category |
| `description` | Job description |
| `requirements` | Skills/requirements |
| `location` | Job location |
| `employment_type` | Full-time, part-time, internship, etc. |
| `salary_min` | Optional minimum salary |
| `salary_max` | Optional maximum salary |
| `deadline` | Optional application deadline |
| `status` | Open, closed, or removed |
| `created_at` | Posting timestamp |

### 10.5 `applications`

| Column | Purpose |
|---|---|
| `application_id` | Primary key |
| `job_id` | Foreign key to `jobs` |
| `job_seeker_id` | Foreign key to `users` |
| `cover_letter` | Applicant's message |
| `resume_path` | Optional resume reference |
| `status` | Pending, shortlisted, rejected, or hired |
| `applied_at` | Application timestamp |
| `updated_at` | Last status update |

### Database rules

- Add primary keys, foreign keys, and appropriate indexes.
- Enforce unique email addresses.
- Prevent duplicate applications with a unique constraint on `(job_id, job_seeker_id)`.
- Use parameterized SQL through Qt SQL.
- Do not store plain-text passwords.
- Do not commit database credentials to Git.
- Use transactions when one action updates multiple related records.
- Validate ownership and user roles in the service/business logic, not just by hiding UI buttons.
- Preserve application history when a job is closed or removed.
- Store date/time values consistently and document the convention.
- If resume files are supported, define where files live and avoid storing arbitrary unsafe paths from user input.

---

## 11. OOP Concepts Required by the Guidelines

The final project and report must explain these concepts with examples from the actual code.

### Class
A blueprint that combines data and behaviour. Examples may include `Job`, `User`, `Company`, and `Application`.

### Object
An instance of a class. For example, a particular `Job` object represents one vacancy retrieved from the database.

### Encapsulation
Keep internal state private and provide suitable methods for accessing or changing it. Avoid making every field public without a reason.

### Abstraction
Expose clear operations such as `applyForJob()` while hiding SQL details and validation steps inside service/repository classes.

### Inheritance
Use a meaningful base/derived relationship if it improves the design. For example, a base `User` type could be extended by `JobSeeker` and `Employer`. Do not introduce inheritance only to tick a box if it makes the code harder to understand.

### Polymorphism
If inheritance is used, demonstrate polymorphism with a virtual method and derived implementations where appropriate. Explain the code and why it is useful.

**Academic deliverable:** `docs/oop-concepts.md` should define each concept, include a short relevant code example, and identify where it appears in the application.

---

## 12. Feasibility Study

### Technical feasibility
C++, Qt Widgets, and MySQL are established technologies. A desktop GUI and local database are achievable on a normal development computer. The MySQL Qt driver and compatible tool versions must be verified first.

### Economic feasibility
The project can be developed with free development tools. No paid hosting, payment service, or commercial API is required for the initial version.

### Operational / behavioural feasibility
Separate screens and role-specific navigation should make the application straightforward to use. Labels, validation messages, confirmations, and empty states will guide users.

### Time feasibility
The project will be implemented in milestones. The core account, job, and application workflows take priority over optional reports or advanced features.

---

## 13. Hardware and Software Requirements

### Suggested hardware
- Dual-core processor or better
- 4 GB RAM minimum; 8 GB recommended
- Approximately 2 GB or more of free disk space for development tools, database, and build files
- Keyboard and display

### Software
- Ubuntu Linux or another OS supported by the chosen Qt/MySQL versions
- C++ compiler
- CMake
- Qt Widgets and Qt SQL modules
- MySQL Server
- Qt SQL MySQL driver
- VS Code and/or Qt Creator
- Git

Actual requirements depend on installed versions and the size of the development environment.

---

## 14. Proposed Repository Structure

Use this as a target structure. Create files gradually rather than generating the entire application in one step.

```text
job-portal/
├── README.md
├── CMakeLists.txt
├── .gitignore
├── .env.example
├── src/
│   ├── main.cpp
│   ├── app/
│   │   ├── AppController.h
│   │   └── AppController.cpp
│   ├── models/
│   │   ├── User.h
│   │   ├── Job.h
│   │   ├── Company.h
│   │   └── Application.h
│   ├── database/
│   │   ├── DatabaseManager.h
│   │   └── DatabaseManager.cpp
│   ├── repositories/
│   │   ├── UserRepository.h
│   │   ├── JobRepository.h
│   │   └── ApplicationRepository.h
│   ├── services/
│   │   ├── AuthService.h
│   │   ├── JobService.h
│   │   └── ApplicationService.h
│   └── ui/
│       ├── MainWindow.h
│       ├── MainWindow.cpp
│       ├── screens/
│       ├── dialogs/
│       └── widgets/
├── database/
│   ├── schema.sql
│   ├── sample_data.sql
│   └── README.md
├── docs/
│   ├── synopsis.md
│   ├── project-report.md
│   ├── feasibility-study.md
│   ├── oop-concepts.md
│   ├── database-design.md
│   ├── test-cases.md
│   ├── user-manual.md
│   └── viva-questions.md
├── tests/
│   └── README.md
└── screenshots/
    └── README.md
```

---

## 15. Synopsis and Project Report

Prepare `docs/synopsis.md` with:
- Project title
- Student name and enrollment number
- Programme, semester, and institution
- Project guide, if assigned
- Introduction and problem statement
- Objectives
- Proposed system
- Technology used
- Frontend/UI, application logic, and backend/database
- Hardware/software requirements
- Feasibility study
- Expected outcomes
- Conclusion

Use placeholders until personal and institutional details are known. Follow the college's official format if one is provided.

The final report should include, as required by the college:
1. Cover page
2. Certificate, if required
3. Declaration
4. Acknowledgement
5. Preface
6. Index / table of contents
7. Abstract
8. Introduction and problem statement
9. Objectives and scope
10. Existing and proposed system
11. History and features of C++
12. Hardware and software requirements
13. Feasibility study
14. System architecture and module descriptions
15. OOP concepts
16. Database design
17. UI screenshots
18. Implementation details
19. Testing and test results
20. Conclusion and future scope
21. References

Only claim features that are implemented and tested. Never invent certificates, signatures, faculty approvals, screenshots, or test results.

---

## 16. Development Roadmap

### Phase 1 — Confirm and set up
- [ ] Confirm topic and faculty guidelines.
- [ ] Confirm that Qt desktop GUI is acceptable.
- [ ] Check compiler, CMake, Qt Widgets, Qt SQL, MySQL, and the MySQL driver.
- [ ] Initialize Git and create the initial project structure.
- [ ] Build a minimal Qt window.

**Milestone:** The application opens a working window.

### Phase 2 — UI shell and navigation
- [ ] Create the main window and consistent styling.
- [ ] Create the welcome screen.
- [ ] Create role-specific navigation.
- [ ] Create placeholder screens for major modules.
- [ ] Add reusable confirmation and message dialogs.

**Milestone:** Every planned screen can be opened, even if the database is not connected yet.

### Phase 3 — Database foundation
- [ ] Finalize schema and relationships.
- [ ] Add `schema.sql` and optional sample data.
- [ ] Configure database connection outside source code.
- [ ] Test connection and display meaningful errors.
- [ ] Implement repositories with parameterized queries.

**Milestone:** The application can safely read and write a test record.

### Phase 4 — Authentication and profiles
- [ ] Registration UI and validation.
- [ ] Secure password hashing.
- [ ] Sign-in and sign-out.
- [ ] Role-based routing and authorization.
- [ ] Job seeker profile.
- [ ] Employer/company profile.

**Milestone:** Users can sign in and see the correct dashboard.

### Phase 5 — Jobs
- [ ] Post a job.
- [ ] Manage own job listings.
- [ ] Browse/search/filter jobs.
- [ ] View job details.
- [ ] Close a job.

**Milestone:** Employers can manage vacancies and seekers can find them.

### Phase 6 — Applications
- [ ] Apply to a job.
- [ ] Prevent duplicate applications.
- [ ] View My Applications.
- [ ] View applicants for employer-owned jobs.
- [ ] Update application statuses.
- [ ] Verify authorization rules.

**Milestone:** The main seeker-to-employer workflow works end to end.

### Phase 7 — Admin and polish
- [ ] Admin dashboard and statistics.
- [ ] User management.
- [ ] Job moderation.
- [ ] Empty, loading, success, and error states.
- [ ] Consistent spacing, labels, and button styles.
- [ ] Basic accessibility and keyboard navigation.

**Milestone:** All required screens and core functions are usable.

### Phase 8 — Testing and academic submission
- [ ] Run functional tests.
- [ ] Test invalid input and database failures.
- [ ] Fix compiler warnings and bugs.
- [ ] Capture genuine screenshots.
- [ ] Complete synopsis and report.
- [ ] Document OOP concepts and database design.
- [ ] Prepare user manual and viva questions.
- [ ] Verify a clean build from the documented instructions.

---

## 17. Testing Checklist

Create `docs/test-cases.md` and record the actual result of each test.

| Test | Expected result |
|---|---|
| Register with valid data | Account is created |
| Register using an existing email | Clear duplicate-email message |
| Sign in with incorrect password | Access is denied with a helpful message |
| Sign in as a job seeker | Job seeker dashboard opens |
| Sign in as an employer | Employer dashboard opens |
| Search for a matching job | Matching results appear |
| Search with no matches | Dedicated empty state appears |
| Post a valid job | Job is saved and displayed |
| Apply to an open job | Application is saved |
| Apply twice to the same job | Duplicate application is prevented |
| Apply to a closed job | Application is rejected |
| Employer views applicants | Only applicants for their own job are shown |
| Employer attempts to manage another employer's job | Operation is denied |
| Update application status | New status is saved and visible |
| Database is unavailable | Clear error appears; no false success |
| Restart application | Previously saved records remain |
| Admin closes/removes a listing | Listing is no longer available for new applications; history is preserved |

---

## 18. Coding and Security Rules

1. Use readable, beginner-friendly C++.
2. Use clear names for classes, methods, variables, and files.
3. Separate UI, services, repositories, and models.
4. Avoid large functions and duplicated logic.
5. Use parameterized SQL queries.
6. Never store passwords as plain text.
7. Never commit credentials or private user data.
8. Validate data in the service layer, not only in the UI.
9. Enforce role and ownership checks in application logic.
10. Handle database errors without crashing.
11. Do not show a success message before the operation succeeds.
12. Confirm destructive actions.
13. Preserve application history.
14. Compile and test after each meaningful change.
15. Keep documentation aligned with the actual code.
16. Do not add unnecessary dependencies or advanced features before core workflows work.

---

## 19. Git Workflow

Check changes before committing:

```bash
git status
git add README.md src database docs
git commit -m "Add initial job portal project structure"
```

Only stage files that exist and that you intend to commit. Add your real remote URL when a repository has been created:

```bash
git remote add origin YOUR_GITHUB_HTTPS_URL
git branch -M main
git push -u origin main
```

If `origin` already exists, inspect it using `git remote -v` before adding it again.

The `.gitignore` should exclude build outputs, local configuration files, credentials, and temporary files. `.env.example` may document the names of required configuration values, but it must not contain real secrets.

---

## 20. Instructions for Codex

Treat this README as the initial project specification.

### Working agreement

- Read this file before changing code.
- Inspect the repository and existing files first.
- Work in small, verifiable steps instead of building everything at once.
- Explain the purpose of each module in beginner-friendly language.
- Build and test the UI screen by screen.
- Give each main function its own purpose-built screen as described in Section 8.
- Use shared components where sensible, but do not collapse all functions into one generic screen.
- Keep visual styling consistent while making each screen's layout appropriate to its task.
- Do not introduce features outside scope without asking first.
- Do not delete or rewrite working code unnecessarily.
- Do not invent test results or claim unverified functionality.
- Report build errors honestly and help fix them.
- Update README and relevant documentation when decisions change.
- Use placeholders for student details that have not been provided.
- Never put database passwords directly into source code.
- If a requirement is ambiguous, explain the options and recommend the simplest suitable approach.

### Active implementation

The active product is the Python / SQLite application in `app.py` and `web/`.
The earlier Qt files and MySQL schema are retained as reference artifacts for
the original academic proposal. They are not part of the runnable web app.
Keep this distinction clear when updating documentation or preparing a report.

---

## 21. Definition of Done

The project is ready for final review when:
- [ ] The application builds and launches using documented steps.
- [ ] Each main feature has a distinct, appropriate UI.
- [ ] Registration, login, and role routing work.
- [ ] Job seekers can browse and apply for jobs.
- [ ] Employers can post jobs and manage their own applicants.
- [ ] Application statuses persist correctly.
- [ ] Administrator functions enforce authorization.
- [ ] MySQL data persists after the application closes.
- [ ] SQL queries are parameterized.
- [ ] Passwords are not stored in plain text.
- [ ] Test cases have real recorded results.
- [ ] OOP concepts are explained with examples from the code.
- [ ] Synopsis and report match the implemented system.
- [ ] Genuine screenshots and a user manual are included.
- [ ] The student can explain the architecture, database, screens, and limitations.

---

## 22. Future Scope

If time permits and the faculty approves, future improvements may include:
- A graphical resume preview
- More advanced job filters
- Resume upload with safe file handling
- Exporting basic reports
- Email notifications through a properly configured service
- A web or mobile version

These are optional. Complete the core academic requirements first.

---

## 23. Current Project Status

**Status:** Runnable local web application with SQLite backend.

The active implementation supports account roles, authentication, job search,
job publishing and management, job applications, employer applicant decisions,
seeker/company profiles, and basic admin moderation. See the current user manual
and project report for implementation details and limitations. The C++ / Qt /
MySQL artifacts are retained as reference material only.

---

*End of README*

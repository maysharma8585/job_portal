# User Manual

## Start the application

Requirements: Python 3.10 or later. The running web version uses only the Python
standard library; no `pip install` step is needed.

```bash
python3 app.py
```

Open <http://127.0.0.1:8000>. Set `JOB_PORTAL_HOST` or `JOB_PORTAL_PORT` to
change the bind address. SQLite data is stored in `data/job_portal.sqlite3` by
default. Set `JOB_PORTAL_DB_PATH` to move it elsewhere. The database and tables
are initialized automatically, with no fabricated users or listings.

Create an administrator in the terminal:

```bash
python3 app.py --create-admin admin@example.com "Portal Administrator"
```

The command prompts for a password. Use at least 10 characters. The active
account is created with a scrypt password hash.

## Job seeker

1. Select **Sign in** and create a job seeker account.
2. Add skills, education, experience, and an optional resume link under **My profile**.
3. Search by keyword, location, job type, or category under **Find jobs**.
4. Open a listing and choose **Apply for this role**. Duplicate applications are rejected.
5. Track status or withdraw a pending/shortlisted application under **Applications**.

## Employer

1. Create an employer account and supply the company name.
2. Complete the company details under **Company profile**.
3. Publish a vacancy from **Post a job**.
4. View, edit, or close vacancies in **Manage jobs**.
5. Open **Applicants** for a vacancy to view candidate details and update a decision.

## Administrator

Sign in with an administrator account. Use **Manage users** to activate or
deactivate accounts and **Moderate jobs** to open, close, or remove listings.
Removed jobs are not shown publicly, and their application history remains.

## Data and limitations

The database is local SQLite. Back up the `.sqlite3` file while the application
is stopped. This is a single-machine academic app, not a production hosting
service. Resume uploads, email delivery, password recovery, and multi-admin
audit logs are not included. Use HTTPS and enable `JOB_PORTAL_SECURE_COOKIE=1`
if deploying behind a trusted TLS proxy.

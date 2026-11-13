# Database notes

The active app uses SQLite. It initializes its schema automatically at startup
and stores data in `data/job_portal.sqlite3` (or `JOB_PORTAL_DB_PATH`). No MySQL
server, package installation, or manual import is needed for the runnable
version.

`schema.sql` is retained as the MySQL schema design from the original C++/Qt
proposal. It is not used by `app.py` and should not be imported for the active
SQLite application.

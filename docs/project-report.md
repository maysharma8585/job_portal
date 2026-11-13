# Project Report (working draft)

Personal and institutional details remain placeholders until supplied. This
report describes the active Python/SQLite web implementation. The earlier
C++/Qt/MySQL proposal remains in the README as a design reference.

## Abstract

The Job Portal Management System is a local web application for job seekers,
employers, and administrators. Job seekers can search vacancies, maintain a
professional profile, apply, and track outcomes. Employers can publish and
manage jobs and review applicants. Administrators can manage account access and
moderate listings. The app uses a Python HTTP backend, a responsive
HTML/CSS/JavaScript interface, and SQLite persistence.

## Architecture

`app.py` serves the frontend, validates API input, authenticates users, applies
role and ownership checks, hashes passwords with scrypt, and reads/writes the
SQLite database. `web/index.html`, `web/styles.css`, and `web/app.js` implement
the interface and call the same-origin JSON API. Tables are initialized at
startup and include users, profiles, companies, jobs, applications, and
sessions.

## Data relationships

Each seeker has one profile and each employer owns one company profile.
Companies own job listings. Applications reference one seeker and one job, with
a unique constraint preventing duplicate applications. Job status changes
preserve linked applications.

## Object-oriented and design concepts

The active backend is procedural Python organized around the request handler
and helper functions rather than a C++ class hierarchy. The original Qt/C++
proposal's OOP examples should not be represented as implemented code. Relevant
design concepts in the active code include encapsulated request handling,
abstraction through API operations, and relational constraints for integrity.

## Security and limitations

Passwords are stored as salted scrypt hashes; sessions use random tokens whose
SHA-256 hashes are stored in SQLite and delivered in HttpOnly, SameSite cookies.
The application enforces role and employer ownership checks in the backend,
parameterizes SQL statements, escapes dynamic text in the browser, and applies
content security headers. This remains an academic local application, not a
production service. HTTPS termination, backups, rate limiting, audit logs,
email verification, password recovery, and resume file storage are outside the
current scope.

## Testing

Record only tests actually run in `docs/test-cases.md`. Add genuine screenshots
and test outcomes before producing a final academic submission.

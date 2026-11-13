# Project Synopsis: Job Portal Management System

**Student:** [Student name]  
**Enrollment number:** [Enrollment number]  
**Programme / semester:** [Programme and semester]  
**Institution:** [Institution]  
**Project guide:** [Guide, if assigned]

## Introduction

The Job Portal Management System provides a shared workspace where job seekers
can discover vacancies and follow their applications while employers publish
jobs and review candidates. Administrators can manage account access and
moderate listings.

## Objectives

- Provide separate seeker, employer, and administrator workflows.
- Store accounts, profiles, jobs, and applications in a relational database.
- Enforce login, role permissions, and duplicate-application rules.
- Present a responsive and understandable interface for common recruitment tasks.

## Proposed and implemented system

The current runnable implementation is a browser application served by Python's
standard HTTP server. It includes registration and login, job browsing and
filtering, seeker profiles and applications, employer company/job/applicant
management, and administrator account/listing controls. SQLite provides local
persistent storage. No sample accounts or fabricated vacancies are seeded.

## Technology

- Frontend: HTML, CSS, and vanilla JavaScript
- Backend: Python 3 standard library HTTP server
- Database: SQLite 3
- Password storage: salted scrypt hashes

## Feasibility and limitations

The system runs locally without third-party Python packages. It is intended for
an academic demonstration on one machine. It does not provide resume uploads,
email delivery, password recovery, or production hosting controls. The original
proposal specified C++ / Qt / MySQL; the implementation stack was changed so a
working version could run in the available environment.

## Expected outcome

Users can complete the main job seeking and hiring workflows while role checks
and relational constraints protect private records and preserve application
history.

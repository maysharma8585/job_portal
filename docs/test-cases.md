# Functional test checklist

Use a temporary database (`JOB_PORTAL_DB_PATH=/tmp/portal-test.sqlite3`) when
checking workflows. Record date and actual result before submitting this table.

| Test | Expected result | Result |
|---|---|---|
| Register seeker and employer accounts | Each role gets its own workspace | Not recorded |
| Register duplicate email | Friendly conflict; no second account | Not recorded |
| Login with wrong password | Access denied | Not recorded |
| Search by keyword and location | Only matching open jobs appear | Not recorded |
| Apply twice to one job | Second application is rejected | Not recorded |
| Apply after deadline or job close | Application is rejected | Not recorded |
| Employer reviews applicant for own job | Candidate details and status controls appear | Not recorded |
| Employer requests another employer's applicants | Access denied | Not recorded |
| Admin closes/removes job | Public listing changes; application history remains | Not recorded |
| Restart the app | SQLite records remain available | Not recorded |

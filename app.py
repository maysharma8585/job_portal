#!/usr/bin/env python3
"""Northstar Job Portal: dependency-light HTTP application and SQLite backend."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import sys
import time
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"


def load_local_env() -> None:
    """Read simple KEY=VALUE settings without overriding the process environment."""
    env_file = ROOT / ".env"
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip("\"'")
        if key and key.replace("_", "").isalnum():
            os.environ.setdefault(key, value)


load_local_env()
DB_PATH = Path(os.environ.get("JOB_PORTAL_DB_PATH", ROOT / "data" / "job_portal.sqlite3"))
SESSION_TTL = 60 * 60 * 12
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
ROLES = {"job_seeker", "employer", "admin"}
STATUSES = {"Pending", "Shortlisted", "Rejected", "Hired", "Withdrawn"}
EMPLOYMENT_TYPES = {"Full-time", "Part-time", "Contract", "Internship", "Temporary"}


class PortalConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc, tb):
        try:
            return super().__exit__(exc_type, exc, tb)
        finally:
            self.close()


def connect_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=10, factory=PortalConnection)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA journal_mode = WAL")
    return db


def initialize_db() -> None:
    with connect_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL CHECK(length(name) BETWEEN 2 AND 120),
          email TEXT NOT NULL COLLATE NOCASE UNIQUE,
          password_hash TEXT NOT NULL,
          role TEXT NOT NULL CHECK(role IN ('job_seeker','employer','admin')),
          active INTEGER NOT NULL DEFAULT 1,
          created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS profiles (
          user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
          phone TEXT NOT NULL DEFAULT '', skills TEXT NOT NULL DEFAULT '',
          education TEXT NOT NULL DEFAULT '', experience TEXT NOT NULL DEFAULT '',
          resume_url TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS companies (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          owner_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE RESTRICT,
          name TEXT NOT NULL, industry TEXT NOT NULL DEFAULT '', location TEXT NOT NULL DEFAULT '',
          website TEXT NOT NULL DEFAULT '', description TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS jobs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
          title TEXT NOT NULL, category TEXT NOT NULL, description TEXT NOT NULL,
          requirements TEXT NOT NULL DEFAULT '', location TEXT NOT NULL,
          employment_type TEXT NOT NULL, salary_min REAL, salary_max REAL, deadline TEXT,
          status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','closed','removed')),
          created_at TEXT NOT NULL DEFAULT (datetime('now')),
          updated_at TEXT NOT NULL DEFAULT (datetime('now')),
          CHECK(salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max)
        );
        CREATE INDEX IF NOT EXISTS idx_jobs_public ON jobs(status, created_at DESC);
        CREATE TABLE IF NOT EXISTS applications (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE RESTRICT,
          seeker_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
          cover_letter TEXT NOT NULL DEFAULT '',
          status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending','Shortlisted','Rejected','Hired','Withdrawn')),
          applied_at TEXT NOT NULL DEFAULT (datetime('now')),
          updated_at TEXT NOT NULL DEFAULT (datetime('now')),
          UNIQUE(job_id, seeker_id)
        );
        CREATE INDEX IF NOT EXISTS idx_apps_seeker ON applications(seeker_id, applied_at DESC);
        CREATE INDEX IF NOT EXISTS idx_apps_job ON applications(job_id, applied_at DESC);
        CREATE TABLE IF NOT EXISTS sessions (
          token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          expires_at INTEGER NOT NULL
        );
        """)
        db.execute("DELETE FROM sessions WHERE expires_at < ?", (int(time.time()),))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return f"scrypt$16384$8$1${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt_hex, digest_hex = encoded.split("$")
        if algorithm != "scrypt":
            return False
        actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex),
                                n=int(n), r=int(r), p=int(p), dklen=len(bytes.fromhex(digest_hex)))
        return hmac.compare_digest(actual.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def clean_text(value, name: str, *, required=False, maximum=5000) -> str:
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise ValueError(f"{name} must be text.")
    value = value.strip()
    if required and not value:
        raise ValueError(f"{name} is required.")
    if len(value) > maximum:
        raise ValueError(f"{name} must be {maximum} characters or fewer.")
    return value


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status, self.message = status, message


class PortalHandler(BaseHTTPRequestHandler):
    server_version = "NorthstarPortal/1.0"

    def log_message(self, fmt, *args):
        sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, status, body=None, content_type="application/json; charset=utf-8", headers=None):
        payload = body if isinstance(body, bytes) else json.dumps(body or {}).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(payload)

    def _json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000:
            raise ApiError(413, "Request is too large.")
        try:
            value = json.loads(self.rfile.read(length) or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ApiError(400, "Request body must be valid JSON.")
        if not isinstance(value, dict):
            raise ApiError(400, "Request body must be an object.")
        return value

    def _cookie_token(self):
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        return cookie["portal_session"].value if "portal_session" in cookie else ""

    def _user(self, required=True):
        token = self._cookie_token()
        if token:
            digest = hashlib.sha256(token.encode()).hexdigest()
            with connect_db() as db:
                row = db.execute("""SELECT u.id,u.name,u.email,u.role,u.active FROM sessions s
                    JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires_at>?""",
                                 (digest, int(time.time()))).fetchone()
            if row and row["active"]:
                return dict(row)
        if required:
            raise ApiError(401, "Please sign in to continue.")
        return None

    @staticmethod
    def _require_role(user, *roles):
        if user["role"] not in roles:
            raise ApiError(403, "Your account does not have permission to do that.")

    def _ok(self, data=None, status=200, headers=None):
        self._send(status, data or {}, headers=headers)

    def do_GET(self):
        try:
            path = urlparse(self.path).path
            if path.startswith("/api/"):
                return self._api_get(path)
            relative = "index.html" if path == "/" else path.lstrip("/")
            target = (WEB / relative).resolve()
            if WEB.resolve() not in target.parents and target != WEB.resolve():
                raise ApiError(404, "Not found.")
            if not target.is_file():
                raise ApiError(404, "Not found.")
            mime = "text/html; charset=utf-8" if target.suffix == ".html" else "text/css; charset=utf-8" if target.suffix == ".css" else "text/javascript; charset=utf-8" if target.suffix == ".js" else "application/octet-stream"
            self._send(200, target.read_bytes(), mime, {"Cache-Control": "no-cache"})
        except ApiError as error:
            self._send(error.status, {"error": error.message})
        except Exception:
            self._send(500, {"error": "The server could not complete that request."})

    def do_POST(self):
        self._dispatch_mutation()

    def do_PUT(self):
        self._dispatch_mutation()

    def do_PATCH(self):
        self._dispatch_mutation()

    def _dispatch_mutation(self):
        try:
            path = urlparse(self.path).path
            body = self._json()
            if path.startswith("/api/"):
                return self._api_mutation(path, body)
            raise ApiError(404, "Not found.")
        except ApiError as error:
            self._send(error.status, {"error": error.message})
        except sqlite3.IntegrityError as error:
            message = "That record conflicts with an existing record or linked history."
            if "UNIQUE constraint failed: applications" in str(error):
                message = "You have already applied for this job."
            self._send(409, {"error": message})
        except Exception:
            self._send(500, {"error": "The server could not complete that request."})

    def do_DELETE(self):
        self._dispatch_mutation()

    def _api_get(self, path):
        query = parse_qs(urlparse(self.path).query)
        user = self._user(required=False)
        with connect_db() as db:
            if path == "/api/me":
                if not user:
                    return self._ok({"user": None})
                result = {"user": user}
                if user["role"] == "job_seeker":
                    result["profile"] = dict(db.execute("SELECT * FROM profiles WHERE user_id=?", (user["id"],)).fetchone() or {})
                if user["role"] == "employer":
                    result["company"] = dict(db.execute("SELECT * FROM companies WHERE owner_id=?", (user["id"],)).fetchone() or {})
                return self._ok(result)
            if path == "/api/jobs":
                sql = """SELECT j.id,j.title,j.category,j.description,j.requirements,j.location,
                    j.employment_type,j.salary_min,j.salary_max,j.deadline,j.status,j.created_at,
                    c.name AS company,c.location AS company_location,c.id AS company_id
                    FROM jobs j JOIN companies c ON c.id=j.company_id WHERE j.status='open'"""
                params = []
                for key, column in (("q", "j.title || ' ' || j.category || ' ' || j.description || ' ' || c.name"),
                                    ("location", "j.location"), ("type", "j.employment_type"), ("category", "j.category")):
                    value = query.get(key, [""])[0].strip()
                    if value:
                        sql += f" AND {column} LIKE ?"
                        params.append(f"%{value}%")
                sql += " ORDER BY j.created_at DESC"
                return self._ok({"jobs": [dict(row) for row in db.execute(sql, params)]})
            if path.startswith("/api/jobs/"):
                job_id = self._id_from_path(path, 2)
                row = db.execute("""SELECT j.*,c.name AS company,c.location AS company_location,
                    c.website AS company_website FROM jobs j JOIN companies c ON c.id=j.company_id
                    WHERE j.id=? AND j.status!='removed'""", (job_id,)).fetchone()
                if not row:
                    raise ApiError(404, "Job not found.")
                return self._ok({"job": dict(row)})
            if path == "/api/applications":
                seeker = self._user()
                self._require_role(seeker, "job_seeker")
                rows = db.execute("""SELECT a.*,j.title,j.location,j.employment_type,c.name AS company
                    FROM applications a JOIN jobs j ON j.id=a.job_id JOIN companies c ON c.id=j.company_id
                    WHERE a.seeker_id=? ORDER BY a.applied_at DESC""", (seeker["id"],)).fetchall()
                return self._ok({"applications": [dict(row) for row in rows]})
            if path == "/api/employer/jobs":
                employer = self._user()
                self._require_role(employer, "employer")
                rows = db.execute("""SELECT j.*, (SELECT count(*) FROM applications a WHERE a.job_id=j.id) AS applicant_count
                    FROM jobs j JOIN companies c ON c.id=j.company_id WHERE c.owner_id=? ORDER BY j.created_at DESC""", (employer["id"],)).fetchall()
                return self._ok({"jobs": [dict(row) for row in rows]})
            if path.startswith("/api/employer/jobs/") and path.endswith("/applications"):
                employer = self._user()
                self._require_role(employer, "employer")
                job_id = self._id_from_path(path, 3)
                self._owned_job(db, employer["id"], job_id)
                rows = db.execute("""SELECT a.*,u.name AS applicant_name,u.email,p.phone,p.skills,p.education,p.experience
                    FROM applications a JOIN users u ON u.id=a.seeker_id
                    LEFT JOIN profiles p ON p.user_id=u.id WHERE a.job_id=? ORDER BY a.applied_at DESC""", (job_id,)).fetchall()
                return self._ok({"applications": [dict(row) for row in rows]})
            if path == "/api/admin/overview":
                admin = self._user()
                self._require_role(admin, "admin")
                counts = {key: db.execute(sql).fetchone()[0] for key, sql in {
                    "users": "SELECT count(*) FROM users", "seekers": "SELECT count(*) FROM users WHERE role='job_seeker'",
                    "employers": "SELECT count(*) FROM users WHERE role='employer'", "open_jobs": "SELECT count(*) FROM jobs WHERE status='open'",
                    "applications": "SELECT count(*) FROM applications"}.items()}
                return self._ok({"stats": counts})
            if path == "/api/admin/users":
                admin = self._user()
                self._require_role(admin, "admin")
                return self._ok({"users": [dict(row) for row in db.execute("SELECT id,name,email,role,active,created_at FROM users ORDER BY created_at DESC")]})
            if path == "/api/admin/jobs":
                admin = self._user()
                self._require_role(admin, "admin")
                rows = db.execute("SELECT j.id,j.title,j.location,j.status,j.created_at,c.name AS company FROM jobs j JOIN companies c ON c.id=j.company_id ORDER BY j.created_at DESC")
                return self._ok({"jobs": [dict(row) for row in rows]})
        raise ApiError(404, "Not found.")

    def _api_mutation(self, path, body):
        method = self.command
        if path == "/api/register" and method == "POST":
            name = clean_text(body.get("name"), "Name", required=True, maximum=120)
            email = clean_text(body.get("email"), "Email", required=True, maximum=254).lower()
            password = body.get("password", "")
            role = body.get("role")
            if not EMAIL_RE.match(email):
                raise ApiError(400, "Enter a valid email address.")
            if not isinstance(password, str) or len(password) < 10 or len(password) > 200:
                raise ApiError(400, "Password must be between 10 and 200 characters.")
            if role not in {"job_seeker", "employer"}:
                raise ApiError(400, "Choose job seeker or employer account.")
            company = clean_text(body.get("company"), "Company name", required=True, maximum=160) if role == "employer" else ""
            with connect_db() as db:
                cursor = db.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)", (name,email,hash_password(password),role))
                uid = cursor.lastrowid
                if role == "employer":
                    db.execute("INSERT INTO companies(owner_id,name) VALUES(?,?)", (uid,company))
                else:
                    db.execute("INSERT INTO profiles(user_id) VALUES(?)", (uid,))
                token, cookie = self._new_session(db, uid)
            return self._ok({"user": {"id":uid,"name":name,"email":email,"role":role}}, 201, {"Set-Cookie":cookie})
        if path == "/api/login" and method == "POST":
            email = clean_text(body.get("email"), "Email", required=True, maximum=254).lower()
            password = body.get("password", "")
            with connect_db() as db:
                row = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
                if not row or not row["active"] or not verify_password(str(password), row["password_hash"]):
                    raise ApiError(401, "Email or password is incorrect.")
                _, cookie = self._new_session(db, row["id"])
            return self._ok({"user": {"id":row["id"],"name":row["name"],"email":row["email"],"role":row["role"]}}, headers={"Set-Cookie":cookie})
        if path == "/api/logout" and method == "POST":
            token = self._cookie_token()
            if token:
                with connect_db() as db:
                    db.execute("DELETE FROM sessions WHERE token_hash=?", (hashlib.sha256(token.encode()).hexdigest(),))
            return self._ok({"ok":True}, headers={"Set-Cookie":"portal_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0"})

        user = self._user()
        with connect_db() as db:
            if path == "/api/profile" and method in ("PUT", "PATCH"):
                self._require_role(user, "job_seeker")
                values = [clean_text(body.get(key), label, maximum=limit) for key,label,limit in (
                    ("phone","Phone",32),("skills","Skills",3000),("education","Education",3000),
                    ("experience","Experience",5000),("resume_url","Resume link",500))]
                if values[4] and not (values[4].startswith("https://") or values[4].startswith("http://")):
                    raise ApiError(400, "Resume link must start with http:// or https://.")
                db.execute("UPDATE profiles SET phone=?,skills=?,education=?,experience=?,resume_url=?,updated_at=datetime('now') WHERE user_id=?", (*values,user["id"]))
                return self._ok({"ok":True})
            if path == "/api/company" and method in ("PUT", "PATCH"):
                self._require_role(user,"employer")
                name=clean_text(body.get("name"),"Company name",required=True,maximum=160)
                industry=clean_text(body.get("industry"),"Industry",maximum=120)
                location=clean_text(body.get("location"),"Location",maximum=160)
                website=clean_text(body.get("website"),"Website",maximum=300)
                description=clean_text(body.get("description"),"Description",maximum=3000)
                if website and not (website.startswith("https://") or website.startswith("http://")):
                    raise ApiError(400,"Website must start with http:// or https://.")
                db.execute("UPDATE companies SET name=?,industry=?,location=?,website=?,description=? WHERE owner_id=?", (name,industry,location,website,description,user["id"]))
                return self._ok({"ok":True})
            if path == "/api/applications" and method == "POST":
                self._require_role(user,"job_seeker")
                try: job_id=int(body.get("job_id"))
                except (TypeError,ValueError): raise ApiError(400,"Choose a valid job.")
                letter=clean_text(body.get("cover_letter"),"Cover letter",maximum=3000)
                cur=db.execute("""INSERT INTO applications(job_id,seeker_id,cover_letter)
                    SELECT id,?,? FROM jobs WHERE id=? AND status='open'
                    AND (deadline IS NULL OR deadline>=date('now'))""",(user["id"],letter,job_id))
                if not cur.rowcount: raise ApiError(400,"This job is no longer accepting applications.")
                return self._ok({"ok":True},201)
            if path.startswith("/api/applications/") and method == "PATCH":
                self._require_role(user,"job_seeker")
                app_id=self._id_from_path(path,2)
                cur=db.execute("UPDATE applications SET status='Withdrawn',updated_at=datetime('now') WHERE id=? AND seeker_id=? AND status IN ('Pending','Shortlisted')",(app_id,user["id"]))
                if not cur.rowcount: raise ApiError(400,"This application can no longer be withdrawn.")
                return self._ok({"ok":True})
            if path == "/api/employer/jobs" and method == "POST":
                self._require_role(user,"employer")
                values=self._job_values(body)
                company=db.execute("SELECT id FROM companies WHERE owner_id=?",(user["id"],)).fetchone()
                cur=db.execute("""INSERT INTO jobs(company_id,title,category,description,requirements,location,
                    employment_type,salary_min,salary_max,deadline) VALUES(?,?,?,?,?,?,?,?,?,?)""",(company["id"],*values))
                return self._ok({"id":cur.lastrowid},201)
            if path.startswith("/api/employer/jobs/"):
                self._require_role(user,"employer")
                job_id=self._id_from_path(path,3)
                self._owned_job(db,user["id"],job_id)
                if path.endswith("/status") and method == "PATCH":
                    status=body.get("status")
                    if status not in {"open","closed"}: raise ApiError(400,"Choose open or closed status.")
                    cur=db.execute("UPDATE jobs SET status=?,updated_at=datetime('now') WHERE id=? AND status!='removed'",(status,job_id))
                    if not cur.rowcount: raise ApiError(400,"A listing removed by an administrator cannot be reopened.")
                    return self._ok({"ok":True})
                if method in ("PUT","PATCH"):
                    removed=db.execute("SELECT status FROM jobs WHERE id=?",(job_id,)).fetchone()
                    if removed and removed["status"]=="removed": raise ApiError(400,"A listing removed by an administrator cannot be edited.")
                    values=self._job_values(body)
                    db.execute("""UPDATE jobs SET title=?,category=?,description=?,requirements=?,location=?,
                      employment_type=?,salary_min=?,salary_max=?,deadline=?,updated_at=datetime('now') WHERE id=?""",(*values,job_id))
                    return self._ok({"ok":True})
            if path.startswith("/api/employer/applications/") and path.endswith("/status") and method == "PATCH":
                self._require_role(user,"employer")
                app_id=self._id_from_path(path,3)
                status=body.get("status")
                if status not in {"Shortlisted","Rejected","Hired"}: raise ApiError(400,"Choose a valid applicant status.")
                owns=db.execute("""SELECT a.id FROM applications a JOIN jobs j ON j.id=a.job_id
                    JOIN companies c ON c.id=j.company_id WHERE a.id=? AND c.owner_id=?""",(app_id,user["id"])).fetchone()
                if not owns: raise ApiError(404,"Application not found for your company.")
                db.execute("UPDATE applications SET status=?,updated_at=datetime('now') WHERE id=?",(status,app_id))
                return self._ok({"ok":True})
            if path.startswith("/api/admin/users/") and path.endswith("/active") and method == "PATCH":
                self._require_role(user,"admin")
                target_id=self._id_from_path(path,3)
                active=body.get("active")
                if not isinstance(active,bool): raise ApiError(400,"Active must be true or false.")
                if target_id==user["id"] and not active: raise ApiError(400,"You cannot deactivate your own account.")
                cur=db.execute("UPDATE users SET active=? WHERE id=?",(int(active),target_id))
                if not cur.rowcount: raise ApiError(404,"User not found.")
                return self._ok({"ok":True})
            if path.startswith("/api/admin/jobs/") and path.endswith("/status") and method == "PATCH":
                self._require_role(user,"admin")
                job_id=self._id_from_path(path,3)
                status=body.get("status")
                if status not in {"open","closed","removed"}: raise ApiError(400,"Choose a valid listing status.")
                cur=db.execute("UPDATE jobs SET status=?,updated_at=datetime('now') WHERE id=?",(status,job_id))
                if not cur.rowcount: raise ApiError(404,"Job not found.")
                return self._ok({"ok":True})
        raise ApiError(404,"Not found.")

    def _new_session(self, db, user_id):
        token=secrets.token_urlsafe(32)
        db.execute("INSERT INTO sessions(token_hash,user_id,expires_at) VALUES(?,?,?)",(hashlib.sha256(token.encode()).hexdigest(),user_id,int(time.time())+SESSION_TTL))
        cookie=f"portal_session={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={SESSION_TTL}"
        if os.environ.get("JOB_PORTAL_SECURE_COOKIE")=="1": cookie += "; Secure"
        return token,cookie

    @staticmethod
    def _id_from_path(path, segment):
        parts=path.strip("/").split("/")
        try: return int(parts[segment])
        except (IndexError,ValueError): raise ApiError(404,"Not found.")

    @staticmethod
    def _owned_job(db, owner_id, job_id):
        row=db.execute("SELECT j.id FROM jobs j JOIN companies c ON c.id=j.company_id WHERE j.id=? AND c.owner_id=?",(job_id,owner_id)).fetchone()
        if not row: raise ApiError(404,"Job not found for your company.")

    @staticmethod
    def _job_values(body):
        title=clean_text(body.get("title"),"Job title",required=True,maximum=180)
        category=clean_text(body.get("category"),"Category",required=True,maximum=120)
        description=clean_text(body.get("description"),"Description",required=True,maximum=10000)
        requirements=clean_text(body.get("requirements"),"Requirements",maximum=5000)
        location=clean_text(body.get("location"),"Location",required=True,maximum=160)
        kind=body.get("employment_type")
        if kind not in EMPLOYMENT_TYPES: raise ApiError(400,"Choose a valid employment type.")
        def amount(key):
            raw=body.get(key)
            if raw in (None,""): return None
            try: value=float(raw)
            except (TypeError,ValueError): raise ApiError(400,"Salary must be a number.")
            if value < 0 or value > 1_000_000_000: raise ApiError(400,"Salary is outside the allowed range.")
            return value
        minimum,maximum=amount("salary_min"),amount("salary_max")
        if minimum is not None and maximum is not None and minimum>maximum: raise ApiError(400,"Minimum salary cannot exceed maximum salary.")
        deadline=clean_text(body.get("deadline"),"Deadline",maximum=10) or None
        if deadline and not re.fullmatch(r"\d{4}-\d{2}-\d{2}",deadline): raise ApiError(400,"Deadline must be a valid date.")
        return (title,category,description,requirements,location,kind,minimum,maximum,deadline)


def create_admin(email, name):
    import getpass
    password=getpass.getpass("Admin password (10+ characters): ")
    if len(password)<10: raise SystemExit("Password must contain at least 10 characters.")
    with connect_db() as db:
        db.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,'admin')",(name,email.lower(),hash_password(password)))
    print(f"Administrator account created for {email}.")


def main():
    parser=argparse.ArgumentParser(description="Northstar Job Portal")
    parser.add_argument("--create-admin",nargs=2,metavar=("EMAIL","NAME"),help="create an admin account (prompts for password)")
    parser.add_argument("--host",default=os.environ.get("JOB_PORTAL_HOST","127.0.0.1"))
    parser.add_argument("--port",type=int,default=int(os.environ.get("JOB_PORTAL_PORT","8000")))
    args=parser.parse_args()
    initialize_db()
    if args.create_admin:
        email,name=args.create_admin
        if not EMAIL_RE.match(email): raise SystemExit("Enter a valid email address.")
        create_admin(email,name)
        return
    server=ThreadingHTTPServer((args.host,args.port),PortalHandler)
    print(f"Northstar Job Portal running at http://{args.host}:{args.port}")
    print(f"Database: {DB_PATH}")
    try: server.serve_forever()
    except KeyboardInterrupt: print("\nPortal stopped.")
    finally: server.server_close()


if __name__ == "__main__":
    main()

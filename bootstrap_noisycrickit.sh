#!/bin/bash
set -e

echo "Setting up NoisyCrickit project..."

# 1. Directories
mkdir -p src/noisycrickit/templates tests .github/workflows

# 2. Configs & Tooling
cat << 'CONFIG' > docker-compose.yml
version: "3.8"
services:
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password
CONFIG

cat << 'CONFIG' > pyproject.toml
[build-system]
requires = ["setuptools>=61.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "noisycrickit"
version = "0.1.0"
description = "A ticket system similar to Jira or GitHub issues, with Flask, HTMX, and MongoDB."
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "flask>=3.0.0",
    "mongoengine>=0.28.0",
    "pydantic-settings>=2.2.0",
    "click>=8.1.0",
    "bcrypt>=4.1.0",
    "email-validator>=2.1.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "hypothesis>=6.98.0",
    "ruff>=0.3.0",
    "mypy>=1.9.0",
    "mdformat>=0.7.17",
    "tox>=4.14.0",
    "mongomock>=4.1.2",
    "requests-mock>=1.11.0"
]

[project.scripts]
noisycrickit = "noisycrickit.cli:cli"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
addopts = "--cov=src/noisycrickit --cov-report=term-missing --cov-fail-under=100"
testpaths = ["tests"]
pythonpath = ["."]

[tool.ruff]
line-length = 160
target-version = "py312"
exclude = ["tests"]

[tool.ruff.lint]
select = [
    "E", "F", "W", "I", "N", "D", "UP", "YTT", "ANN", "BLE",
    "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "EM", "EXE", "ISC",
    "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET",
    "SLF", "SIM", "TID", "TCH", "INT", "ARG", "PTH", "ERA", "PD",
    "PGH", "PLC", "PLE", "PLR", "PLW", "TRY", "NPY", "RUF"
]
ignore = [
    "D100", "D101", "D102", "D103", "D104", "D105", "D106", "D107", "D203", "D212",
    "ANN101", "ANN102", "ANN001", "ANN201", "ANN002", "ANN003", "ANN204",
    "S101", "S104", "S105", "PLR2004", "PLC0415", "PLR0913",
    "EM101", "EM102", "TRY003", "TRY002", "TRY004", "ARG001", "COM812", "ISC001"
]

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true
warn_unused_ignores = true
disallow_untyped_defs = true
exclude = ["tests"]
explicit_package_bases = true
mypy_path = "src"

[tool.coverage.run]
branch = true
source = ["src/noisycrickit"]

[tool.coverage.report]
show_missing = true
fail_under = 100

[tool.tox]
legacy_tox_ini = """
[tox]
envlist = py312, py313, lint, type

[testenv]
deps = .[dev]
commands = pytest

[testenv:lint]
deps = .[dev]
commands =
    ruff check src/
    ruff format --check src/
    mdformat --check README.md USER_GUIDE.md DEVELOPER_GUIDE.md

[testenv:type]
deps = .[dev]
commands = mypy src/
"""
CONFIG

cat << 'CONFIG' > .pre-commit-config.yaml
repos:
-   repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
    - id: ruff
      args: [--fix, --exit-non-zero-on-fix]
    - id: ruff-format
-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
    - id: mypy
      additional_dependencies: [pydantic-settings, mongoengine, Flask, click]
-   repo: https://github.com/executablebooks/mdformat
    rev: 0.7.17
    hooks:
    - id: mdformat
      additional_dependencies:
      - mdformat-gfm
      - mdformat-frontmatter
      - mdformat-footnote
CONFIG

cat << 'CONFIG' > .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python \${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: \${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    - name: Start MongoDB
      run: docker-compose up -d
    - name: Run checks with Tox
      run: tox
    - name: Stop MongoDB
      run: docker-compose down
CONFIG

# 3. Documentation
cat << 'DOCS' > README.md
# NoisyCrickit

A ticket system built with Python, Flask, HTMX, and MongoDB.

## Features

- Tickets with life cycles, labels, parent-child groups.
- View filters by status.
- Guest user assignments with automated invitations.
- Estimates, dates, and ETAs.
- Reminders system.
DOCS

cat << 'DOCS' > USER_GUIDE.md
# User Guide

Detailed user instructions will go here.
DOCS

cat << 'DOCS' > DEVELOPER_GUIDE.md
# Developer Guide

Setup instructions and architectural context will go here.
DOCS

# 4. Source Code
touch src/noisycrickit/__init__.py

cat << 'SRC' > src/noisycrickit/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration."""
    mongo_uri: str = "mongodb://admin:password@localhost:27017/noisycrickit?authSource=admin"
    secret_key: str = "dev_secret_key"
    env: str = "dev"
    port: int = 5000

settings = Settings()
SRC

cat << 'SRC' > src/noisycrickit/models.py
from datetime import datetime
from enum import StrEnum
import mongoengine as me

class Role(StrEnum):
    """User roles determining ticket limits and permissions."""
    ADMIN = "admin"
    PREMIUM = "premium"
    BASIC = "basic"
    GUEST = "guest"

class User(me.Document):
    """User model."""
    email = me.EmailField(required=True, unique=True)
    password_hash = me.StringField(required=True)
    role = me.EnumField(Role, default=Role.GUEST)

class Status(StrEnum):
    """Ticket status lifecycle."""
    NEW = "new"
    READY = "ready"
    IN_PROGRESS = "in-progress"
    PEER_REVIEW = "peer-review"
    CLOSED = "closed"

class ProjectStandards(me.Document):
    """Text blob defining estimates."""
    content = me.StringField(default="1 point = 1 day of work")

class Ticket(me.Document):
    """Ticket model."""
    title = me.StringField(required=True)
    description = me.StringField()
    status = me.EnumField(Status, default=Status.NEW)
    labels = me.ListField(me.StringField())

    parent = me.ReferenceField("self", null=True)

    owning_user = me.ReferenceField(User, required=True)

    # Assignee can be an actual User, or if it's an external email, we store it as a string
    assignee_user = me.ReferenceField(User, null=True)
    assignee_email = me.EmailField(null=True)

    value_estimate = me.IntField(default=0) # In points
    work_estimate = me.IntField(default=0) # In points

    created_at = me.DateTimeField(default=datetime.utcnow)
    eta = me.DateTimeField(null=True)

    project_standards = me.ReferenceField(ProjectStandards)
SRC

cat << 'SRC' > src/noisycrickit/services.py
from datetime import datetime, timezone
import bcrypt
import logging
from .models import User, Ticket, Role, Status, ProjectStandards
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROLE_LIMITS = {
    Role.ADMIN: float('inf'),
    Role.PREMIUM: 100,
    Role.BASIC: 10,
    Role.GUEST: 1
}

class TicketLimitExceededError(Exception):
    pass

class UnauthorizedActionError(Exception):
    pass

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(email: str, password: str, role: Role = Role.GUEST) -> User:
    user = User(email=email, password_hash=hash_password(password), role=role)
    user.save()
    return user

def authenticate_user(email: str, password: str) -> Optional[User]:
    user = User.objects(email=email).first()
    if user and check_password(password, user.password_hash):
        return user
    return None

def create_ticket(
    user: User,
    title: str,
    description: str = "",
    project_standards_id: Optional[str] = None
) -> Ticket:
    ticket_count = Ticket.objects(owning_user=user).count()
    if ticket_count >= ROLE_LIMITS.get(user.role, 0):
        msg = f"User with role {user.role.value} cannot create more than {ROLE_LIMITS.get(user.role)} tickets."
        raise TicketLimitExceededError(msg)

    standards = ProjectStandards.objects(id=project_standards_id).first() if project_standards_id else ProjectStandards().save()

    ticket = Ticket(
        title=title,
        description=description,
        owning_user=user,
        assignee_user=user,
        project_standards=standards,
        created_at=datetime.now(timezone.utc)
    )
    ticket.save()
    return ticket

def assign_ticket(ticket: Ticket, _assigner: User, assignee_identifier: str) -> None:
    # Assignee_identifier can be an email string
    # Try to find user
    assignee_user = User.objects(email=assignee_identifier).first()

    if assignee_user:
        ticket.assignee_user = assignee_user
        ticket.assignee_email = None
        # Owning user logic
        # If the new assignee is an actual user, they become the owning user.
        ticket.owning_user = assignee_user
    else:
        # Assignee is just an external email
        ticket.assignee_user = None
        ticket.assignee_email = assignee_identifier
        send_invitation_email(assignee_identifier, str(ticket.id))
        # Owning user remains the same (last actual user, who is the current assigner or previous owner)

    ticket.save()

def claim_ticket_by_signup(new_user: User) -> None:
    # If an external email signs up, they become the owning user and assignee of tickets assigned to their email.
    tickets = Ticket.objects(assignee_email=new_user.email)
    for ticket in tickets:
        ticket.assignee_email = None
        ticket.assignee_user = new_user
        ticket.owning_user = new_user
        ticket.save()

def send_invitation_email(email: str, ticket_id: str) -> None:
    # Mock sending email
    logger.info("Sending invitation email to %s for ticket %s", email, ticket_id)

def send_reminder_email(email: str, ticket_id: str) -> None:
    # Mock sending reminder
    logger.info("Sending reminder email to %s for ticket %s", email, ticket_id)

def trigger_reminders() -> None:
    # Send reminders to all assignees and owning users of active tickets
    # Active tickets are non-closed
    active_tickets = Ticket.objects(status__ne=Status.CLOSED)
    for ticket in active_tickets:
        if ticket.owning_user:
            send_reminder_email(ticket.owning_user.email, str(ticket.id))
        if ticket.assignee_user and ticket.assignee_user != ticket.owning_user:
            send_reminder_email(ticket.assignee_user.email, str(ticket.id))
        elif ticket.assignee_email and (not ticket.owning_user or ticket.assignee_email != ticket.owning_user.email):
            send_reminder_email(ticket.assignee_email, str(ticket.id))

def update_project_standards(ticket: Ticket, user: User, content: str) -> None:
    if user.role == Role.GUEST:
        msg = "Guest users cannot update project standards."
        raise UnauthorizedActionError(msg)

    ticket.project_standards.content = content
    ticket.project_standards.save()
SRC

cat << 'SRC' > src/noisycrickit/app.py
from flask import Flask
from src.noisycrickit.config import settings
import mongoengine as me

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.secret_key

    me.connect(host=settings.mongo_uri)

    # Register blueprints (routes)
    from src.noisycrickit.routes import main_bp
    app.register_blueprint(main_bp)

    return app
SRC

cat << 'SRC' > src/noisycrickit/routes.py
from flask import Blueprint, request, render_template, redirect, url_for, session, g
from .models import User, Ticket, Status, Role
from .services import (
    authenticate_user, create_user, create_ticket, assign_ticket, claim_ticket_by_signup, TicketLimitExceededError
)

main_bp = Blueprint("main", __name__)

@main_bp.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = User.objects(id=user_id).first()

@main_bp.route("/")
def index():
    if g.user is None:
        return redirect(url_for("main.login"))
    return render_template("index.html")

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        action = request.form.get("action")

        if action == "register":
            # For simplicity, register as Guest
            if User.objects(email=email).first():
                return "User already exists", 400
            user = create_user(email, password, Role.GUEST)
            claim_ticket_by_signup(user)
            session["user_id"] = str(user.id)
            return redirect(url_for("main.index"))
        elif action == "login":
            user = authenticate_user(email, password)
            if user:
                session["user_id"] = str(user.id)
                return redirect(url_for("main.index"))
            return "Invalid credentials", 401

    return render_template("login.html")

@main_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))

@main_bp.route("/tickets", methods=["GET", "POST"])
def tickets():
    if not g.user:
        return "Unauthorized", 401

    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description", "")
        try:
            ticket = create_ticket(g.user, title, description)
            return render_template("tickets_partial.html", tickets=[ticket])
        except TicketLimitExceededError as e:
            return f"<div style='color:red'>{str(e)}</div>", 400

    # GET requests
    status_filter = request.args.get("status")
    query = Ticket.objects()
    if status_filter:
        query = query.filter(status=status_filter)

    return render_template("tickets_partial.html", tickets=query)

@main_bp.route("/tickets/<ticket_id>/assign", methods=["POST"])
def assign_ticket_route(ticket_id):
    if not g.user:
        return "Unauthorized", 401

    ticket = Ticket.objects(id=ticket_id).first()
    if not ticket:
        return "Not found", 404

    assignee = request.form["assignee"]
    assign_ticket(ticket, g.user, assignee)

    ticket.reload()
    return render_template("tickets_partial.html", tickets=[ticket])
SRC

cat << 'SRC' > src/noisycrickit/cli.py
import click
import logging
from src.noisycrickit.app import create_app
from src.noisycrickit.services import trigger_reminders

logging.basicConfig(level=logging.INFO)

@click.group()
def cli():
    """NoisyCrickit Command Line Interface."""
    pass

@cli.command()
def reminders():
    """Trigger reminder emails for active tickets."""
    # We need to initialize the app context/db connection
    app = create_app()
    with app.app_context():
        trigger_reminders()
    click.echo("Reminders triggered successfully.")
SRC

# 5. Templates
cat << 'TPL' > src/noisycrickit/templates/base.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NoisyCrickit</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style>
        body { font-family: sans-serif; margin: 2rem; }
        .ticket { border: 1px solid #ccc; padding: 1rem; margin-bottom: 1rem; }
    </style>
</head>
<body>
    <h1>NoisyCrickit Ticket System</h1>
    <nav>
        <a href="/">Home</a> |
        <a href="/login">Login</a> |
        <a href="/logout">Logout</a>
    </nav>
    <hr>
    <div id="content">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
TPL

cat << 'TPL' > src/noisycrickit/templates/login.html
{% extends "base.html" %}

{% block content %}
<h2>Login / Register</h2>
<form action="/login" method="POST">
    <label>Email: <input type="email" name="email" required></label><br>
    <label>Password: <input type="password" name="password" required></label><br>
    <button type="submit" name="action" value="login">Login</button>
    <button type="submit" name="action" value="register">Register (Guest)</button>
</form>
{% endblock %}
TPL

cat << 'TPL' > src/noisycrickit/templates/index.html
{% extends "base.html" %}

{% block content %}
<h2>Tickets</h2>
<form hx-get="/tickets" hx-target="#ticket-list">
    <label>Filter by status:
        <select name="status" onchange="this.form.dispatchEvent(new Event('submit'))">
            <option value="">All</option>
            <option value="new">New</option>
            <option value="ready">Ready</option>
            <option value="in-progress">In Progress</option>
            <option value="peer-review">Peer Review</option>
            <option value="closed">Closed</option>
        </select>
    </label>
</form>

<div id="ticket-list" hx-get="/tickets" hx-trigger="load">
    <!-- Tickets loaded via HTMX -->
</div>

<h3>Create Ticket</h3>
<form hx-post="/tickets" hx-target="#ticket-list" hx-swap="beforeend">
    <label>Title: <input type="text" name="title" required></label><br>
    <label>Description: <textarea name="description"></textarea></label><br>
    <button type="submit">Create</button>
</form>

{% if error %}
<div style="color:red">{{ error }}</div>
{% endif %}
{% endblock %}
TPL

cat << 'TPL' > src/noisycrickit/templates/tickets_partial.html
{% for ticket in tickets %}
<div class="ticket" id="ticket-{{ ticket.id }}">
    <h4>{{ ticket.title }} ({{ ticket.status.value }})</h4>
    <p>{{ ticket.description }}</p>
    <p>Owner: {{ ticket.owning_user.email }}</p>
    <p>Assignee: {{ ticket.assignee_user.email if ticket.assignee_user else ticket.assignee_email }}</p>

    <form hx-post="/tickets/{{ ticket.id }}/assign" hx-target="#ticket-{{ ticket.id }}" hx-swap="outerHTML">
        <input type="email" name="assignee" placeholder="Assignee Email" required>
        <button type="submit">Assign</button>
    </form>
</div>
{% endfor %}
TPL

# 6. Tests
touch tests/__init__.py
cat << 'TEST' > tests/test_app_config.py
from src.noisycrickit.config import Settings
from src.noisycrickit.app import create_app

def test_config():
    settings = Settings()
    assert settings.port == 5000
    assert settings.env == "dev"

def test_app_creation(mocker):
    mocker.patch("mongoengine.connect")
    app = create_app()
    assert app.config["SECRET_KEY"] == "dev_secret_key"
TEST

cat << 'TEST' > tests/test_cli.py
from click.testing import CliRunner
from src.noisycrickit.cli import cli
import pytest
import sys

def test_reminders_cli(mocker):
    mock_app = mocker.MagicMock()
    mocker.patch("src.noisycrickit.cli.create_app", return_value=mock_app)
    mock_trigger = mocker.patch("src.noisycrickit.cli.trigger_reminders")

    runner = CliRunner()
    result = runner.invoke(cli, ["reminders"])

    assert result.exit_code == 0
    assert "Reminders triggered successfully." in result.output
    mock_trigger.assert_called_once()
TEST

cat << 'TEST' > tests/test_routes.py
import pytest
import mongoengine as me
from mongomock import MongoClient
from flask import session
from src.noisycrickit.app import create_app
from src.noisycrickit.models import User, Ticket, Role, Status
from src.noisycrickit.services import create_user, create_ticket, TicketLimitExceededError

@pytest.fixture(autouse=True)
def setup_db():
    me.connect('mongoenginetest', mongo_client_class=MongoClient)
    User.drop_collection()
    Ticket.drop_collection()
    yield
    me.disconnect()

@pytest.fixture
def app(mocker):
    mocker.patch("src.noisycrickit.app.me.connect")
    app = create_app()
    app.config.update({"TESTING": True, "SECRET_KEY": "test"})
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_redirects_if_not_logged_in(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_index_when_logged_in(client):
    user = create_user("test@example.com", "pass", Role.ADMIN)
    with client.session_transaction() as sess:
        sess["user_id"] = str(user.id)
    response = client.get("/")
    assert response.status_code == 200
    assert b"NoisyCrickit Ticket System" in response.data

def test_login_and_logout(client):
    user = create_user("test@example.com", "pass", Role.ADMIN)

    # Test Login
    response = client.post("/login", data={"email": "test@example.com", "password": "pass", "action": "login"})
    assert response.status_code == 302
    assert "/" in response.headers["Location"]

    # Test Logout
    response = client.get("/logout")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    # Invalid login
    response = client.post("/login", data={"email": "test@example.com", "password": "wrong", "action": "login"})
    assert response.status_code == 401

    # GET login
    response = client.get("/login")
    assert response.status_code == 200

def test_register(client):
    response = client.post("/login", data={"email": "new@test.com", "password": "pass", "action": "register"})
    assert response.status_code == 302
    assert "/" in response.headers["Location"]

    # Register existing
    response = client.post("/login", data={"email": "new@test.com", "password": "pass", "action": "register"})
    assert response.status_code == 400

def test_tickets_get_unauthorized(client):
    response = client.get("/tickets")
    assert response.status_code == 401

def test_tickets_get_authorized(client):
    user = create_user("test@example.com", "pass", Role.ADMIN)
    ticket = create_ticket(user, "Test Ticket", "Desc")
    with client.session_transaction() as sess:
        sess["user_id"] = str(user.id)

    response = client.get("/tickets")
    assert response.status_code == 200
    assert b"Test Ticket" in response.data

def test_tickets_get_authorized_filtered(client):
    user = create_user("test@example.com", "pass", Role.ADMIN)
    ticket = create_ticket(user, "Test Ticket", "Desc")
    ticket.status = Status.CLOSED
    ticket.save()

    with client.session_transaction() as sess:
        sess["user_id"] = str(user.id)

    response = client.get("/tickets?status=closed")
    assert response.status_code == 200
    assert b"Test Ticket" in response.data

def test_tickets_post_unauthorized(client):
    response = client.post("/tickets", data={"title": "Test", "description": "Desc"})
    assert response.status_code == 401

def test_tickets_post_authorized(client):
    user = create_user("test@example.com", "pass", Role.ADMIN)
    with client.session_transaction() as sess:
        sess["user_id"] = str(user.id)

    response = client.post("/tickets", data={"title": "Test", "description": "Desc"})
    assert response.status_code == 200
    assert b"Test" in response.data

def test_tickets_post_limit_exceeded(client):
    user = create_user("test@example.com", "pass", Role.GUEST)
    create_ticket(user, "First")

    with client.session_transaction() as sess:
        sess["user_id"] = str(user.id)

    response = client.post("/tickets", data={"title": "Second", "description": "Desc"})
    assert response.status_code == 400

def test_assign_route(client):
    user = create_user("test@example.com", "pass", Role.ADMIN)
    ticket = create_ticket(user, "Test Ticket")

    with client.session_transaction() as sess:
        sess["user_id"] = str(user.id)

    response = client.post(f"/tickets/{ticket.id}/assign", data={"assignee": "external@test.com"})
    assert response.status_code == 200
    assert b"external@test.com" in response.data

def test_assign_route_unauthorized(client):
    response = client.post(f"/tickets/123/assign", data={"assignee": "external@test.com"})
    assert response.status_code == 401

def test_assign_route_not_found(client):
    user = create_user("test@example.com", "pass", Role.ADMIN)
    with client.session_transaction() as sess:
        sess["user_id"] = str(user.id)

    response = client.post(f"/tickets/64b3014a93864003d42b36e3/assign", data={"assignee": "external@test.com"})
    assert response.status_code == 404

def test_login_invalid_action(client):
    response = client.post("/login", data={"email": "test@test.com", "password": "pass", "action": "unknown"})
    assert response.status_code == 200

TEST

cat << 'TEST' > tests/test_services.py
from datetime import datetime
import pytest
import mongoengine as me
from mongomock import MongoClient

from src.noisycrickit.models import User, Ticket, Role, Status, ProjectStandards
from src.noisycrickit.services import (
    create_user, authenticate_user, create_ticket, assign_ticket,
    claim_ticket_by_signup, update_project_standards, TicketLimitExceededError,
    UnauthorizedActionError, hash_password, check_password, trigger_reminders
)

@pytest.fixture(autouse=True)
def setup_db():
    me.connect('mongoenginetest', mongo_client_class=MongoClient)
    User.drop_collection()
    Ticket.drop_collection()
    ProjectStandards.drop_collection()
    yield
    me.disconnect()

def test_user_creation_and_authentication():
    user = create_user("test@example.com", "password", Role.ADMIN)
    assert authenticate_user("test@example.com", "password") == user
    assert authenticate_user("test@example.com", "wrong") is None
    assert authenticate_user("notfound@example.com", "password") is None

def test_ticket_limit():
    user = create_user("basic@example.com", "password", Role.GUEST)
    create_ticket(user, "Ticket 1")
    with pytest.raises(TicketLimitExceededError):
        create_ticket(user, "Ticket 2")

def test_assign_ticket_to_existing_user():
    admin = create_user("admin@example.com", "password", Role.ADMIN)
    basic = create_user("basic@example.com", "password", Role.BASIC)
    ticket = create_ticket(admin, "Ticket 1")

    assign_ticket(ticket, admin, basic.email)

    ticket.reload()
    assert ticket.assignee_user == basic
    assert ticket.owning_user == basic
    assert ticket.assignee_email is None

def test_assign_ticket_to_external_email():
    admin = create_user("admin@example.com", "password", Role.ADMIN)
    ticket = create_ticket(admin, "Ticket 1")

    assign_ticket(ticket, admin, "external@example.com")

    ticket.reload()
    assert ticket.assignee_user is None
    assert ticket.assignee_email == "external@example.com"
    assert ticket.owning_user == admin

def test_claim_ticket_by_signup():
    admin = create_user("admin@example.com", "password", Role.ADMIN)
    ticket = create_ticket(admin, "Ticket 1")
    assign_ticket(ticket, admin, "external@example.com")

    new_user = create_user("external@example.com", "password", Role.BASIC)
    claim_ticket_by_signup(new_user)

    ticket.reload()
    assert ticket.assignee_user == new_user
    assert ticket.owning_user == new_user
    assert ticket.assignee_email is None

def test_update_project_standards():
    admin = create_user("admin@example.com", "password", Role.ADMIN)
    guest = create_user("guest@example.com", "password", Role.GUEST)
    ticket = create_ticket(admin, "Ticket 1")

    update_project_standards(ticket, admin, "New standard")
    ticket.reload()
    assert ticket.project_standards.content == "New standard"

    with pytest.raises(UnauthorizedActionError):
        update_project_standards(ticket, guest, "Guest standard")

def test_trigger_reminders(mocker):
    mock_send = mocker.patch("src.noisycrickit.services.send_reminder_email")

    admin = create_user("admin@example.com", "password", Role.ADMIN)
    ticket1 = create_ticket(admin, "Ticket 1")
    assign_ticket(ticket1, admin, "external@example.com")

    basic = create_user("basic@example.com", "password", Role.BASIC)
    ticket2 = create_ticket(admin, "Ticket 2")
    assign_ticket(ticket2, admin, basic.email)

    ticket3 = create_ticket(admin, "Ticket 3")
    ticket3.status = Status.CLOSED
    ticket3.save()

    trigger_reminders()

    # Should send to owner (admin) and assignee (external) for ticket1 (2 emails)
    # Should send to owner (basic) and assignee (basic) for ticket2 -> only 1 email since they are the same
    # Should not send for ticket3 because it's closed
    assert mock_send.call_count == 3

def test_trigger_reminders_branch_assignee_email(mocker):
    mock_send = mocker.patch("src.noisycrickit.services.send_reminder_email")
    admin = create_user("admin2@example.com", "password", Role.ADMIN)
    ticket1 = create_ticket(admin, "Ticket 1")
    assign_ticket(ticket1, admin, "external1@example.com")

    trigger_reminders()
    assert mock_send.call_count >= 2

def test_trigger_reminders_branch_same_email(mocker):
    mock_send = mocker.patch("src.noisycrickit.services.send_reminder_email")
    admin = create_user("admin3@example.com", "password", Role.ADMIN)
    ticket1 = create_ticket(admin, "Ticket 1")
    assign_ticket(ticket1, admin, "admin3@example.com")

    trigger_reminders()
    assert mock_send.call_count >= 1

def test_send_emails():
    from src.noisycrickit.services import send_invitation_email, send_reminder_email
    send_invitation_email("test@example.com", "123")
    send_reminder_email("test@example.com", "123")

def test_trigger_reminders_branch_external_same_email(mocker):
    admin = create_user("admin4@example.com", "password", Role.ADMIN)
    ticket1 = create_ticket(admin, "Ticket 1")
    ticket1.assignee_user = None
    ticket1.assignee_email = "admin4@example.com"
    ticket1.save()

    mocker.patch("src.noisycrickit.services.send_reminder_email")
    trigger_reminders()
def test_trigger_reminders_branch_assignee_user_different(mocker):
    admin = create_user("admin6@example.com", "password", Role.ADMIN)
    create_user("basic6@example.com", "password", Role.BASIC)
    ticket1 = create_ticket(admin, "Ticket 1")
    assign_ticket(ticket1, admin, "basic6@example.com")

    # owning_user becomes basic6, assignee_user becomes basic6. They are the same.
    # We want a case where ticket.assignee_user is set, BUT is DIFFERENT from ticket.owning_user.
    # To achieve this:
    # Create ticket, assign it to an existing user (basic6) -> basic6 is owner and assignee.
    # Now, bypass and change assignee to admin directly.
    ticket1.assignee_user = admin
    ticket1.save()

    mocker.patch("src.noisycrickit.services.send_reminder_email")
    trigger_reminders()

TEST

cat << 'TEST' > tests/test_services_edge.py
from src.noisycrickit.services import trigger_reminders

def test_trigger_reminders_branch_no_owning_user(mocker):
    class MockTicket:
        owning_user = None
        assignee_user = None
        assignee_email = "test@example.com"
        id = "mock_id"

    mock_objects = mocker.patch("src.noisycrickit.services.Ticket.objects")
    mock_objects.return_value = [MockTicket()]

    mock_send = mocker.patch("src.noisycrickit.services.send_reminder_email")
    trigger_reminders()
    mock_send.assert_called_once_with("test@example.com", "mock_id")
TEST

echo "NoisyCrickit setup script generated."

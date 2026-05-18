# E-Commerce API

A full-featured e-commerce backend built with Django and Django REST Framework. Supports product browsing, shopping cart, Stripe-powered checkout, JWT authentication, and a role-based user system — all containerized with Docker.

---

## Preview

> Click to view demo video

[![E-commerce Demo Video](https://img.youtube.com/vi/D9gyEVefmLU/maxresdefault.jpg)](https://www.youtube.com/watch?v=D9gyEVefmLU)

---

## Features

- **Auth** — Register, login, logout via web UI and REST API; JWT access/refresh tokens with blacklist on logout
- **Roles** — Three user roles: Admin, Seller, Customer
- **Products** — Hierarchical categories, product gallery, discount pricing, inventory tracking, featured products
- **Cart** — Persistent cart per user; add, update, remove items
- **Checkout** — Stripe Checkout Sessions; success/cancel redirect flows; Stripe CLI for local webhook testing
- **Orders** — Full order lifecycle: Pending → Paid → Shipped → Delivered (+ Failed / Refunded)
- **API** — RESTful endpoints with filtering, JWT authentication, and DRF browsable API
- **Admin** — Django admin panel for full data management
- **Docker** — One-command setup with PostgreSQL, Django, and Stripe CLI

---

### 📖 API Documentation
*   **Swagger UI:** `/api/docs/`
*   **Redoc:** `/api/redoc/`

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | Django 6, Django REST Framework |
| Auth | JWT (SimpleJWT) + Django sessions |
| Database | PostgreSQL 16 |
| Payments | Stripe |
| Package manager | uv |
| Server | Gunicorn |
| Containerization | Docker, Docker Compose |
| Linting | Ruff |
| Testing | Pytest, pytest-django |

---

## Project Structure

```
ecommerce_api/
├── apps/
│   ├── users/          # Custom user model, roles, auth views & API
│   ├── products/       # Categories, products, inventory, images
│   ├── cart/           # Cart, orders, payments, Stripe integration
│   └── common/         # Shared storage backend, media serving
├── core/
│   ├── settings.py
│   └── urls.py
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Stripe account](https://dashboard.stripe.com/register) (for payment testing)

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ecommerce-api.git
cd ecommerce-api
```

### 2. Configure environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and update the values (see [Environment Variables](#environment-variables) below).

### 3. Start with Docker

```bash
docker compose up --build
```

This starts three services:
- `db` — PostgreSQL database
- `web` — Django app (runs migrations automatically, then serves on port 8000)
- `stripe-cli` — Stripe webhook listener forwarding to your local app

### 4. Create a superuser

```bash
docker compose exec web uv run python manage.py createsuperuser
```

Visit [http://localhost:8000/admin/](http://localhost:8000/admin/) to access the admin panel.

---

## Running Without Docker

### Prerequisites

- Python 3.12+
- PostgreSQL running locally
- [uv](https://github.com/astral-sh/uv) installed

```bash
# Install dependencies
uv sync

# Apply migrations
uv run python manage.py migrate

# Run dev server
uv run python manage.py runserver
```

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `DB_NAME` | PostgreSQL database name | `ecommerce_db` |
| `DB_USER` | PostgreSQL user | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `yourpassword` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | `pk_test_...` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | `whsec_...` |
| `SITE_URL` | Base URL for Stripe redirect URLs | `http://localhost:8000` |

---

## API Reference

Base URL: `http://localhost:8000/api/v1/`

### Authentication

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| `POST` | `/users/register/` | Create a new account | No |
| `POST` | `/users/login/` | Get access + refresh tokens | No |
| `POST` | `/users/logout/` | Blacklist refresh token | Yes |
| `POST` | `/users/token/refresh/` | Refresh access token | No |
| `GET/PUT` | `/users/profile/` | View or update profile | Yes |
| `POST` | `/users/password/change/` | Change password | Yes |
| `GET` | `/users/list/` | List all users (Admin only) | Yes |

### Products

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| `GET` | `/products/` | List products (filterable) | No |
| `GET` | `/products/<slug>/` | Product detail | No |
| `GET` | `/products/categories/` | List categories | No |
| `GET` | `/products/categories/<slug>/` | Category detail | No |

### Web Routes

| Route | Description |
|---|---|
| `/` | Product listing page |
| `/<slug>/` | Product detail page |
| `/users/register/` | Registration page |
| `/users/login/` | Login page |
| `/users/profile/` | User profile page |
| `/cart/` | Cart page |
| `/cart/checkout/` | Checkout page |
| `/cart/orders/<id>/` | Order detail page |

---

## Testing

```bash
# With uv (local)
uv run pytest

# Inside Docker
docker compose exec web uv run pytest
```

Tests are located in `apps/*/tests.py` and `tests/`.

---

## License

This project is open-source and available under the [MIT License](LICENSE).

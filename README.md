# Revanex Forms

A production-ready custom web form application built with **FastAPI**, **MySQL**, **vanilla HTML/CSS/JS**, **yagmail**, and **Razorpay**.

## Features

- **Form Builder** – Create custom forms with text, email, number, dropdown, checkbox, radio, date, and more field types
- **Shareable Links & Embed** – Generate direct links and iframe embed codes for any form
- **Email Notifications** – Automatic confirmation email to respondents and admin notification via yagmail
- **Razorpay Payments** – Per-form toggle to enable/disable payment collection
- **CSV Export** – One-click export of all submission data as a CSV file
- **Submission Dashboard** – View, search, and manage all form submissions
- **Drag-and-Drop Reordering** – Reorder form fields with drag-and-drop

## Tech Stack

| Layer    | Technology         |
| -------- | ------------------ |
| Frontend | HTML, CSS, JavaScript (vanilla) |
| Backend  | FastAPI (Python)   |
| Database | MySQL              |
| Email    | yagmail (Gmail SMTP) |
| Payments | Razorpay           |

## Project Structure

```
Revanex-Forms/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # SQLAlchemy database setup
│   ├── models.py            # ORM models (Form, Submission)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── routes/
│   │   ├── forms.py         # Form CRUD + CSV export + embed
│   │   ├── submissions.py   # Submission CRUD
│   │   └── payments.py      # Razorpay order + verification
│   └── services/
│       ├── email_service.py  # yagmail email delivery
│       └── payment_service.py # Razorpay API integration
├── static/
│   ├── css/style.css        # Global styles
│   ├── js/
│   │   ├── dashboard.js     # Dashboard page logic
│   │   ├── form-builder.js  # Form builder logic
│   │   ├── submissions.js   # Submissions page logic
│   │   └── public-form.js   # Public form submission logic
│   ├── dashboard.html       # Form list / dashboard
│   ├── create-form.html     # Form builder (create + edit)
│   ├── submissions.html     # View submissions per form
│   └── form.html            # Public-facing form page
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md
```

## Prerequisites

- **Python 3.10+**
- **MySQL 8.0+**
- **Gmail account** (for yagmail email delivery)
- **Razorpay account** (optional, for payments)

## Setup Instructions

### 1. Clone & Navigate

```bash
cd Revanex-Forms
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```ini
# MySQL connection string
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/revanex_forms

# Gmail SMTP (yagmail)
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_NAME=Revanex Forms

# Razorpay (optional — leave blank to disable)
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
```

> **Gmail App Password**: Go to your Google Account → Security → 2-Step Verification → App passwords. Generate one for "Mail". Use that 16-character password here.

### 5. Create MySQL Database

Open MySQL CLI or a GUI tool and run:

```sql
CREATE DATABASE revanex_forms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Tables are created automatically on first startup.

### 6. Run the Application

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000/dashboard.html** in your browser.

## API Endpoints

### Forms

| Method | Endpoint                    | Description              |
| ------ | --------------------------- | ------------------------ |
| GET    | `/api/forms`                | List all forms           |
| POST   | `/api/forms`                | Create a new form        |
| GET    | `/api/forms/{id}`           | Get form details         |
| PUT    | `/api/forms/{id}`           | Update a form            |
| DELETE | `/api/forms/{id}`           | Delete a form            |
| GET    | `/api/forms/{id}/embed`     | Get embed code           |

### Submissions

| Method | Endpoint                                      | Description              |
| ------ | --------------------------------------------- | ------------------------ |
| POST   | `/api/forms/{id}/submit`                      | Submit form data         |
| GET    | `/api/forms/{id}/submissions`                 | List submissions         |
| GET    | `/api/forms/{id}/submissions/export`          | Export as CSV            |
| DELETE | `/api/forms/{id}/submissions/{sid}`           | Delete a submission      |

### Payments

| Method | Endpoint                               | Description              |
| ------ | -------------------------------------- | ------------------------ |
| POST   | `/api/forms/{id}/payment/order`        | Create Razorpay order    |
| POST   | `/api/forms/{id}/payment/verify`       | Verify payment signature |

## Usage Walkthrough

1. **Create a Form** – Go to `/create-form.html`, add fields, configure settings
2. **Enable Payments** – Toggle Razorpay on, enter your API keys, add a field with id/name "Price"
3. **Share** – From the dashboard, click "Share" to get a direct link or embed code
4. **Collect Responses** – Respondents fill and submit the form at the shared link
5. **View Submissions** – Click "View" on any form card to see all submissions
6. **Export** – Click "Export CSV" to download all data

## Razorpay Integration

When Razorpay is enabled for a form:
- The public form page shows a payment section
- Add a field with `id="price"` or label "Price" (type: number) — this determines the payment amount
- The respondent pays via Razorpay checkout before the submission is recorded
- Payment status is stored with each submission record

## Email Notifications

Two types of emails are sent:

1. **Respondent Confirmation** – Sent to the email address the respondent provides in an email-type field
2. **Admin Notification** – Sent to the `notification_email` configured on the form

Both use yagmail with Gmail SMTP. Emails include a styled HTML summary of the submission.

## Database Schema

### `forms`

| Column              | Type          | Description                        |
| ------------------- | ------------- | ---------------------------------- |
| id                  | INT (PK)      | Auto-increment ID                  |
| title               | VARCHAR(255)  | Form title                         |
| description         | TEXT          | Form description                   |
| fields              | JSON          | Array of field definitions         |
| razorpay_enabled    | BOOLEAN       | Payment integration toggle         |
| razorpay_key_id     | VARCHAR(255)  | Razorpay API key ID                |
| razorpay_key_secret | VARCHAR(255)  | Razorpay API secret (encrypted)    |
| notification_email  | VARCHAR(255)  | Admin email for notifications      |
| submit_button_text  | VARCHAR(100)  | Custom submit button label         |
| redirect_url        | VARCHAR(500)  | Post-submission redirect           |
| is_active           | BOOLEAN       | Accepting submissions?             |
| created_at          | DATETIME      | Creation timestamp                 |
| updated_at          | DATETIME      | Last update timestamp              |

### `submissions`

| Column             | Type         | Description                    |
| ------------------ | ------------ | ------------------------------ |
| id                 | INT (PK)     | Auto-increment ID              |
| form_id            | INT (FK)     | References forms.id            |
| data               | JSON         | Submitted field values         |
| respondent_email   | VARCHAR(255) | Respondent's email address     |
| payment_id         | VARCHAR(255) | Razorpay payment ID            |
| payment_status     | VARCHAR(50)  | none / captured / failed       |
| payment_amount     | FLOAT        | Payment amount in rupees       |
| created_at         | DATETIME     | Submission timestamp           |

## Error Handling

- Form submission validation with inline error messages
- Payment failure handling with user-facing error messages
- Email send failures are logged but don't block submission
- API returns appropriate HTTP status codes and error messages
- Frontend shows toast notifications for success/error states

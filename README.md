# M G Fibernet — Three Portal Django Web Application

A Python/Django responsive web application with separate entry URLs for Customer, Employee and Admin. It includes an installable PWA shell for mobile browsers.

## Three portal links (local development)

Run the app, then open:

- **Customer portal:** http://127.0.0.1:8000/customer/
- **Employee portal:** http://127.0.0.1:8000/employee/
- **Admin operations portal:** http://127.0.0.1:8000/admin-portal/
- **Django system administration:** http://127.0.0.1:8000/admin/

These are local development URLs, not public internet links. To share the portals with customers and staff, deploy the project to a server/domain with HTTPS. The same domain can host all three paths, or a reverse proxy can map separate subdomains to the same Django app.

## Implemented workflow

1. A customer signs in and raises one of the nine complaint types. The request can include a description, optional location/address and optional photo.
2. Django creates a ticket number and activity record.
3. In-app notifications are created for active admin/staff users and employee accounts.
4. Employees see tickets in oldest-first order. The first employee to open an unassigned ticket claims it and changes its status to Assigned.
5. On first access, an in-app notification tells the customer which employee accessed the request; administrators also receive a notification. The event is written to the ticket activity history.
6. Employees can update the status and add a note. The customer and admins are notified about the update.
7. Admin operations dashboard can see every ticket, current assignee, status, customer, recent system notifications, and all activity via ticket details. Admin can assign tickets to employees.
8. Plans and callback requests remain available in the customer portal; callback requests notify administrators.

## Setup on Windows / PyCharm

1. Extract the ZIP and open the `mgfibernet_project` folder in PyCharm.
2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Create database tables and an admin user:

   ```powershell
   python manage.py makemigrations portal
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Run the local server:

   ```powershell
   python manage.py runserver
   ```

6. Open the four local URLs above.

## Create employee/customer accounts

Create accounts and profiles from Django Admin. First sign in at `/admin/` using the superuser account. Open **User profiles** and add a profile for each user:

- Employee: `role = Employee`, select a department, and optionally enter a mobile number.
- Customer: `role = Customer`; also create a `CustomerProfile` with a unique customer ID and registered mobile number if you use the OTP demo flow.
- Admin: create a Django user with `is_staff=True` (or a superuser). Admin accounts are treated as administrators and can see all tickets.

The admin portal `/admin-portal/` is restricted to Django staff/superusers. The employee portal is restricted to users whose `UserProfile.role` is `employee`. The customer portal is restricted to users whose profile role is `customer`.

## Important production notes

- Notification delivery in this version is **in-app**. SMS, email, WhatsApp and push notifications need provider credentials and integration. This code does not claim to send SMS messages.
- OTP login is a development demo that prints the OTP in the Django terminal. Do not use this OTP flow in production until a real SMS provider, expiry, rate limiting and abuse protections are configured.
- Before production, set a strong `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, correct `DJANGO_ALLOWED_HOSTS`, configure PostgreSQL, HTTPS, secure cookies, backups, logging and a production web server.
- The default database is SQLite for local development. PostgreSQL is recommended for deployment and concurrent use.
- Employee ticket access and status updates are logged in the ticket activity history. Admin users can view all tickets and their activity. Notification list visibility is per-recipient; the admin dashboard separately shows recent system notifications across recipients.
- Browser geolocation requires user permission and HTTPS in production. This starter accepts a typed location and optional photo; GPS capture can be added to the form if required.
- PWA installation requires a deployed HTTPS origin. The manifest and service worker are included; browser installation UI varies by device/browser.

## Main routes

- `/customer/` — customer dashboard
- `/complaints/new/` — raise request
- `/complaints/` — customer ticket history
- `/plans/` — plans and callback request
- `/employee/` — employee task queue
- `/employee/ticket/<ticket_id>/` — ticket detail, status update and activity
- `/admin-portal/` — admin overview of all tickets and recent notifications
- `/notifications/` — signed-in user's notifications
- `/admin/` — Django administration for users, profiles, plans, tickets and records

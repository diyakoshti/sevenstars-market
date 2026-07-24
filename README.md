# SevenStars Market

A premium role-based e-commerce application built with HTML, CSS, JavaScript,
Python and Django. It includes protected product management, Cloudinary images,
wishlist, cart, Razorpay test checkout, order history and role dashboards.

## Roles

- Admin: manages every product, user role and order; sees sales statistics.
- Sales Person: manages only their own products and sees matching order items.
- User: shops, filters, uses wishlist/cart, pays and views their own orders.

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` and admin at
`http://127.0.0.1:8000/admin/`.

## Environment variables

Copy `.env.example` to `.env` and add Cloudinary and Razorpay test credentials.
Never commit `.env`.

## Deployment

- Render: use `render.yaml`, then configure Cloudinary/Razorpay variables.
- Vercel: follow `vercel_proxy/README.txt` after Render is live.

## Git workflow

Commit each milestone separately. Create a feature branch, push it, open a pull
request, and merge it into `main`.

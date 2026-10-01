# LumiAnsh — Personal Notes

Login details, local run steps aur Vercel deploy guide. Project overview ke liye [README.md](README.md) dekho.

---

## 🔑 Login details (dummy project)

| Kahan | URL | Username | Password |
|---|---|---|---|
| Custom dashboard (local) | http://127.0.0.1:8000/dashboard/login/ | `anshi` | `______` ← yahan likh do |
| Django admin (local) | http://127.0.0.1:8000/admin/ | `anshi` | same as above |
| Live site dashboard (Vercel) | https://YOUR-APP.vercel.app/dashboard/login/ | `______` | `______` |

> Password bhool gaye? `python manage.py changepassword anshi` se naya set kar lo.
>
> ⚠ Repo **public** hai to live site ka password yahan mat likhna (koi bhi login kar lega).
> `DATABASE_URL` aur `DJANGO_SECRET_KEY` kabhi bhi is file mein ya GitHub pe mat daalna.

---

## 💻 Laptop pe run kaise karein (Windows / PowerShell)

### Pehli baar (naye laptop pe ya GitHub se clone karke)

```powershell
git clone https://github.com/AnshikaAgarwall/lumiansh_django_project.git
cd lumiansh_django_project

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

python manage.py migrate            # database tables banata hai
python manage.py seed_data          # sample candles daalta hai (optional)
python manage.py createsuperuser    # admin login banata hai

python manage.py runserver
```

> "running scripts is disabled" error aaye to ek baar chalao:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### Har baar (is laptop pe — venv `E:\django-pro\sms_env` mein hai)

```powershell
cd E:\django-pro\lumiansh_project
..\sms_env\Scripts\Activate.ps1
python manage.py runserver
```

Site: http://127.0.0.1:8000/ · Band karne ke liye `Ctrl + C`

### Tests

```powershell
python manage.py test
```

---

## 🌐 Pages

| Page | URL |
|---|---|
| Home | `/` |
| Shop | `/shop/` |
| Our Customers | `/our-customers/` |
| Buy / Contact | `/buy-now/` |
| Bulk order form | `/bulk-order/` |
| Admin dashboard | `/dashboard/` |
| Django admin | `/admin/` |

---

## 🚀 Vercel pe deploy

Vercel pe `db.sqlite3` kaam nahi karta (wahan files save nahi hoti), isliye live site ke liye
free **Postgres (Neon)** database use hota hai. Laptop pe SQLite hi chalta hai.

### 1. Code GitHub pe push karo

```powershell
git add .
git commit -m "Prepare for Vercel"
git push
```

### 2. Vercel pe project banao

1. https://vercel.com → GitHub se login → **Add New → Project** → `lumiansh_django_project` import karo.
2. Framework Preset: **Other**. Baaki settings default rehne do.

### 3. Database banao

Vercel project → **Storage** tab → **Create Database** → **Neon (Postgres)** → project se connect karo.
Isse `DATABASE_URL` environment variable apne aap add ho jaata hai.

### 4. Environment variables

Vercel project → **Settings → Environment Variables** mein ye add karo:

| Name | Value |
|---|---|
| `DJANGO_SECRET_KEY` | koi lamba random string (neeche command se banao) |
| `DJANGO_DEBUG` | `False` |
| `DATABASE_URL` | step 3 se apne aap aa jaata hai |

Secret key banane ke liye:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Custom domain lagaya ho to `DJANGO_ALLOWED_HOSTS=yourdomain.com` aur
`DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com` bhi add karna.

### 5. Live database mein tables + admin banao (laptop se, ek baar)

Vercel → Storage → apna database → `DATABASE_URL` copy karo, phir laptop pe:

```powershell
$env:DATABASE_URL = "postgresql://...yahan paste karo..."
python manage.py migrate
python manage.py seed_data          # optional
python manage.py createsuperuser    # live site ka admin
Remove-Item Env:DATABASE_URL        # wapas local SQLite pe aane ke liye
```

> Jab bhi `models.py` badlo aur nayi migration bane, ye `migrate` live database pe bhi dobara chalana.

### 6. Redeploy

Vercel → **Deployments** → latest → **Redeploy**. Ab `https://YOUR-APP.vercel.app` khulega.
Iske baad har `git push` pe Vercel khud deploy kar dega.

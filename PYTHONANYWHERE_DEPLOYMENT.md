# PythonAnywhere Deployment Guide

## 🚀 Step-by-Step Deployment

### Step 1: Create PythonAnywhere Account
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for a free account
3. Choose "Beginner" plan

### Step 2: Upload Your Code
1. **Option A: Upload via Files tab**
   - Go to Files tab in PythonAnywhere dashboard
   - Upload your entire `lms_backend` folder
   - Extract it in your home directory

2. **Option B: Use Git (Recommended)**
   ```bash
   # In PythonAnywhere console
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo/lms_backend
   ```

### Step 3: Install Dependencies
```bash
# In PythonAnywhere console
cd lms_backend
pip3.10 install --user -r requirements.txt
```

### Step 4: Configure Database
```bash
# Run migrations
python3.10 manage.py migrate

# Create superuser
python3.10 manage.py createsuperuser
```

### Step 5: Configure Web App
1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Select **Python 3.10**
5. Click **Next**

### Step 6: Set Up WSGI Configuration
1. In the Web tab, click on **"WSGI configuration file"**
2. Replace the content with:

```python
import os
import sys

# Add your project directory to the Python path
path = '/home/yourusername/lms_backend'  # Replace with your actual path
if path not in sys.path:
    sys.path.append(path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'lms_backend.settings'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Step 7: Configure Static Files
1. In the Web tab, scroll down to **"Static files"**
2. Add these mappings:
   - **URL:** `/static/`
   - **Directory:** `/home/yourusername/lms_backend/staticfiles/`

### Step 8: Update ALLOWED_HOSTS
In your `settings.py`, replace `yourusername` with your actual PythonAnywhere username:
```python
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1',
    'yourusername.pythonanywhere.com',  # Your actual username
    '.pythonanywhere.com'
]
```

### Step 9: Reload Web App
1. Go to Web tab
2. Click **"Reload"** button
3. Your app should be live at `https://yourusername.pythonanywhere.com`

## 🔧 Troubleshooting

### Common Issues:
1. **Import errors:** Make sure all dependencies are installed
2. **Database errors:** Run migrations with `python3.10 manage.py migrate`
3. **Static files not loading:** Check static files configuration
4. **CORS errors:** Update CORS settings in your frontend

### Useful Commands:
```bash
# Check if your app is working
python3.10 manage.py check

# Collect static files
python3.10 manage.py collectstatic

# View logs
# Go to Web tab → "Error log" or "Server log"
```

## 📝 Notes
- Free accounts have limited CPU seconds per month
- Database is SQLite (sufficient for testing)
- For production, consider upgrading to paid plan








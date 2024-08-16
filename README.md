# OnePrep Django Application Setup Guide

## Introduction
This README documents the setup process, initial issues encountered, and solutions implemented for the OnePrep Django application. It covers database configuration, migration adjustments, and deployment considerations.

## Initial Setup and Issues

### Dependencies
- Ensure all required packages are listed in `requirements.txt`
- Run `pip install -r requirements.txt` to install dependencies

### Database Configuration
- Initially configured for PostgreSQL, switched to SQLite for simplicity
- Modified `config/settings/base.py` to use SQLite

### Migration Issues
- Encountered compatibility issues with SQLite and certain Django model constraints
- Adjusted migrations in the `questions` app to ensure SQLite compatibility

## Key Changes Made

### Database Settings (`config/settings/base.py`)
- Updated DATABASES setting to use SQLite:
  ```python
  DATABASES = {
      "default": {
          "ENGINE": "django.db.backends.sqlite3",
          "NAME": BASE_DIR / "db.sqlite3",
      }
  }
  ```

### Model Adjustments (`questions/models.py`)
- Removed conditional constraints incompatible with SQLite
- Implemented non-conditional constraints and indexes for better compatibility
- Added comments to explain changes and potential application-level validations needed

### Migration Modifications (`questions/migrations/0001_initial.py`)
- Removed SQLite-incompatible constraints
- Added TODO comments for alternative indexing strategies

## Deployment Considerations

### Local Testing
1. Run `python manage.py migrate` to apply database changes
2. Start the development server: `python manage.py runserver`
3. Access the application at `http://localhost:8000`

### Google Cloud Platform (GCP) Deployment
- Configured `app.yaml` for GCP App Engine deployment
- Ensure `gunicorn` is installed and specified in `requirements.txt`
- Deploy using `gcloud app deploy`

## Troubleshooting Tips
- If encountering database errors, check SQLite file permissions
- For migration issues, consider resetting migrations: `python manage.py migrate --fake questions zero`
- Monitor GCP logs for deployment-specific issues

## Resources
- Django Documentation: https://docs.djangoproject.com/
- SQLite with Django: https://docs.djangoproject.com/en/3.2/ref/databases/#sqlite-notes
- GCP App Engine Deployment: https://cloud.google.com/appengine/docs/standard/python3/runtime

## Next Steps
- Implement additional data validation in application logic where needed
- Consider adding more robust error handling and logging
- Regularly update dependencies and check for security patches

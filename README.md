This is the webapp for AI picture classification demo.

add a new line.

Steps of starting web app:
source venv/bin/activate
pip install -r requirements.txt
gunicorn -c dcca-ai.conf application:app


#!/bin/bash
# Run backend locally (without docker)
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
python3 backend/main.py

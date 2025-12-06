
#!/bin/bash
python3 - <<'PY'
from backend.main import Base, engine
Base.metadata.create_all(bind=engine)
print("DB initialized")
PY

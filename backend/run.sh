set -e

# create venv
python3 -m venv .venv
source .venv/bin/activate

# upgrade pip & install
pip install -U pip
pip install -r requirements.txt

# install Playwright browsers
python -m playwright install

# start uvicorn
export UVICORN_CMD="uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "Starting server: $UVICORN_CMD"
$UVICORN_CMD

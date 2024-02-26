python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install black==24.2.0
pip install ruff==0.2.2
pip install ipykernel==6.29.2
pip install pyarrow==15.0.0
pip install pandas==2.2.1
pip install -r requirements.txt
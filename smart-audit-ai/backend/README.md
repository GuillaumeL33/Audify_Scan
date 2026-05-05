# Backend FastAPI - Smart Audit AI

## Installation
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## API
- `POST /api/scans` : code Solidity ou fichiers `.sol`
- `GET /api/scans/{scan_id}`
- `GET /api/scans/{scan_id}/report.json`
- `GET /api/scans/{scan_id}/report.md`
- `GET /health`

## Notes
- Slither est optionnel (auto-détecté via binaire `slither`).
- Claude est optionnel (`ANTHROPIC_API_KEY`).

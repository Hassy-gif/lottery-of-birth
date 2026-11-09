# 🌍 The Lottery of Birth

**Live demo:** https://lottery-of-birth-three.vercel.app

About 134 million babies are born every year, and none of them choose where. Press one button and you're born somewhere on Earth, weighted by real birth data. Then you live a full life using the real odds of that country: surviving childhood, finishing school, getting electricity and internet, income, and how long you live.

## How it works
- **Real data:** a Python script pulls 10 indicators for 196 countries from the World Bank API (births, child mortality, life expectancy, income, schooling, electricity, internet, extreme poverty).
- **Weighted by births, not population:** about 1 in 6 players is born in India, just like real babies.
- **Life simulation:** each life event is a probability roll using that country's real rates, then the result is compared with life in the United States.
- **Shareable lives without a database:** every life comes from a random seed, so the same link replays the exact same life.

## Tech stack
| Layer | Tech |
|---|---|
| Frontend | React + Vite, deployed on Vercel |
| Backend | Python + FastAPI, deployed on Render |
| Data | World Bank Open Data API |

## Security
- **CORS allowlist:** the API only accepts browser requests from this site, configured with an environment variable.
- **Input validation:** life IDs are checked against a strict pattern before use.
- **Secure randomness:** life IDs come from Python's `secrets` module.
- **Least privilege:** Render and Vercel can access only this one repository.
- **No secrets in code:** configuration lives in environment variables.

## Run it locally
```bash
# Backend
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && uvicorn main:app --reload

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

## Roadmap
- Global stats: where everyone has been born so far
- Rate limiting on the API
- More life events (marriage age, gender gaps, healthcare access)

*Each life is a simplified simulation based on national averages. Real lives vary much more than any model.*

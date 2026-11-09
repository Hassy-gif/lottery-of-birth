"""Simulates one human life using real World Bank odds for the country you are born in."""
import json
import random
import re
import secrets
from pathlib import Path

DATA = json.loads((Path(__file__).parent / "data" / "countries.json").read_text())
WEIGHTS = [c["births_per_year"] for c in DATA]
TOTAL_BIRTHS = sum(WEIGHTS)
BY_CODE = {c["code"]: c for c in DATA}

# A life ID is the random seed. Same ID = same life, so lives can be shared without a database.
SEED_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,32}$")

STAT_KEYS = [
    "population", "births_per_year", "under5_mortality", "life_expectancy",
    "gdp_per_capita", "primary_completion", "secondary_completion",
    "electricity", "internet", "extreme_poverty",
]


def new_seed():
    return secrets.token_urlsafe(9)  # 12 random URL-safe characters


def chance(percent):
    """Turn a percentage like 87.5 into a probability between 0 and 1."""
    return max(0.0, min(1.0, percent / 100))


def stats(c):
    return {k: c.get(k) for k in STAT_KEYS}


def simulate(seed):
    rng = random.Random(seed)
    c = rng.choices(DATA, weights=WEIGHTS, k=1)[0]
    name = c["name"]
    sex = "girl" if rng.random() < 0.488 else "boy"  # slightly more boys are born worldwide
    events = []

    def add(age, kind, text, good=None):
        events.append({"age": age, "type": kind, "text": text, "good": good})

    add(0, "born", f"You are born a {sex} in {name}, one of about "
        f"{c['births_per_year']:,} babies born there this year.")

    # 1. Surviving childhood
    q5 = c["under5_mortality"] / 1000
    if rng.random() < q5:
        death_age = rng.choice([0, 0, 0, 0, 1, 1, 2, 3, 4])
    else:
        # Life expectancy at birth includes child deaths, so adults live a bit longer on average.
        adult_mean = (c["life_expectancy"] - q5 * 1) / (1 - q5)
        death_age = max(5, min(105, round(rng.gauss(adult_mean, 12))))

    def alive_at(age):
        return age < death_age

    if alive_at(1) and "electricity" in c:
        if rng.random() < chance(c["electricity"]):
            add(1, "electricity", "Your home has electricity.", True)
        else:
            add(1, "electricity", f"Your home has no electricity, like "
                f"{100 - c['electricity']:.0f}% of people in {name}.", False)

    if alive_at(3) and "extreme_poverty" in c:
        if rng.random() < chance(c["extreme_poverty"]):
            add(3, "poverty", f"Your family lives in extreme poverty, like "
                f"{c['extreme_poverty']:.0f}% of people in {name}.", False)

    if alive_at(5):
        add(5, "survived", f"You survive to age 5. In {name}, "
            f"{c['under5_mortality']:.0f} of every 1,000 children do not.", True)

    finished_primary = False
    if alive_at(12) and "primary_completion" in c:
        finished_primary = rng.random() < chance(c["primary_completion"])
        if finished_primary:
            add(12, "school", "You finish primary school.", True)
        else:
            add(12, "school", f"You never finish primary school. Only "
                f"{min(c['primary_completion'], 100):.0f}% of children in {name} do.", False)

    if alive_at(13) and "internet" in c:
        if rng.random() < chance(c["internet"]):
            add(13, "internet", "You get online for the first time.", True)
        else:
            add(13, "internet", f"You never use the internet, like "
                f"{100 - c['internet']:.0f}% of people in {name}.", False)

    if alive_at(16) and finished_primary and "secondary_completion" in c:
        # Odds of finishing secondary school, given you already finished primary.
        p = chance(c["secondary_completion"]) / max(chance(c.get("primary_completion", 100)), 0.01)
        if rng.random() < min(p, 1):
            add(16, "school", "You finish secondary school.", True)
        else:
            add(16, "school", "You leave school before finishing secondary school.", False)

    if alive_at(25) and "gdp_per_capita" in c:
        add(25, "income", f"The average income in {name} is about "
            f"${c['gdp_per_capita']:,.0f} a year (adjusted for local prices).")

    if death_age < 5:
        add(death_age, "death", f"You die before your fifth birthday. In {name}, "
            f"{c['under5_mortality']:.0f} of every 1,000 children do.", False)
    else:
        add(death_age, "death", f"You die at age {death_age}. Life expectancy in "
            f"{name} is {c['life_expectancy']:.0f}.")

    events.sort(key=lambda e: e["age"])
    usa = BY_CODE.get("USA")
    return {
        "seed": seed,
        "sex": sex,
        "death_age": death_age,
        "country": {k: c[k] for k in ["code", "iso2", "name", "region", "income_level"]},
        "birth_chance_percent": round(c["births_per_year"] / TOTAL_BIRTHS * 100, 3),
        "events": events,
        "stats": stats(c),
        "compare": {"name": usa["name"], "stats": stats(usa)} if usa else None,
    }

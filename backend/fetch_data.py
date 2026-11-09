"""Download real country data from the World Bank API and save it to data/countries.json."""
import json
import requests

API = "https://api.worldbank.org/v2"

INDICATORS = {
    "population": "SP.POP.TOTL",
    "birth_rate": "SP.DYN.CBRT.IN",            # births per 1,000 people per year
    "under5_mortality": "SH.DYN.MORT",         # deaths before age 5 per 1,000 births
    "life_expectancy": "SP.DYN.LE00.IN",       # years
    "gdp_per_capita": "NY.GDP.PCAP.PP.CD",     # income per person, price-adjusted (PPP $)
    "primary_completion": "SE.PRM.CMPT.ZS",    # % who finish primary school
    "secondary_completion": "SE.SEC.CMPT.LO.ZS",  # % who finish lower secondary
    "electricity": "EG.ELC.ACCS.ZS",           # % with electricity
    "internet": "IT.NET.USER.ZS",              # % using the internet
    "extreme_poverty": "SI.POV.DDAY",          # % in extreme poverty
}
REQUIRED = ["population", "birth_rate", "under5_mortality", "life_expectancy"]


def get(url):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.json()


def main():
    meta = get(f"{API}/country?format=json&per_page=400")[1]
    countries = {
        c["id"]: {
            "code": c["id"],
            "iso2": c["iso2Code"],
            "name": c["name"],
            "region": c["region"]["value"].strip(),
            "income_level": c["incomeLevel"]["value"],
        }
        for c in meta
        if c["region"]["id"] != "NA"  # skip aggregates like "World" or "Europe"
    }

    for key, code in INDICATORS.items():
        print(f"Downloading {key}...")
        rows = get(f"{API}/country/all/indicator/{code}?format=json&per_page=20000&mrnev=1")[1] or []
        for row in rows:
            cid = row["countryiso3code"]
            if cid in countries and row["value"] is not None:
                countries[cid][key] = row["value"]
                countries[cid][key + "_year"] = int(row["date"])

    result = []
    for c in countries.values():
        if all(k in c for k in REQUIRED):
            c["births_per_year"] = round(c["population"] * c["birth_rate"] / 1000)
            result.append(c)
    result.sort(key=lambda c: c["births_per_year"], reverse=True)

    with open("data/countries.json", "w") as f:
        json.dump(result, f, indent=2)

    total = sum(c["births_per_year"] for c in result)
    print(f"\nSaved {len(result)} countries. About {total:,} babies are born each year.")
    print("Most likely places to be born:")
    for c in result[:5]:
        print(f"  {c['name']}: {c['births_per_year'] / total:.1%}")


if __name__ == "__main__":
    main()

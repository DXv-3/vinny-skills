# Salary-Focused Search Queries

<!-- CUSTOMIZED FOR MAXIMUM COMPENSATION -->

## High-Paying Job Searches

Run these through `/scrape` or the LinkedIn search skills:

### Top-Tier Companies (Target Index 150+)
```
"Google" OR "Meta" OR "Apple" OR "Microsoft" OR "Netflix"
"Staff Software Engineer" OR "Senior Staff" OR "Principal"
"Machine Learning" OR "LLM" OR "AI"
```

### High-Paying Industries (Target Index 130+)
```
"Snowflake" OR "Palantir" OR "Datadog" OR "Twilio"
"Stripe" OR "Coinbase" OR "Plaid"
"Cybersecurity Engineer" OR "Security Architect"
"Cloud Architect" OR "Principal Cloud Engineer"
```

### High-Demand Skill Searches (Premium Rates)
```
"LLM Engineer" OR "Prompt Engineer" OR "AI Research Engineer"
"Machine Learning Engineer" OR "ML Engineer"
"Cloud Security" OR "Security Engineering"
"Data Engineering" OR "Data Platform"
"Platform Engineer" OR "Site Reliability Engineer"
```

## LinkedIn Search Commands

```bash
# High-paying AI roles
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -q "LLM Engineer" -l "Remote" --jobage 30 --format table

# Big Tech senior roles
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -q "Senior Staff Software Engineer" -l "San Francisco, CA" --remote remote --format table

# High-paying fintech
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -q "Machine Learning Engineer" -l "New York, NY" --format table
```

## Geographic High-Paying Markets

Priority locations for salary maximization:
1. **San Francisco Bay Area** - Highest software engineer salaries
2. **Seattle** - Amazon/Microsoft rates
3. **New York** - Finance + Tech crossover
4. **Austin** - Growing tech hub with good rates
5. **Remote (Big Tech)** - Many companies offer SF rates everywhere

## Salary Signal Keywords

Filter for roles mentioning:
- "competitive salary"
- "above market"
- "sign-on bonus"
- "equity package"
- "total compensation"
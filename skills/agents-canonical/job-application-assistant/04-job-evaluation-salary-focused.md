# Salary-Focused Job Evaluation Framework

<!-- CUSTOMIZED: Enhanced for salary-maximization -->

## Scoring Dimensions

Evaluate each job posting against these five dimensions:

### 1. Technical Skills Match (0-100)
How well do the required/preferred skills align with the candidate's capabilities?

| Score | Meaning |
|-------|---------|
| 80-100 | Core requirements are primary skills |
| 60-79 | Most requirements match, 1-2 gaps that are learnable |
| 40-59 | Partial match, significant upskilling needed |
| 0-39 | Fundamental mismatch |

**Strong match areas:** [YOUR_PRIMARY_SKILLS]
**Moderate match areas:** [YOUR_SECONDARY_SKILLS]
**Weak match areas:** [SKILLS_YOU_LACK]

### 2. Experience Match (0-100)
Does work history align with what they're looking for?

| Score | Meaning |
|-------|---------|
| 80-100 | Direct experience in the same domain and role type |
| 60-79 | Related experience, transferable skills clear |
| 40-59 | Adjacent experience, would need to make the case |
| 0-39 | Unrelated experience |

**Strong:** [YOUR_DIRECT_EXPERIENCE_DOMAINS]
**Moderate:** [YOUR_ADJACENT_EXPERIENCE]
**Entry-level:** [ROLES_WITH_LIMITED_EXPERIENCE]

### 3. Salary Benchmark (0-100) - **PRIMARY FOCUS FOR MONEY MAXIMIZATION**

**This dimension is now weighted at 35% (up from optional) because maximizing compensation is the goal.**

If salary data is available, evaluate compensation competitiveness:

```bash
python salary_lookup.py "<Company Name>" --json
```

If the posting specifies a city, add `--city "<City>"`.

**Salary scoring framework:**

| Score | Benchmark Interpretation |
|-------|------------------------|
| 80-100 | Top-tier paying company (index 115+ or 20%+ above market) |
| 60-79 | Above average (index 105-115 or 10-20% above market) |
| 40-59 | Market average (index 95-105 or ±10% of market) |
| 20-39 | Below market (index 85-95 or 10-20% below market) |
| 0-19 | Significantly underpaying (index <85 or >20% below market) |

**No salary data available - infer from:**
- Job level (Senior/Staff/Principal = higher bands)
- Equity offerings
- Benefits comprehensiveness
- Company funding stage and reputation
- Industry benchmarks

### 4. Behavioral/Culture Fit (0-100)
Does the role and company culture match the behavioral profile?

| Score | Meaning |
|-------|---------|
| 80-100 | Culture strongly matches behavioral preferences |
| 60-79 | Mixed signals but mostly compatible |
| 40-59 | Some friction areas |
| 0-39 | Significant culture mismatch |

**Red flags to research:** Department disorganization, work dominated by maintenance over development, poor chemistry with leadership, culture mismatches. Check reviews, media coverage, LinkedIn connections, and network contacts for insider perspective.

### 5. Location & Logistics (Pass/Fail + Notes)
- Within commute range: PASS
- Remote with occasional office: PASS
- Requires relocation: FAIL (deal-breaker - unless salary compensates)
- Frequent international travel: FLAG (discuss salary premium justification)

### 6. Career Alignment & Growth (0-100)
Does this role advance career goals and increase future earning potential?

| Score | Meaning |
|-------|---------|
| 80-100 | Strong growth trajectory + high future compensation potential |
| 60-79 | Good role with decent advancement + reasonable compensation growth |
| 40-59 | Limited growth but stable/pay acceptable |
| 0-39 | Dead end or backwards step |

**Career goals:**
- Maximize immediate compensation while building high-value skills
- Target roles with equity/gratuity structures that compound wealth
- Prioritize companies with documented promotion paths and salary bands
- Focus on high-demand specializations (AI/ML, cloud, security, data engineering)

## Output Format

Present the evaluation as:

```
## Job Fit Evaluation: [Role] at [Company]

| Dimension | Score | Notes |
|-----------|-------|-------|
| Technical Skills | XX/100 | [brief note] |
| Experience Match | XX/100 | [brief note] |
| Salary Benchmark | XX/100 | [salary range/index + market comparison] |
| Behavioral Fit | XX/100 | [brief note] |
| Location | PASS/FAIL | [brief note] |
| Career Alignment | XX/100 | [brief note] |

**Overall Score: XX/100** (weighted average)

### Salary Assessment
- **Compensation level:** [Above Market / At Market / Below Market]
- **Total package:** [Salary + Equity + Benefits analysis]
- **Negotiation potential:** [High / Medium / Low based on company practices]

### Verdict: [Strong Fit / Good Fit / Moderate Fit / Weak Fit / Poor Fit]
```

## Weighting - **SALARY OPTIMIZED**

- **Salary Benchmark: 35%** (increased priority)
- Technical Skills: 25%
- Experience Match: 20%
- Behavioral Fit: 10%
- Career Alignment: 10%

(Location is pass/fail, not weighted)

## Thresholds

- **Strong Fit** (78+): High pay + good match - apply immediately, negotiate aggressively
- **Good Fit** (65-77): Solid compensation + decent match - apply, negotiate
- **Moderate Fit** (50-64): Market rate + partial match - consider carefully
- **Weak Fit** (35-49): Below market + weak match - skip unless strategic
- **Poor Fit** (<35): Low pay + poor match - skip

## Salary Negotiation Strategy

### Pre-application Signals (High Negotiation Potential)
- Explicitly states "competitive salary" or salary ranges
- Equity/gratuity mentioned prominently
- "Benefits package" or "comprehensive benefits" listed
- Large tech company or well-funded startup
- Role labeled "Senior", "Lead", or "Principal"
- No salary in posting = potential to negotiate higher

### Negotiation Angles for Cover Letter

- "Based on my research, roles with these responsibilities typically command X-Y range"
- "I'm seeking a package that reflects the market value for these specialized skills"
- "I'm flexible on structure (salary vs equity) based on total compensation"
- Reference specific achievements that justify premium compensation

### ATS Keyword Stuffers (Salary-Coded Language)
- "Competitive compensation package"
- "Market-leading salary"
- "Above-market rates"
- "Total compensation includes equity/options"
- "Salary commensurate with experience" → indicates negotiation expectation
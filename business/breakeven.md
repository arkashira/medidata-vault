# breakeven.md

## Unit Economics & Break-even Analysis

### Cost per Active User
- **Compute Costs**: $5/user/month
  - Based on average cloud compute pricing for data processing and analytics.
  
- **Storage Costs**: $2/user/month
  - Estimated storage cost for medical datasets (HIPAA-compliant storage solutions).
  
- **Bandwidth Costs**: $1/user/month
  - Average cost for data transfer and API calls.

**Total Cost per Active User**: **$8/user/month**

---

### Pricing Tiers
| Tier         | Price ($/mo) | Features                                                                 |
|--------------|---------------|--------------------------------------------------------------------------|
| Basic        | $20           | Ingest, query, and visualize datasets; basic compliance checks          |
| Professional  | $50           | All Basic features + version control, advanced analytics, and reporting  |
| Enterprise    | $100          | All Professional features + dedicated support, custom compliance checks   |

---

### Customer Acquisition Cost (CAC) Range
- **CAC Estimate**: $100 - $200
  - Includes marketing, sales efforts, and onboarding costs.

---

### Lifetime Value (LTV) Estimate
- **Average Revenue per User (ARPU)**: 
  - Assuming a mix of users across tiers: 
    - 50% Basic, 30% Professional, 20% Enterprise
    - ARPU = (0.5 * $20) + (0.3 * $50) + (0.2 * $100) = $10 + $15 + $20 = **$45/month**
  
- **Average Customer Lifespan**: 24 months
- **LTV**: 
  - LTV = ARPU * Average Customer Lifespan = $45 * 24 = **$1,080**

---

### Break-even Users Count
- **Monthly Fixed Costs**: $2,000 (estimated operational costs)
- **Break-even Formula**: Break-even Users = Monthly Fixed Costs / (Price per User - Cost per User)

Using the Basic tier for conservative estimates:
- Break-even Users = $2,000 / ($20 - $8) = $2,000 / $12 = **167 users**

---

### Path to $10K MRR
- **Target Monthly Recurring Revenue (MRR)**: $10,000
- **Using Pricing Tiers**:
  
1. **Basic Tier**: 
   - Users needed = $10,000 / $20 = **500 users**
  
2. **Professional Tier**: 
   - Users needed = $10,000 / $50 = **200 users**
  
3. **Enterprise Tier**: 
   - Users needed = $10,000 / $100 = **100 users**

**Optimal Path**: 
- Focus on acquiring **200 Professional tier users** for a balanced approach to revenue and user engagement.
# 🚀 Supabase & Railway Setup Guide

## ✅ Supabase Database Setup

### Step 1: Run Schema in Supabase

1. Go to your Supabase project: https://app.supabase.com
2. Click **SQL Editor** (left sidebar)
3. Click **New query**
4. Copy the entire contents of `infra/supabase/schema.sql`
5. Paste into the SQL editor
6. Click **Run** (or press F5)
7. You should see: "Success. No rows returned"

### Step 2: Run Seed Data (Optional for testing)

1. In SQL Editor, click **New query**
2. Copy contents of `infra/supabase/seed.sql`
3. Paste and **Run**
4. Verify data:
   ```sql
   SELECT * FROM daily_sales;
   SELECT * FROM user_activity;
   SELECT * FROM fraud_signals;
   ```

### Step 3: Verify Tables Created

In Supabase, go to **Table Editor** (left sidebar), you should see:
- ✅ daily_sales
- ✅ user_activity
- ✅ fraud_signals
- ✅ raw_events (partitioned)

---

## 🔑 GitHub Secrets Configuration

Go to: https://github.com/aditya-hubli/Real-Time-Event-Driven-Data-Platform/settings/secrets/actions

### Add these secrets:

| Secret Name | How to Get It | Example |
|-------------|---------------|---------|
| `SUPABASE_URL` | Supabase → Settings → API → Project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase → Settings → API → anon public | `eyJhbGc...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Settings → API → service_role | `eyJhbGc...` (⚠️ keep secret!) |
| `SUPABASE_DB_URL` | Supabase → Settings → Database → Connection string → URI | `postgresql://postgres...` |
| `RAILWAY_TOKEN` | Railway → Settings → Tokens → Create | `abc123...` |

---

## 🚂 Railway Project Structure

Your Railway project will have these services:

```
event-driven-platform/
├── redpanda (Message Broker)
├── user-service
├── order-service
├── payment-service
├── stream-processor
├── analytics-api
└── dashboard
```

Each service will be deployed from Docker images built by GitHub Actions.

---

## 📋 Next Steps

Once you've completed the above:

1. ✅ Supabase schema applied
2. ✅ GitHub secrets configured
3. ✅ Railway project created

**Reply "done" and I'll proceed with creating Branch 1 files!**

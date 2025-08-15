# Supabase API Setup Guide

## 🔑 Step 1: Get Supabase API Keys

### 1. Go to Supabase Dashboard
- Navigate to: https://supabase.com/dashboard/project/ouailhcurstporcnypfk

### 2. Get API Keys
- Go to **Settings** → **API**
- Copy these values:
  - **Project URL**: `https://ouailhcurstporcnypfk.supabase.co`
  - **Service Role Key**: (the secret key for server-side operations)

## 🔧 Step 2: Update Environment Variables

### Update your `.env` file with:

```bash
# Supabase API Configuration
SUPABASE_API_URL=https://ouailhcurstporcnypfk.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_actual_service_role_key_here
```

**⚠️ Important**: Replace `your_actual_service_role_key_here` with the actual service role key from your Supabase dashboard.

## 🚀 Step 3: Test the API Integration

### Run the workflow to test:
```bash
source venv/bin/activate
python3 reporting_workflow.py
```

## ✅ Benefits of API vs Selenium

### **API Method (New):**
- ✅ **Faster** - Direct database insertion
- ✅ **More reliable** - No browser automation issues
- ✅ **Better error handling** - Clear API responses
- ✅ **No date format issues** - Direct data insertion
- ✅ **No browser dependencies** - Works headless
- ✅ **Better logging** - Clear success/failure responses

### **Selenium Method (Old):**
- ❌ **Slower** - Browser automation
- ❌ **Fragile** - Form field changes break it
- ❌ **Date issues** - Form validation can modify dates
- ❌ **Browser dependencies** - Requires Chrome/WebDriver
- ❌ **Unreliable** - Can fail due to UI changes

## 🔍 API Endpoint Details

The new agent uses:
- **Endpoint**: `https://ouailhcurstporcnypfk.supabase.co/rest/v1/progress_reports`
- **Method**: `POST`
- **Headers**: 
  - `apikey`: Your service role key
  - `Authorization`: `Bearer your_service_role_key`
  - `Content-Type`: `application/json`

## 📊 Data Format

The API expects data in this format:
```json
{
  "week_nu": 15,
  "date": "2025-08-15",
  "weight": 124.2,
  "fat_percent": 0.513,
  "bmi": 45.6,
  "fat_weight": 63.7,
  "lean_weight": 60.5,
  "neck": 16,
  "shoulders": 18,
  "biceps": 18,
  "forearms": 12.5,
  "chest": 43.5,
  "above_navel": 39,
  "navel": 39,
  "waist": 42,
  "hips": 48,
  "thighs": 29,
  "calves": 17
}
```

## 🛡️ Security Notes

- **Service Role Key** has full database access
- **Keep it secret** - Don't commit to version control
- **Use environment variables** - Never hardcode in code
- **Monitor usage** - Check Supabase logs for API calls

## 🔄 Migration Complete

Once you've updated the environment variables:
1. The workflow will automatically use the new API agent
2. No more Selenium browser automation
3. Faster, more reliable data insertion
4. No more date format issues
5. Better error reporting

**The date format issue should be completely resolved with this API approach!** 🎉

# App Workflow — Simple, Detailed Explanation

This document explains how the workflow works in this app in plain language. There are **two** layers: the **GitHub Actions workflow** (how the job is run) and the **application workflow** (what the app actually does).

---

## Part 1: GitHub Actions Workflow (How the Job Runs)

Defined in `.github/workflows/fitness-reporting.yml`. This is the “runner” that sets up the environment and runs your Python reporting pipeline.

### When It Runs

- **Manual only (for now)**  
  The scheduled cron is commented out, so the workflow does **not** run on a schedule. It runs only when you trigger it manually from the GitHub Actions tab (“Run workflow”).
- **Manual options when you run it:**
  - **Test mode** – if you turn it on, it skips actually sending emails.
  - **Custom email (To)** – override who gets the report for this run.
  - **Custom CC** – override who gets a copy (comma-separated).
  - **Skip notifications** – don’t send push notifications for this run.

### What the Workflow Does, Step by Step

1. **Checkout**  
   Checks out your repo so the runner has the latest code.

2. **Python setup**  
   Installs Python 3.11 on an Ubuntu runner.

3. **Playwright / Chromium**  
   Installs Playwright and the Chromium browser (used for browser automation in your app, e.g. Supabase).

4. **Python dependencies**  
   Runs `pip install -r requirements.txt` so all Python packages are available.

5. **Credentials**  
   Writes secret values from GitHub Secrets into files the app expects:
   - `credentials.json` (Google OAuth client)
   - `token.json` (Gmail API token)
   - `token_sender.json` (token for the sending Gmail account)  
   Then it checks that these files exist and are valid JSON.

6. **Environment variables**  
   Sets all the env vars the app needs (Gmail addresses/passwords, API keys for OpenAI, Anthropic, Google, Supabase, Pushover, LangSmith, LLM provider/model settings, email recipients, test mode, etc.).  
   If you triggered manually and set “custom email” or “skip notifications,” those choices are applied here.

7. **Display configuration**  
   Prints a summary of how the run is configured (event type, test mode, emails, notifications, LLM config, which API keys are set). This is for debugging and transparency.

8. **Run the fitness reporting workflow**  
   Runs:
   ```bash
   python3 reporting_workflow.py
   ```
   This is where the **actual app workflow** (Part 2) runs.

9. **Upload workflow logs**  
   After the run (success or failure), it uploads logs and outputs as artifacts (e.g. `*.log`, `validation_result_*.json`, `fitness_data_*.json`, `*.xlsx`) and keeps them for 7 days.

10. **Cleanup**  
    Deletes `credentials.json` and `token.json` from the runner so secrets aren’t left on disk.

11. **Summary**  
    Prints a short summary (repo, run ID, event, status).

So in simple terms: **GitHub Actions prepares the machine, injects secrets and config, runs `reporting_workflow.py`, then saves logs and cleans up.**

---

## Part 2: Application Workflow (What the App Does)

This is the **LangGraph** pipeline in `reporting_workflow.py`. It’s a linear + conditional chain of steps that:

- Fetches fitness data from email and from a database  
- Reconciles and validates that data  
- Enters it into Supabase  
- Drafts a report email  
- Optionally improves the draft with a feedback loop  
- Sends the final email and cleans up  

Below is the same flow in simple, ordered language.

### Before the Graph: Gmail Token Check

Before the LangGraph steps start, the script checks the Gmail OAuth token (used to send the final report). If it’s expired or missing, it tries to refresh it using `credentials.json` and `token_sender.json`. If that fails, the workflow stops (you’d need to fix tokens locally or in secrets).

---

### Step 1: Model Config Validation

- **What:** Checks that all required AI/LLM settings are present and valid (e.g. provider and model for each of the 3 LLM slots).
- **Why:** So the rest of the pipeline doesn’t run with broken or missing model config.
- **Result:** If validation fails → workflow ends. If it passes → continue to fetch email.

---

### Step 2: Fetch Email

- **What:** Gets the **latest fitness email** from Gmail (using the “fetcher” Gmail account and app password from env).
- **Why:** This email is the **source of new fitness data** (e.g. weight, measurements).
- **Result:** Email content is parsed into a structured format (e.g. JSON) and stored in workflow state. Then the pipeline continues.

---

### Step 3: Fetch Database

- **What:** Fetches the **latest fitness entry** from your database (SQLite Cloud in your setup).
- **Why:** You need the “last known” data to compare with the new email and to detect duplicates or mismatches.
- **Result:** Database record is turned into a similar structured format and stored. Then the pipeline continues.

---

### Step 4: Reconcile Data

- **What:** An LLM compares the **email data** and **database data** to see if they match and whether it makes sense to proceed (e.g. “is this new data or already stored?”).
- **Why:** To avoid double-processing and to ensure both sources agree before updating anything.
- **Result:**  
  - If they don’t match or it’s not okay to proceed → later steps (validation, Supabase, report) are effectively skipped and the workflow can end without sending a report.  
  - If they match and the system says “proceed” → continue to validation.

---

### Step 5: Validate Data

- **What:** Another LLM checks the **new fitness data** (from the email) against **historical trends** (e.g. “is this weight/measurement plausible given past entries?”). You get a validation status and often a confidence score.
- **Why:** To catch typos or impossible values before they’re written to Supabase or reported.
- **Result:**  
  - If validation fails → workflow can end (no Supabase entry, no report).  
  - If validation succeeds → continue to Supabase entry.

---

### Step 6: Supabase Entry

- **What:** The app **enters the validated fitness data** into your Supabase-backed app. This is done via automation (e.g. browser/Playwright or API), so the data shows up in your fitness app as if someone had typed it in.
- **Why:** So your “source of truth” (Supabase / app) is updated with the new measurements.
- **Result:**  
  - If entry fails → workflow can end.  
  - If entry succeeds → continue to report drafting.

---

### Step 7: Report Drafter

- **What:** An LLM **drafts the fitness report email**: the text that will be sent to the coach/recipient, summarizing progress and metrics.
- **Why:** To produce a readable, professional report instead of raw numbers.
- **Result:** A draft email body (and any structured “email body data”) is stored. Then the pipeline evaluates this draft.

---

### Step 8: Email Evaluation

- **What:** Another LLM **evaluates the draft email** (quality, clarity, completeness) and decides: **approved** or **needs revision**, and optionally gives **feedback** (e.g. “add a sentence about trends”).
- **Why:** So the final email isn’t sent until it meets a quality bar, within limits (see next step).
- **Result:** Stored: approved yes/no, score, and feedback text.

---

### Step 9: Feedback Decision

- **What:** The workflow decides what to do next:
  - If the email is **approved** → go to **send final email**.
  - If the email is **not approved** but you haven’t hit the **max iterations** (e.g. 3) → go to the **feedback loop** and then **back to the report drafter** with the evaluation feedback so it can redraft.
  - If the email is **not approved** but you’ve **already used the max iterations** → go to **send final email** anyway (send the best version you have).
- **Why:** Balance between quality (iterative improvement) and not running forever (cap at 3 drafts).
- **Result:** Either “send final email,” “do another draft (feedback loop),” or in error cases “end workflow.”

---

### Step 10: Feedback Loop (Only When Improving the Draft)

- **What:** Takes the **evaluation feedback** and updates the workflow state (e.g. “feedback” text, increment “iteration count”). Then the graph sends execution **back to the report drafter**.
- **Why:** So the drafter can produce a new draft using that feedback.
- **Result:** Report drafter runs again; then evaluation and feedback decision run again until approved or max iterations.

---

### Step 11: Send Final Email

- **What:** The **Final Email Agent** sends the **approved (or final) report email** from your sending Gmail account (OAuth, e.g. charles@parmarcharles.com). It can attach an Excel file with historical data and may trigger a push notification (e.g. Pushover) that the report was sent.
- **Why:** To deliver the report to the coach/recipient.
- **Result:** Success or failure is recorded (e.g. `final_email_sent`). Then the pipeline always runs cleanup.

---

### Step 12: Cleanup

- **What:** Cleans up resources used during the run (e.g. browser sessions, temporary files).
- **Why:** So the runner (or your machine) doesn’t leave stray processes or files.
- **Result:** Cleanup result is stored; then the workflow ends.

---

### Step 13: End Workflow

- **What:** The graph finishes. All state (email data, database data, reconciliation, validation, Supabase result, report draft, evaluation, whether email was sent, cleanup) is available in the final state.
- **Why:** To have a clear end and a single “result” of the run.

---

## Summary in One Paragraph

**GitHub Actions** (when you run it manually) checks out the repo, installs Python and Playwright, creates credential files from secrets, sets all environment variables, runs **`reporting_workflow.py`**, then uploads logs and removes credential files.  

**The app workflow** checks the Gmail token, validates LLM config, fetches the latest fitness email and the latest DB row, reconciles them with an LLM, validates the new data against history, enters it into Supabase, drafts a report email, has another LLM evaluate the draft and optionally loops back up to 3 times to improve it, then sends the final email (with optional Excel and push notification) and cleans up.

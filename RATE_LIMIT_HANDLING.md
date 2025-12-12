# Rate Limit and Error Handling

## Overview

ESCAPER automatically handles OpenAI API rate limits and transient errors with **exponential backoff retry logic**. Your experiments will continue without manual intervention.

## What Gets Handled

### 1. Rate Limit Errors (Most Common)

When you hit OpenAI's rate limits, ESCAPER automatically:
- Detects the rate limit error
- Waits with exponential backoff (1s → 2s → 4s → 8s → 16s, max 60s)
- Retries up to 5 times
- Shows clear progress messages

**Example output:**
```
⚠️  Rate limit hit. Retrying in 2.0s... (attempt 1/5)
⚠️  Rate limit hit. Retrying in 4.0s... (attempt 2/5)
✓ Request succeeded
```

### 2. Connection Errors

Network issues are handled the same way:
- `APIConnectionError`: Network connectivity issues
- `APITimeoutError`: Request took too long
- Automatic retry with exponential backoff

### 3. Server Errors (5xx)

When OpenAI's servers have issues:
- Detects 500-599 status codes
- Retries automatically
- Your experiment continues

### 4. Client Errors (4xx)

These **do not** retry (they're not transient):
- Invalid API key
- Malformed requests
- These fail immediately so you can fix the root cause

## Retry Strategy

```python
Attempt 1: Wait 1 second
Attempt 2: Wait 2 seconds  
Attempt 3: Wait 4 seconds
Attempt 4: Wait 8 seconds
Attempt 5: Wait 16 seconds
(Max wait capped at 60 seconds)
```

After 5 attempts, if still failing, the error is raised.

## Rate Limit Best Practices

### Understanding OpenAI Rate Limits

OpenAI has different rate limits based on:
- **Your account tier** (free, tier 1, tier 2, etc.)
- **Model** (GPT-3.5 has higher limits than GPT-4)
- **Time window** (requests per minute, tokens per minute)

Check your limits: https://platform.openai.com/account/limits

### Tips to Avoid Rate Limits

1. **Use GPT-3.5 Turbo for large experiments:**
   ```bash
   python -m escaper.cli.run_experiment \
     --model gpt-3.5-turbo \
     --seeds 50  # Can handle more requests
   ```

2. **Upgrade your OpenAI tier:**
   - Higher tiers = higher rate limits
   - Check platform.openai.com for tier requirements

3. **Accept that rate limits will happen:**
   - For large experiments (20+ seeds), rate limits are expected
   - ESCAPER handles them automatically - no action needed!

4. **Space out large experiments:**
   - Instead of running 100 seeds at once, run multiple smaller batches
   - This is only needed if you're frequently hitting limits

## When Rate Limits Become a Problem

### Symptoms

If you see many consecutive rate limit retries:
```
⚠️  Rate limit hit. Retrying in 2.0s... (attempt 1/5)
⚠️  Rate limit hit. Retrying in 4.0s... (attempt 2/5)
⚠️  Rate limit hit. Retrying in 8.0s... (attempt 3/5)
⚠️  Rate limit hit. Retrying in 16.0s... (attempt 4/5)
⚠️  Rate limit hit. Retrying in 32.0s... (attempt 5/5)
```

### Solutions

1. **Check your account status:**
   - Visit platform.openai.com/account/limits
   - See your current usage and limits
   - Consider upgrading tier

2. **Switch models:**
   ```bash
   # From GPT-4 (lower limits)
   --model gpt-4-turbo-preview
   
   # To GPT-3.5 (higher limits)
   --model gpt-3.5-turbo
   ```

3. **Reduce concurrency:**
   - ESCAPER runs episodes sequentially, so this isn't usually an issue
   - Rate limits are per-minute, so they reset automatically

4. **Wait and retry:**
   - Rate limits reset after the time window passes
   - Come back in 10-15 minutes and try again

## Technical Details

### Implementation

Located in `escaper/core/agents.py` → `OpenAILLMClient.call_with_tools()`:

```python
max_retries = 5
base_delay = 1  # seconds
max_delay = 60  # seconds

for attempt in range(max_retries):
    try:
        response = self.client.chat.completions.create(...)
        return response
    except RateLimitError:
        delay = min(base_delay * (2 ** attempt), max_delay)
        print(f"Rate limit hit. Retrying in {delay:.1f}s...")
        time.sleep(delay)
```

### Error Types Handled

From OpenAI Python SDK:
- `openai.RateLimitError`: Rate limits exceeded
- `openai.APIConnectionError`: Network/connection issues
- `openai.APITimeoutError`: Request timeout
- `openai.APIError` (5xx only): Server-side issues

### Why This Matters

**Without retry logic:**
```
Running episode 5...
Error: RateLimitError - You exceeded your rate limit
Experiment FAILED ❌
(You lose all progress)
```

**With retry logic:**
```
Running episode 5...
⚠️  Rate limit hit. Retrying in 2.0s... (attempt 1/5)
Episode 5: ✓ SUCCESS
Running episode 6...
(Experiment continues smoothly ✓)
```

## Monitoring Rate Limits

### During Experiments

Watch for retry messages:
- **Occasional retries**: Normal, no action needed
- **Frequent retries**: Consider switching to GPT-3.5 or upgrading tier
- **All requests failing**: Check API key and account status

### After Experiments

Check the terminal output log:
```bash
# If you used --log-dir
grep "Rate limit" experiment-logs/terminal_output_*.txt
```

Count how many rate limit hits occurred:
```bash
grep -c "Rate limit hit" experiment-logs/terminal_output_*.txt
```

## FAQs

**Q: Will retries slow down my experiment?**

A: Yes, but only slightly. Most rate limit waits are 1-4 seconds. Without retries, your entire experiment would fail and you'd have to restart.

**Q: Can I disable retries?**

A: Not currently. Retries prevent experiment failures and are a best practice for API usage.

**Q: What if all 5 retries fail?**

A: The experiment stops with a clear error message. This usually means:
- Your API key is invalid
- Your account is suspended
- You're out of credits
- There's a major OpenAI outage

**Q: Does ESCAPER respect OpenAI's Retry-After header?**

A: The current implementation uses exponential backoff rather than Retry-After headers. This is a conservative approach that works well in practice.

## Example: Running a Large Experiment

```bash
# 50 episodes with adversary + reputation + gossip
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary --reputation --gossip \
  --max-steps 40 \
  --seeds 50 \
  --log-dir runs/large_experiment \
  --model gpt-3.5-turbo
```

**Expected behavior:**
- Some rate limit retries (normal)
- Automatic recovery
- Experiment completes successfully
- All output saved to logs

**If using GPT-4 instead:**
- More frequent rate limit retries
- Still completes, just takes longer
- Consider switching to GPT-3.5 for large experiments

## Summary

✅ **Rate limits are handled automatically**
✅ **Experiments continue without manual intervention**
✅ **Clear feedback on retry progress**
✅ **Exponential backoff prevents hammering the API**
✅ **Works for all transient errors, not just rate limits**

You can run experiments confidently knowing that temporary API issues won't derail your work!


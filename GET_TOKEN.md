# How to Get Your OpenReplay Bearer Token

## Steps:

1. **Login to OpenReplay Dashboard**
   - Go to https://app.openreplay.com
   - Login with your credentials

2. **Open Browser Developer Tools**
   - Press F12 or right-click → Inspect
   - Go to the **Network** tab

3. **Find an API Request**
   - Navigate around the dashboard (click on Sessions, etc.)
   - Look for requests to `api.openreplay.com`
   - Click on any request to `/13571/sessions/search` or similar

4. **Copy the Authorization Header**
   - In the request details, go to **Headers** tab
   - Find the `Authorization` header
   - Copy the entire value (it starts with `Bearer eyJ...`)
   - It should look like:
   ```
   Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9...
   ```

5. **Update .env File**
   - Open `.env` file
   - Replace `your_bearer_token_here` with the token (WITHOUT the "Bearer " prefix)
   - Example:
   ```
   OPENREPLAY_API_KEY=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9...
   ```

## Important Notes:

- The token expires after some time (usually 24 hours)
- You'll need to refresh it when it expires
- Keep the token secure - it provides access to your OpenReplay data

## Quick Test:

After updating the token, test with:
```bash
uv run python test_post_api.py
```
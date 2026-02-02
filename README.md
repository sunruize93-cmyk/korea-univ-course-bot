# Korea University Course Registration Bot (Sugang Auto-Register)

Automated Python script for monitoring and registering for courses on the Korea University Course Registration System (Sugang).

## 📢 Manifesto

**"We all pay the same tuition. We deserve to take the classes we actually want."**

Let's be real: course registration shouldn't be a lottery based on who has the fastest click speed or the lowest ping. It feels unfair when you can't get into a class you need just because the server lagged for a second.

This tool is designed to **level the playing field**. It's not about hacking; it's about automating the boring stuff so you can get the education you paid for.

### ⚠️ Heads Up
With great power comes great responsibility.
*   **Don't be reckless**: If you spam the server too hard, you *will* get blocked.
*   **Use common sense**: I wrote this code to help you, but I can't take the fall if the school admin gets mad. Use it wisely, grab your courses, and enjoy your semester.

## Features
- **Automated Login**: Handles credential entry (supports manual CAPTCHA solving).
- **Course Monitoring**: Continuously checks availability for a list of target courses.
- **Auto-Registration**: Instantly attempts to register when a slot opens.
- **Anti-Detection**: Uses Selenium with randomization and proper User-Agent headers.
- **Configurable**: Settings managed via `config.json`.

## Prerequisites
- Python 3.8+
- Google Chrome Browser installed

## Installation

1. Clone or download this repository.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Open `config.json`.
2. Enter your Portal ID and password (same as KUPID):
   ```json
   "username": "2023123456",
   "password": "your_password"
   ```
3. Add the courses you want to monitor:
   ```json
   "target_courses": [
       {
           "course_code": "COSE123",
           "course_name": "Operating Systems"
       }
   ]
   ```
4. Adjust `refresh_interval` (default 3 seconds). **Do not set this too low** to avoid being blocked.

## 🛠️ CRITICAL: Selector Setup
Since the Sugang system's internal HTML structure changes and is not publicly accessible without a student account, **you must update the CSS selectors in `bot.py`**.

1. Open `bot.py`.
2. Search for `TODO: UPDATE THESE SELECTORS`.
3. Go to https://sugang.korea.ac.kr in your Chrome browser, right-click the input fields (ID, Password, Search Box, etc.), and select **Inspect**.
4. Find the `id` or `name` attribute of the elements and update the Python code accordingly.
   - Example: If the ID input has `<input id="login_id" ...>`, change `USERNAME_FIELD_ID = "id"` to `USERNAME_FIELD_ID = "login_id"`.

## Usage

Run the bot:
```bash
python main.py
```

- A Chrome window will open.
- The bot will attempt to log in.
- If a CAPTCHA appears, solve it manually in the browser window; the bot will wait.
- Once logged in, it will start monitoring the target courses.

## Troubleshooting
- **ChromeDriver Error**: The `webdriver-manager` library should handle this automatically. If not, download the ChromeDriver matching your Chrome version manually.
- **Login Fails**: Check `bot.py` selectors. The login page structure might have changed.
- **Bot crashes immediately**: Check `bot.log` for details.

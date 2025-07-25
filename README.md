# FuOverflow Downloader
vibe coded script but fast af, imagine using selenium

## Requirements

- Python 3.11+
- Dependencies in `requirements.txt`

## Installation

1. Clone this repository:
```bash
git clone https://github.com/rumi-chan/fuovfl-dl.git
cd fuovfl-dl
```
2. Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate  # Linux/Mac
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration
Edit the configuration values at the top of `script.py`:
```py
# --- CONFIGURATION: PLEASE EDIT THESE VALUES ---
FORUM_PAGE_URL = "https://fuoverflow.com/threads/your-thread-here/"
USER_COOKIE = "your_cookie_here"
BASE_URL = "https://fuoverflow.com"
MAX_CONCURRENT_DOWNLOADS = 50
# --- END OF CONFIGURATION ---
```

## How to Get Your Cookie
- Log in to the forum in your browser
- Open Developer Tools (F12 or Ctrl Shift I/J)
- Go to Network tab and refresh page
- Click on any request to the forum domain
- Find "Cookie" in Request Headers
- Copy the entire cookie string

## Usage
```bash
python script.py
```

## Disclaimer
This script is intended for personal use and convenience. Please be responsible and respect the website's terms of service. Do not use this script to overload a website's servers. The user is responsible for ensuring they have the right to download and store the content.

## License
This project is licensed under the MIT License. Use at your own risk.
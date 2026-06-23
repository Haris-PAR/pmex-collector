import json
from pathlib import Path
import cloudscraper

URL = "https://dportal.pmex.com.pk/MWatchNew/Home/GetJSONObject"

HEADERS = {
	"Accept": "application/json, text/javascript, */*; q=0.01",
	"Content-Type": "application/json; charset=UTF-8",
	"Origin": "https://dportal.pmex.com.pk",
	"Referer": "https://dportal.pmex.com.pk/mwatchnew",
	"X-Requested-With": "XMLHttpRequest",
}

def fetch_pmex(status: str = "Active") -> dict:
	"""
	Fetch data from PMEX using cloudscraper to automatically handle 
	Cloudflare anti-bot checks and cookie rotation.
	"""
	scraper = cloudscraper.create_scraper(
		browser={
			'browser': 'chrome',
			'platform': 'windows',
			'desktop': True
		}
	)
	
	payload = {"status": status}
	
	# First visit the main page to establish the Cloudflare clearance session
	try:
		scraper.get("https://dportal.pmex.com.pk/mwatchnew", timeout=15)
	except Exception as e:
		print("Warning: Initial page load failed, trying API anyway...", e)
	
	# Then post to the API using the established session
	resp = scraper.post(URL, headers=HEADERS, json=payload, timeout=20)
	resp.raise_for_status()
	
	return resp.json()

def main() -> None:
	try:
		data = fetch_pmex("Active")
	except Exception as exc:
		print("Request failed:", exc)
		return

	out_path = Path("pmex_response.json")
	out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
	print(f"Saved response to {out_path} (Items found: {len(data)})")

if __name__ == "__main__":
	main()

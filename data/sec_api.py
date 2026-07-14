import requests

# 1. Setup your SEC-mandated User-Agent
# Replace this with your actual name/company and email
HEADERS = {"User-Agent": "Jane Doe (jane.doe@example.com)"}


def get_latest_10k_html(cik: str, output_filename: str = "latest_10K.html"):
    # Ensure CIK is exactly 10 digits for the submissions API (pad with leading zeros)
    cik_padded = cik.zfill(10)

    # 2. Query the submissions endpoint
    print(f"Fetching metadata for CIK: {cik_padded}...")
    submissions_url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"

    response = requests.get(submissions_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return

    data = response.json()
    recent_filings = data["filings"]["recent"]

    # 3. Find the most recent 10-K in the filings list
    accession_number = None
    primary_document = None

    for i, form_type in enumerate(recent_filings["form"]):
        if form_type == "10-K":
            accession_number = recent_filings["accessionNumber"][i]
            primary_document = recent_filings["primaryDocument"][i]
            break

    if not accession_number:
        print("No 10-K found for this company.")
        return

    # 4. Construct the URL to the raw HTML file
    # Rule: The Archives URL strips leading zeros from the CIK and hyphens from the Accession Number
    cik_stripped = str(int(cik))
    accession_stripped = accession_number.replace("-", "")

    html_url = f"https://www.sec.gov/Archives/edgar/data/{cik_stripped}/{accession_stripped}/{primary_document}"
    print(f"Found 10-K HTML at: {html_url}")

    # 5. Download the HTML file
    print("Downloading HTML file...")
    html_response = requests.get(html_url, headers=HEADERS)

    if html_response.status_code == 200:
        with open(output_filename, "wb") as f:
            f.write(html_response.content)
        print(f"Success! Saved as {output_filename}")
    else:
        print("Failed to download the HTML file.")


# --- Execute the script ---
# Example: Apple Inc. (CIK: 0000320193)
# Note: You can pass it with or without the leading zeros; the script handles it.
APPLE_CIK = "320193"

get_latest_10k_html(APPLE_CIK, "apple_10k.html")

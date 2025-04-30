from playwright.sync_api import sync_playwright

def scrape_and_save_upwork(job_url, output_file):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Turn headless off so you can watch it
        page = browser.new_page()

        page.goto(job_url, timeout=60000)  # wait up to 60 seconds

        # NEW: wait for something that only appears on a real job page
        page.wait_for_selector('h1', timeout=60000)  # Upwork job titles are inside <h1> tags

        html = page.content()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"Saved page to {output_file}")


# Example usage
scrape_and_save_upwork(
    'https://www.upwork.com/jobs/~021916900997976461491',
    'upwork_job.html'
)

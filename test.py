from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import os

def scrape_tbsnews_multiple_days(start_date, days_to_scrape=10):
    print("🔄 Starting TBS News archive scrape...\n")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(current_dir, "chromedriver.exe")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    wait = WebDriverWait(driver, 20)

    base_url = "https://www.tbsnews.net/archive"
    collected_links = set()

    try:
        for i in range(days_to_scrape):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            print(f"\n📅 Scraping articles for {date}...")

            driver.get(base_url)
            wait.until(EC.presence_of_element_located((By.NAME, "archive_date")))

            # Input date into the archive calendar
            date_input = driver.find_element(By.NAME, "archive_date")
            driver.execute_script("arguments[0].value = arguments[1]", date_input, date)
            date_input.submit()

            # Wait for articles to load
            time.sleep(3)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h4.title a")))

            # Parse page with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "html.parser")
            links = [a['href'] for a in soup.select("h4.title a") if a['href'].startswith("https://www.tbsnews.net")]
            collected_links.update(links)
            print(f"📰 Found {len(links)} articles for {date}")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        driver.quit()
        print("\n✅ Browser closed.")

    # Save to file
    output_file = os.path.join(current_dir, "tbsnews_archive_links.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(collected_links)))

    print(f"\n✅ Total unique articles collected: {len(collected_links)}")
    print(f"✅ Links saved to: {output_file}")

if __name__ == "__main__":
    scrape_tbsnews_multiple_days(datetime.strptime("2025-06-20", "%Y-%m-%d"), days_to_scrape=10)
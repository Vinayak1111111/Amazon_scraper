import random
import requests
from bs4 import BeautifulSoup
import csv
import time

# List of sample User-Agent headers to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'
]

# Function to fetch product details from each product block
def fetch_product_details(product):
    # Extract product name
    product_name = product.find('span', class_='a-text-normal').text if product.find('span', class_='a-text-normal') else 'N/A'

    # Check if the product is out of stock or has invalid data
    if "Check each product page for other buying options." in product_name:
        return None  # Skip this product

    # Extract price
    price = product.find('span', class_='a-price-whole').text if product.find('span', class_='a-price-whole') else 'N/A'

    # Extract rating
    rating = product.find('span', class_='a-icon-alt').text if product.find('span', class_='a-icon-alt') else 'N/A'

    # Extract seller name (if available)
    seller = 'N/A'
    seller_tag = product.find('span', class_='a-size-small')
    if seller_tag and 'sold by' in seller_tag.text.lower():
        seller = seller_tag.text.split(' ')[-1]

    # Detect stock status: Check if the product is out of stock
    out_of_stock_tag = product.find('span', class_='a-declarative')
    if out_of_stock_tag:
        out_of_stock_text = out_of_stock_tag.text.lower()
        if "out of stock" in out_of_stock_text or "currently unavailable" in out_of_stock_text:
            return None  # Skip this product if it is out of stock

    # Return a tuple with product details
    return (product_name, price, rating, seller)

# Main function to scrape Amazon
def scrape_amazon(url):
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }

    # Send the GET request to Amazon
    response = requests.get(url, headers=headers)

    # If request was successful (HTTP status code 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extracting all product items from the search page
        products = soup.find_all('div', class_='s-main-slot')[0].find_all('div', class_='s-result-item')
        
        product_details = []

        # Loop through each product and extract details
        for product in products:
            details = fetch_product_details(product)
            if details and details != ('N/A', 'N/A', 'N/A', 'N/A'):  # Ensure product is valid and not all N/A
                product_details.append(details)
        
        # Writing the scraped data to a CSV file
        with open('amazon_products.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Product Name', 'Price', 'Rating', 'Seller Name'])
            writer.writerows(product_details)
        
        print(f"Data scraped and saved to 'amazon_products.csv' successfully!")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

if __name__ == "__main__":
    url = "https://www.amazon.in/s?rh=n%3A6612025031&fs=true&ref=lp_6612025031_sar"
    scrape_amazon(url)

    time.sleep(3)

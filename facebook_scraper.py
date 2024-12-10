import random
import time
import pymongo
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import webbrowser
import threading

app = Flask(__name__)

def open_url():
    # Delay for 2 seconds before opening the URL
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

# MongoDB Setup
def get_mongo_client():
    # Connect to the MongoDB client (local)
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["facebook_data"]  # Access 'facebook_data' database
    return db["posts"]  # Return the 'posts' collection

# Function to initialize the browser
def initialize_browser():
    print("Initializing browser...")
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument(r"user-data-dir=C:\\Users\\skand\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")
    options.add_argument("--incognito")
    driver = webdriver.Chrome(service=service, options=options)
    print("Browser initialized successfully.")
    return driver

# Function to perform Facebook login
def facebook_login(driver, email, password):
    try:
        print("Logging in to Facebook...")
        driver.get("https://www.facebook.com")
        time.sleep(random.uniform(5, 8))  # Wait for the page to load

        # Find input fields
        email_input = driver.find_element(By.ID, "email")  # Email field
        password_input = driver.find_element(By.ID, "pass")  # Password field
        email_input.send_keys(email)
        time.sleep(random.uniform(3, 5))
        password_input.send_keys(password)
        time.sleep(random.uniform(3, 5))

        # Click the login button
        login_button = driver.find_element(By.NAME, "login")
        login_button.click()
        time.sleep(random.uniform(8, 12))
        print("Login attempt completed.")
    except NoSuchElementException as e:
        print(f"Element not found during login: {e}")
    except Exception as e:
        print(f"Unexpected error during login: {e}")

# Function to calculate max posts based on start and end date
def calculate_max_posts(start_date, end_date):
    # Convert the string dates to datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Calculate the number of days between start and end date
    days_diff = (end_date - start_date).days

    # Map days difference to a range of posts (2 to 25 posts for simplicity)
    if days_diff < 1:
        return 2  # If the date range is less than 1 day, return 2 posts
    elif days_diff <= 7:
        return random.randint(4, 8)  # For a week, return between 4 and 8 posts
    elif days_diff <= 14:
        return random.randint(8, 12)  # For 2 weeks, return between 8 and 12 posts
    elif days_diff <= 30:
        return random.randint(15, 18)  # For 1 month, return between 15 and 18 posts
    else:
        return random.randint(20, 25)  # For longer periods, return between 20 and 25 posts

# Function to scroll the page and scrape posts
def scroll_and_scrape(driver, max_posts):
    captions = []
    image_urls = []
    comments = []
    reactions = []
    post_dates = []

    while len(captions) < max_posts:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)

        posts = driver.find_elements(By.CSS_SELECTOR, "div.xu06os2.x1ok221b")
        for post in posts:
            if len(captions) >= max_posts:
                break

            # Scraping captions
        # Scraping captions
        try:
            caption = post.find_element(By.CSS_SELECTOR, "div.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x1vvkbs.x126k92a > div[dir='auto']").text
            captions.append(caption)
        except Exception:
            pass  # Skip if caption is not found


            # Scraping image URLs using BeautifulSoup
            try:
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                post_divs = soup.find_all("div", class_="x6s0dn4 x1jx94hy x78zum5 xdt5ytf x6ikm8r x10wlt62 x1n2onr6 xh8yej3")
                for post_div in post_divs:
                    image = post_div.find("img")
                    image_url = image['src'] if image else None
                    if image_url:
                        image_urls.append(image_url)
            except Exception:
                image_urls.append(None)

            # Scraping comments
            try:
                soup = BeautifulSoup(post.get_attribute('outerHTML'), 'html.parser')
                comment_elements = soup.find_all("div", class_="x1lliihq xjkvuk6 x1iorvi4")
                post_comments = [comment.text for comment in comment_elements if comment.text]
                comments.append(post_comments)
            except Exception:
                comments.append([])

            # Scraping reactions
            try:
                reaction_elements = post.find_elements(By.CSS_SELECTOR, "div[aria-label]")
                post_reactions = {}

                for element in reaction_elements:
                    aria_label = element.get_attribute("aria-label")
                    if aria_label:
                        parts = aria_label.split(":")
                        if len(parts) == 2:
                            reaction_type = parts[0].strip()
                            count = parts[1].strip().split()[0]
                            if reaction_type in ["Love", "Like", "Care", "Haha", "Sad", "Angry", "Wow"]:
                                post_reactions[reaction_type] = int(count)

                reactions.append(post_reactions)
            except Exception:
                reactions.append({})

            # Scraping dates
            try:
                date_element = post.find_element(By.CSS_SELECTOR, "span.x4k7w5x.x1h91t0o.x1h9r5lt")
                date_text = date_element.text.strip().lower()
                post_dates.append(date_text)
            except Exception:
                post_dates.append(None)

    # Insert data into MongoDB
    collection = get_mongo_client()

    # Creating a list of posts to insert into MongoDB
    posts_data = []
    for idx in range(len(captions)):
        post = {
            "_id": f"post {idx + 1}",  # Set the custom _id as 'post 1', 'post 2', etc.
            "caption": captions[idx],
            "image_url": image_urls[idx] if idx < len(image_urls) else None,
            "comments": comments[idx] if idx < len(comments) else [],
            "reactions": reactions[idx] if idx < len(reactions) else {},
            "date": post_dates[idx] if idx < len(post_dates) else None
        }
        posts_data.append(post)

    # Inserting all posts into MongoDB
    collection.insert_many(posts_data)
    print(f"{len(posts_data)} posts inserted into MongoDB successfully.")

    return posts_data

# Route for the main page
@app.route("/")
def index():
    return render_template("index.html")

# Route for starting the scraping
@app.route("/start_scraping", methods=["POST"])
def start_scraping():
    # Get user inputs from the form
    url = request.form.get("url")
    start_date = request.form.get("start_date")  # Start date from form
    end_date = request.form.get("end_date")  # End date from form

    # Calculate the max posts based on start and end date
    max_posts = calculate_max_posts(start_date, end_date)

    # Initialize the browser
    driver = initialize_browser()

    # Perform Facebook login
    email = "your_facebook_email@test.com"  # Replace with your Facebook email
    password = "your_facebook_password"  # Replace with your Facebook password
    facebook_login(driver, email, password)

    # Open the Facebook page
    driver.get(url)
    time.sleep(20)

    # Scrape the data
    posts_data = scroll_and_scrape(driver, max_posts)

    # Display the scraped data in the terminal
    for idx, post in enumerate(posts_data):
        print(f"Post {idx + 1}:")
        print(f"  Caption: {post['caption']}")
        print(f"  Image URL: {post['image_url']}")
        print(f"  Comments: {', '.join(post['comments']) if post['comments'] else 'None'}")
        print(f"  Reactions: {', '.join([f'{k}: {v}' for k, v in post['reactions'].items()]) if post['reactions'] else 'None'}")
        print(f"  Date: {post['date']}")

    # Close the browser
    driver.quit()

    return "Scraping started! Check the terminal for results."



if __name__ == "__main__":
    threading.Thread(target=open_url).start()
    app.run(debug=True, use_reloader=False)
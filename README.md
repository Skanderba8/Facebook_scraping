# Facebook Scraping Application  

This application scrapes posts from a Facebook page based on a user-defined date range. It uses Selenium for web automation, BeautifulSoup for HTML parsing, and MongoDB for storing scraped data.  

## Prerequisites  

1. **Python**: Ensure Python 3.7 or higher is installed.  
2. **MongoDB**: Install and set up MongoDB on your system.  
3. **Chrome and ChromeDriver**: Install the Google Chrome browser and download ChromeDriver compatible with your browser version.  
4. **Python Packages**: Install the required packages using `pip`:  

   ```bash
   pip install flask selenium webdriver-manager beautifulsoup4 pymongo
Project Structure
facebook_scraper.py: The main script containing the scraping logic and Flask app.
templates/index.html: The front-end interface to input parameters for scraping.
Usage
Clone or Download the Repository:

bash
Copy code
git clone https://github.com/your-repo/facebook-scraping-app.git
cd facebook-scraping-app
Edit Login Credentials:

Open the facebook_scraper.py file and replace the following lines with your Facebook credentials:

python
Copy code
email = "your_facebook_email@test.com"  # Replace with your Facebook email
password = "your_facebook_password"  # Replace with your Facebook password
Run the Application:

Start the Flask application:

bash
Copy code
python facebook_scraper.py
After running the script, a browser tab will open automatically with the application interface.

Use the Web Interface:

Enter the URL of the Facebook page you want to scrape.
Define the start and end dates for posts to scrape.
Click the button to start scraping.
View Results:

Scraped data is stored in your MongoDB instance under the database facebook_data and collection posts.

You can also view the scraped data in the terminal where the app is running.

Notes
MongoDB Configuration:
Ensure your MongoDB server is running locally on localhost:27017. Update the connection string in facebook_scraper.py if needed.

ChromeDriver Path:
The application uses webdriver-manager to automatically handle the ChromeDriver setup. Ensure your Chrome browser is updated.

Troubleshooting:
If the script fails during login or scraping, ensure:

Your credentials are correct.
Two-factor authentication is disabled for the Facebook account.
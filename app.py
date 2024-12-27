from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.twitter_scraper
trends_collection = db.trends

print("Current working directory:", os.getcwd())

def fetch_trending_topics():
    driver = None
    print("Starting trend fetch process...")
    print("Using credentials - Username:", os.getenv('TWITTER_USERNAME'))
    
    # ScraperAPI configuration
    scraper_api_key = "25c5cf9837ab5214a4f8ad9c06fdfb58"
    proxy_host = "proxy-server.scraperapi.com"
    proxy_port = "8001"
    proxy_username = "scraperapi"
    proxy_password = scraper_api_key
    
    # Configure proxy URL
    proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
    print("Configuring ScraperAPI proxy...")
    
    chrome_options = Options()
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--user-data-dir=./chrome-profile')
    chrome_options.add_argument(f'--proxy-server={proxy_host}:{proxy_port}')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-insecure-localhost')
    
    # Add proxy authentication extension
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        }
    }
    """
    
    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: %s
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {urls: ["<all_urls>"]},
        ['blocking']
    );
    """ % (proxy_host, proxy_port, proxy_username, proxy_password)
    
    # Create proxy auth extension
    import zipfile
    plugin_file = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    chrome_options.add_extension(plugin_file)

    try:
        # Start Chrome using run_chrome.bat
        print("Starting Chrome with remote debugging...")
        subprocess.Popen(['run_chrome.bat'], shell=True)
        time.sleep(5)  # Wait for Chrome to start
        
        # Test proxy connection and get IP
        try:
            session = requests.Session()
            
            print("Verifying proxy connection...")
            # Use ScraperAPI to verify IP
            try:
                verify_url = f"http://api.scraperapi.com?api_key={scraper_api_key}&url=http://httpbin.org/ip"
                ip_response = requests.get(verify_url, timeout=10)
                ip_data = ip_response.json()
                ip_address = ip_data['origin']
                print(f"Got IP from ScraperAPI: {ip_address}")
            except Exception as e:
                print(f"ScraperAPI IP verification failed: {str(e)}")
                # Fallback to direct IP check
                ip_response = session.get(
                    'https://api.ipify.org?format=json',
                    timeout=10,
                    auth=(proxy_username, proxy_password)
                )
                ip_address = ip_response.json()['ip']
            
            print(f"Using IP: {ip_address}")
        except Exception as e:
            print(f"Proxy verification failed: {str(e)}")
            print("Response details:", getattr(e, 'response', 'No response'))
            ip_address = "proxy verification failed"
        
        # Get the debugging URL
        try:
            response = requests.get('http://localhost:9222/json/version')
            websocket_debugger_url = response.json()['webSocketDebuggerUrl']
            print(f"Connected to Chrome debugger: {websocket_debugger_url}")
        except Exception as e:
            print(f"Failed to get debugger URL: {str(e)}")
            raise

        chromedriver_path = os.path.join(os.getcwd(), "chromedriver-win64", "chromedriver.exe")
        print(f"Using ChromeDriver from: {chromedriver_path}")
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)
        print("Chrome driver initialized successfully")
        
        # First go to login page
        # print("Accessing X.com login page...")
        # driver.get("https://x.com/i/flow/login")
        # time.sleep(3)
        
        # # Click sign in button if present
        # try:
        #     sign_in_button = wait.until(EC.element_to_be_clickable((
        #         By.CSS_SELECTOR, "#react-root > div > div > div.css-175oi2r.r-1f2l425.r-13qz1uu.r-417010 > main > div > div > div.css-175oi2r.r-tv6buo.r-791edh.r-1euycsn > div.css-175oi2r.r-1777fci.r-nsbfu8.r-1qmwkkh > div > div.css-175oi2r > div.css-175oi2r.r-2o02ov > a > div > span > span"
        #     )))
        #     print("Found sign in button")
        #     sign_in_button.click()
        #     time.sleep(2)
        # except Exception as e:
        #     print(f"Sign in button not found: {str(e)}")
        #     print("Proceeding with direct login")
        
        # print("Looking for username input...")
        # username_input = wait.until(EC.element_to_be_clickable((
        #     By.CSS_SELECTOR, "#layers > div:nth-child(2) > div > div > div > div > div > div.css-175oi2r.r-1ny4l3l.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv.r-1awozwy > div.css-175oi2r.r-1wbh5a2.r-htvplk.r-1udh08x.r-1867qdf.r-kwpbio.r-rsyp9y.r-1pjcn9w.r-1279nm1 > div > div > div.css-175oi2r.r-1ny4l3l.r-6koalj.r-16y2uox.r-kemksi.r-1wbh5a2 > div.css-175oi2r.r-16y2uox.r-1wbh5a2.r-f8sm7e.r-13qz1uu.r-1ye8kvj > div > div > div > div.css-175oi2r.r-1mmae3n.r-1e084wi.r-13qz1uu > label > div > div.css-175oi2r.r-18u37iz.r-16y2uox.r-1wbh5a2.r-1wzrnnt.r-1udh08x.r-xd6kpl.r-is05cd.r-ttdzmv > div > input"
        # )))
        # print("Found username input")
        # username_input.clear()
        # username_input.send_keys(os.getenv('TWITTER_USERNAME'))
        # print("Entered username")
        
        # # Click the Next button after entering username
        # next_button = wait.until(EC.element_to_be_clickable((
        #     By.CSS_SELECTOR, "#layers > div:nth-child(2) > div > div > div > div > div > div.css-175oi2r.r-1ny4l3l.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv.r-1awozwy > div.css-175oi2r.r-1wbh5a2.r-htvplk.r-1udh08x.r-1867qdf.r-kwpbio.r-rsyp9y.r-1pjcn9w.r-1279nm1 > div > div > div.css-175oi2r.r-1ny4l3l.r-6koalj.r-16y2uox.r-kemksi.r-1wbh5a2 > div.css-175oi2r.r-16y2uox.r-1wbh5a2.r-f8sm7e.r-13qz1uu.r-1ye8kvj > div > div > div > button:nth-child(6) > div"
        # )))
        # next_button.click()
        # print("Clicked Next button")
        # time.sleep(2)
        
        # print("Looking for password input...")
        # password_input = wait.until(EC.element_to_be_clickable((
        #     By.CSS_SELECTOR, "#layers > div:nth-child(2) > div > div > div > div > div > div.css-175oi2r.r-1ny4l3l.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv.r-1awozwy > div.css-175oi2r.r-1wbh5a2.r-htvplk.r-1udh08x.r-1867qdf.r-kwpbio.r-rsyp9y.r-1pjcn9w.r-1279nm1 > div > div > div.css-175oi2r.r-1ny4l3l.r-6koalj.r-16y2uox.r-kemksi.r-1wbh5a2 > div.css-175oi2r.r-16y2uox.r-1wbh5a2.r-f8sm7e.r-13qz1uu.r-1ye8kvj > div.css-175oi2r.r-16y2uox.r-1wbh5a2.r-1dqxon3 > div > div > div.css-175oi2r.r-1e084wi.r-13qz1uu > div > label > div > div.css-175oi2r.r-18u37iz.r-16y2uox.r-1wbh5a2.r-1wzrnnt.r-1udh08x.r-xd6kpl.r-is05cd.r-ttdzmv > div.css-146c3p1.r-bcqeeo.r-1ttztb7.r-qvutc0.r-37j5jr.r-135wba7.r-16dba41.r-1awozwy.r-6koalj.r-1inkyih.r-13qz1uu > input"
        # )))
        # print("Found password input")
        # password_input.clear()
        # password_input.send_keys(os.getenv('TWITTER_PASSWORD'))
        # print("Entered password")
        
        # # Click the Login button after entering password
        # login_button = wait.until(EC.element_to_be_clickable((
        #     By.CSS_SELECTOR, "#layers > div:nth-child(2) > div > div > div > div > div > div.css-175oi2r.r-1ny4l3l.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv.r-1awozwy > div.css-175oi2r.r-1wbh5a2.r-htvplk.r-1udh08x.r-1867qdf.r-kwpbio.r-rsyp9y.r-1pjcn9w.r-1279nm1 > div > div > div.css-175oi2r.r-1ny4l3l.r-6koalj.r-16y2uox.r-kemksi.r-1wbh5a2 > div.css-175oi2r.r-16y2uox.r-1wbh5a2.r-f8sm7e.r-13qz1uu.r-1ye8kvj > div.css-175oi2r.r-1f0wa7y > div > div.css-175oi2r > div > div > button > div"
        # )))
        # login_button.click()
        # print("Submitted login form")
        # time.sleep(5)
        
        # # Check for various error conditions
        # try:
        #     error_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='error']")
        #     if error_elements:
        #         error_text = error_elements[0].text
        #         print(f"Login error detected: {error_text}")
        #         return {"error": f"Login failed: {error_text}"}
        # except Exception as e:
        #     print(f"Error checking for login errors: {str(e)}")
        
        # # Verify we're logged in before proceeding
        # if "i/flow/login" in driver.current_url:
        #     print("Still on login page - authentication failed")
        #     return {"error": "Login failed - please check credentials"}
        
        # Instead of starting a new Chrome instance, just open a new tab
        print("Opening X.com in a new tab...")
        # Switch to the new tab after opening it
        current_handles = driver.window_handles
        driver.execute_script("window.open('https://x.com/home', '_blank');")
        time.sleep(1)
        
        # Switch to the newly opened tab
        new_handles = driver.window_handles
        new_tab = [handle for handle in new_handles if handle not in current_handles][0]
        driver.switch_to.window(new_tab)
        
        # Remove or comment out the Chrome startup code
        # print("Starting Chrome with remote debugging...")
        # subprocess.Popen(['run_chrome.bat'], shell=True)
        # time.sleep(5)  # Wait for Chrome to start
        
        # Wait for trends to load with new XPath
        print("Waiting for trends to load...")
        # First wait for the trends section to be visible
        trends_section = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, "#react-root > div > div > div.css-175oi2r.r-1f2l425.r-13qz1uu.r-417010.r-18u37iz > main > div > div > div > div.css-175oi2r.r-aqfbo4.r-10f7w94.r-1hycxz > div > div.css-175oi2r.r-1hycxz.r-gtdqiz > div > div > div > div:nth-child(4) > section > div > div"
        )))
        print("Found trends container")

        # Get all trend elements within the container
        trends = wait.until(EC.presence_of_all_elements_located((
            By.CSS_SELECTOR, "div.css-146c3p1.r-bcqeeo.r-1ttztb7.r-qvutc0.r-37j5jr.r-a023e6.r-rjixqe.r-b88u0q.r-1bymd8e"
        )))
        print(f"Found {len(trends)} potential trends")

        # Clean up trend names
        trend_names = []
        for trend in trends:
            try:
                name = trend.text.strip()
                if name and not name.startswith("Show more"):  # Exclude "Show more" button
                    trend_names.append(name)
                if len(trend_names) >= 5:
                    break
            except Exception as e:
                print(f"Error processing trend: {str(e)}")
                continue

        print(f"Found {len(trend_names)} trends: {trend_names}")
        if len(trend_names) == 0:
            raise Exception("No trends found")

        # Create record
        unique_id = str(uuid.uuid4())
        end_time = datetime.utcnow()

        trend_record = {
            "unique_id": unique_id,
            "nameoftrend1": trend_names[0] if len(trend_names) > 0 else "",
            "nameoftrend2": trend_names[1] if len(trend_names) > 1 else "",
            "nameoftrend3": trend_names[2] if len(trend_names) > 2 else "", 
            "nameoftrend4": trend_names[3] if len(trend_names) > 3 else "",
            "nameoftrend5": trend_names[4] if len(trend_names) > 4 else "",
            "date_time": end_time,
            "ip_address": ip_address
        }

        # Save to MongoDB
        trends_collection.insert_one(trend_record)
        print("Successfully saved trends to database")
        return trend_record

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        if driver:
            print("Taking error screenshot...")
            driver.save_screenshot("error.png")
            with open("error_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Page source saved to error_page.html")
            print(f"Current URL: {driver.current_url}")
            
            # Additional debugging information
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text
                print(f"Page text content: {body_text[:500]}...")  # Print first 500 chars
                
                # Try to find any trends-related elements
                sidebar = driver.find_elements(By.CSS_SELECTOR, "[data-testid='sidebarColumn']")
                if sidebar:
                    print("Found sidebar, checking contents...")
                    print(sidebar[0].text[:500])
                
                # Check for specific error conditions
                if "login" in driver.current_url.lower():
                    print("Login failed - still on login page")
                    return {"error": "Login failed - please check credentials"}
                elif "account/access" in driver.current_url.lower():
                    print("Account verification required")
                    return {"error": "Account verification required"}
                elif "logout" in driver.current_url.lower():
                    print("Session expired - user logged out")
                    return {"error": "Session expired - please try again"}
            except:
                pass
        return {"error": str(e)}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script', methods=['POST'])
def run_script():
    trend_data = fetch_trending_topics()
    if "error" in trend_data:
        return jsonify({
            "success": False,
            "error": trend_data["error"],
            "timestamp": datetime.utcnow().isoformat()
        })
    # Convert ObjectId to string before returning
    json_data = trend_data.copy()
    if '_id' in json_data:
        json_data['_id'] = str(json_data['_id'])
    return jsonify({"success": True, "data": json_data})

if __name__ == '__main__':
    app.run(debug=True)

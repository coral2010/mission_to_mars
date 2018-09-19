
from bs4 import BeautifulSoup
from splinter import Browser
import time
import tweepy
import json
import pandas as pd

# Initialize browser
def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

# scrape websites for mars info
def scrape():

    print('COMMENCING DATA SCRAPE FOR MARS')
    print("-----------------------------------------------")

# dictionary to hold scraped data
    mars_data = {}

# scrape for recent mars news
    browser = init_browser()    
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    news_title = soup.find("div", class_="content_title").text
    news_p = soup.find("div", class_="rollover_description_inner").text

    mars_data['news_title'] = news_title
    mars_data['news_p'] = news_p

    print("OBTAINED RECENT NEWS")

# scrape for freatured image
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    time.sleep(5)
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(5)
    browser.click_link_by_partial_text('more info')
    time.sleep(5)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    results = soup.find('article')
    extension = results.find('figure', 'lede').a['href']
    link = "https://www.jpl.nasa.gov"
    featured_image_url = link + extension

    mars_data['featured_image_url'] = featured_image_url

    print("OBTAINED FEATURED IMAGE")

# scrape for recent weather news from twitter account
    from config import consumer_key, consumer_secret, access_token, access_token_secret

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

    target_user = "MarsWxReport"
    tweet_list = []
    public_tweets = api.user_timeline(target_user)

    for tweet in public_tweets:
        text = tweet["text"]
        tweet_list.append(text)
        print(tweet_list)

    mars_weather = tweet_list[0]
    mars_data['mars_weather'] = mars_weather

    print("OBTAINED WEATHER TWEET")

# scrape for facts about mars
    url = "https://space-facts.com/mars/"
    tables = pd.read_html(url)
    df = tables[0]
    df.columns = ['Description', 'Value']
    df.set_index('Description', inplace=True)

    html_table = df.to_html()
    html_table.replace('\n', '')
    df.to_html('table.html')

    mars_data['fact_table'] = 'table.html'

    print("OBTAINED FACT TABLE")

# scrape hemisphere image urls
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    articles = soup.find_all('div', class_="item")

    image_dict = []

    for article in articles:
    #find title
        description = article.find('div', class_='description')
    
        title = description.find('h3').text
        title = title.replace(' Enhanced', '')
    
        #find link to visit next page
        end_link = description.find('a')['href']
        image_link = 'https://astrogeology.usgs.gov' + end_link
        browser.visit(image_link)
        html = browser.html
        soup = BeautifulSoup(html, "html.parser")
    
        #find image url
        container = soup.find('div', class_='container')
        end_url = container.find('img', class_='wide-image')['src']
        image_url = 'https://astrogeology.usgs.gov' + end_url
    
        #create dictionary
        image_dict.append({'title': title, 'img_url': image_url})

    mars_data['hemisphere_image_urls'] = image_dict

    print("OBTAINED HEMISPHERE IMAGE URLS")
    print("-----------------------------------------------")
    print("SCRAPING COMPLETED")
    print("-----------------------------------------------")
    print(mars_data)

    return mars_data


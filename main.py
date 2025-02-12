from scraper import Scraper
from looper import Looper

#scrape time!
scraper = Scraper()

links = scraper.GetLinks()
titles = scraper.GetTitles()
dates = scraper.GetDates()
platforms = scraper.GetPlatforms()

prices = scraper.GetPrices()
prices_before = prices.get('prices_before')
prices_after = prices.get('prices_final')
discounts = prices.get('discounts')

#loop time!
looper = Looper()
looper.loop(links, titles, dates, platforms, prices_before, prices_after, discounts)

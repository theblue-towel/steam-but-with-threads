from submitter import Submitter
import threading

class Looper:

    def __init__(self):
        self.threads = []


    def loop(self, links, titles, dates, platforms, prices_before, prices_after, discounts):

        def SubmitOne(link, title, date, platform_condensed, price_before, price_after, discount):

            submitter = Submitter()
            submitter.SubmitForm(link, title, date, platform_condensed, price_before, price_after, discount)

        for i in range(50):

            platform_raw = platforms[i]
            platform_condensed = ', '.join(platform_raw)

            t = threading.Thread(target=SubmitOne, args=[links[i], titles[i], dates[i], platform_condensed, prices_before[i], prices_after[i], discounts[i]])
            t.start()
            self.threads.append(t)

        for thread in self.threads:
            thread.join()
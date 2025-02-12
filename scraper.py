from bs4 import BeautifulSoup
import requests
import time

class Scraper:

    def __init__(self):

        print('initializing')
        start = time.time()

        response = requests.get('https://store.steampowered.com/search/?filter=topsellers')
        data = response.text
        self.soup = BeautifulSoup(data, 'html.parser')

        end = time.time()
        print('initialized in', (end - start) * 10**3, 'ms')

    def GetPrices(self):

        print('Retrieving prices')
        start = time.time()

        maybe_empties_alpha = self.soup.find_all(name='div', class_='col search_discount_and_price responsive_secondrow')
        maybe_empties = [item.getText().replace('\n', '').strip() for item in maybe_empties_alpha]
        
        #clear steam -40 -38 mistake

        maybe_empties_beta = []
        discount_indexes = []

        for i in range(len(maybe_empties)):
            current = maybe_empties[i]
            if current == '':
                maybe_empties_beta.append('NA')
            elif len(current) > 8:
                discount_indexes.append(i)
                maybe_empties_beta.append(maybe_empties[i])
            else:
                maybe_empties_beta.append(maybe_empties[i])

        #before cleaned
        discounts = [maybe_empties_beta[i] for i in discount_indexes] 
        print(f'# of discounts found: {len(discounts)}/{len(maybe_empties_beta)} games')
        non_discounts = []
        non_discount_indexes = []
        for iter in range(len(maybe_empties_beta)):
            if maybe_empties_beta[iter] not in discounts:
                non_discounts.append(maybe_empties_beta[iter])
                non_discount_indexes.append(iter)

        #---------------------------------------Final variable--------------------------------------------
        discounts_final = [0 for i in maybe_empties_beta]
        prices_before = [0 for i in maybe_empties_beta]
        prices_final = [0 for i in maybe_empties_beta]
        master_disc_controller = 0
        #---------------------------------------Final variable--------------------------------------------

        for i in range(len(discounts)):
            listed = list(discounts[i])
            listdisc = []
            percents = 0
            list_final = []

            for ij in range(8):
                listdisc.append(listed[ij])
            for value in listdisc:
                if value == '%':
                    percents += 1
            if percents >= 2:
                #remove first 4 char
                iter = 4
                while iter < len(listed):
                    list_final.append(listed[iter])
                    iter += 1
                
                listedConcatentated = ''.join(list_final)
                discounts[i] = listedConcatentated
            

        for i in discounts:
            if len(i) <= 11:
                #separate into 2 part

                listed_short = list(i)
                to_len = len(listed_short)
                disc_percent_uncomp = []
                price_point_uncomp = []
                short_pos = 1
                run = True

                while run:
                    current_short = listed_short[short_pos]
                    if current_short != '%':
                        disc_percent_uncomp.append(current_short)
                        short_pos += 1
                    else:
                        short_pos += 2
                        run = False

                while short_pos < to_len:
                    price_point_uncomp.append(listed_short[short_pos])
                    short_pos += 1

                disc_decimal = round(float(''.join(disc_percent_uncomp)) * 0.01, 2)
                price_point = round(float(''.join(price_point_uncomp)), 2)
                off = int(round((1 - disc_decimal) * 100, 2))
                apply = price_point * disc_decimal
                final_price = round(price_point - apply, 2)

                prices_before[discount_indexes[master_disc_controller]] = price_point
                prices_final[discount_indexes[master_disc_controller]] = final_price
                discounts_final[discount_indexes[master_disc_controller]] = f'-{off}%'

            else:

                #get percent
                listed_non_steam_problem = list(i)
                to_len = len(listed_non_steam_problem)
                reg_disc_discount_percent_uncomp = []
                reg_disc_price_point_before_uncomp = []
                reg_disc_price_point_after_uncomp = []
                short_pos = 1
                run = True

                while run:
                    current_v = listed_non_steam_problem[short_pos]
                    if current_v != '%':
                        reg_disc_discount_percent_uncomp.append(current_v)
                        short_pos += 1
                    else:
                        run = False
                        short_pos += 2

                #get first price
                run = True

                while run:
                    current_v = listed_non_steam_problem[short_pos]
                    if current_v != '$':
                        reg_disc_price_point_before_uncomp.append(current_v)
                        short_pos += 1
                    else:
                        run = False
                        short_pos += 1

                #get final price
                while short_pos < to_len:
                    reg_disc_price_point_after_uncomp.append(listed_non_steam_problem[short_pos])
                    short_pos += 1

                reg_disc_before_comp = ''.join(reg_disc_price_point_before_uncomp)
                reg_disc_after_comp = ''.join(reg_disc_price_point_after_uncomp)
                reg_disc_percent_comp = ''.join(reg_disc_discount_percent_uncomp)

                prices_before[discount_indexes[master_disc_controller]] = reg_disc_before_comp
                prices_final[discount_indexes[master_disc_controller]] = reg_disc_after_comp
                discounts_final[discount_indexes[master_disc_controller]] = f'-{reg_disc_percent_comp}%'

            master_disc_controller += 1 

        for I in range(len(discounts_final)):
            if discounts_final[I] == 0:
                discounts_final[I] = 'NA'

        #slot the other stuff back in

        for i in range(len(non_discounts)):
            current_non = non_discounts[i]
            current_non_index = non_discount_indexes[i]

            prices_before[current_non_index] = current_non
            prices_final[current_non_index] = current_non

        fat_result = {
            'prices_before': prices_before,
            'prices_final': prices_final,
            'discounts': discounts_final,
        }

        end = time.time()
        print('successfully retrieved prices in', (end - start) * 10**3, 'ms')

        return fat_result

    def GetLinks(self):

        print('Retrieving links')
        start = time.time()

        large_div = self.soup.find(name='div', id='search_resultsRows')
        a_raw = large_div.find_all(name='a')
        links = [link.get('href') for link in a_raw]

        end = time.time()
        print('successfully retrieved links in', (end - start) * 10**3, 'ms')

        return links

    def GetTitles(self):

        print('Retrieving titles')
        start = time.time()

        titles_raw = self.soup.find_all(name='span', class_='title')
        titles = [title.getText() for title in titles_raw]

        end = time.time()
        print('successfully retrieved titles in ', (end - start) * 10**3, 'ms')

        return titles
    
    def GetDates(self):

        print('Retrieving dates')
        start = time.time()

        dates_raw = self.soup.find_all(name='div', class_='col search_released responsive_secondrow')
        dates = [date.getText().replace('\n', '').strip() for date in dates_raw]

        end = time.time()
        print('successfully retrieved dates in', (end - start) * 10**3, 'ms')

        return dates

    def GetPlatforms(self):

        #this took like 4 hours

        print('Retrieving supported platforms')
        start = time.time()

        secondary_div = self.soup.find_all(name='div', class_='col search_name ellipsis')
        platform_divs = [div.find(name='div') for div in secondary_div]
        # print(platform_divs)
        large_spans = []

        #loop through platform divs
        for current in range(len(platform_divs)):
            current_game = platform_divs[current]
            spans = current_game.find_all(name='span')
            large_spans.append(spans)

        whole_platforms = []
        for div in large_spans:
            #print(div)
            platforms = []
            for span in div:
                klass = span.get('class')
                platforms.append(klass)

            for i in platforms:
                for j in i:
                    if j == 'platform_img' or j == 'includes_games_results':
                        i.remove(j)
            whole_platforms.append(platforms)

        formatted = []
        for o in whole_platforms:
            temp = []
            for t in o:
                for u in t:
                    temp.append(u)
            for item in temp:
                if item == 'group_separator':
                    temp.remove(item)
            formatted.append(temp)
        
        end = time.time()
        print('successfully retrieved supported platforms in', (end - start) * 10**3, 'ms')

        return formatted
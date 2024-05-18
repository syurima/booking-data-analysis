import atexit
import datetime
import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd
import requests

def create_url(city: str, date: datetime.datetime, n_of_adults = 1, n_of_children = 0, currency='EUR') -> str:
    date_format = '%Y-%m-%d'
    url = 'https://www.booking.com/searchresults.pl.html?'
    url += '&'.join([
        f'ss={city}',
        f'checkin={date.strftime(date_format)}',
        f'checkout={(date + datetime.timedelta(days=1)).strftime(date_format)}',
        f'group_adults={n_of_adults}',
        f'group_children={n_of_children}'
        f'no_rooms=1',
        f'selected_currency={currency}',
        'lang=en'
    ])
    #EXTRA UNUSED TAGS
    '''
    #f'dest_id=-2140479',
    #'efdco=1',
    #'&label=gen173nr-1FCAEoggI46AdIHlgEaLYBiAEBmAEeuAEXyAEM2AEB6AEB-AECiAIBqAIDuALqvu-xBsACAdICJGY2MjhkMzMxLWFkNWYtNDkwZS05OGRiLTkzM2ZkNDc2NDNhM9gCBeACAQ',
    #'aid=304142',
    #'lang=pl',
    #'sb=1',
    #'src_elem=sb',
    #'src=index',
    #'dest_type=city',
    #'ac_position=2',
    #'ac_click_type=b',
    #'ac_langcode=pl',
    #'ac_suggestion_list_length=5',
    #'search_selected=true',
    #'search_pageview_id=de888f7554e4090d',
    #'ac_meta=GhBkZTg4OGY3NTU0ZTQwOTBkIAIoATICcGw6AUFAAEoAUAA%3D'
    '''
    print(url)
    return url

def generate_params(city: str, date_min_offset: int, date_max_offset: int, max_adults: int, max_children: int) -> dict:
    
    date = datetime.datetime.today() + datetime.timedelta(days=random.randint(date_min_offset, date_max_offset))
    n_of_adults = random.randint(1, max_adults)
    if random.random(): n_of_children = random.randint(0, max_children)
    else: n_of_children = 0

    params = {
        'city': city,
        'date': date,
        'adults': n_of_adults,
        'children': n_of_children
    }
    return params

class page_loaded:
    def __call__(self, driver):
        document_ready = driver.execute_script("return document.readyState;") == "complete"
        jquery_ready = driver.execute_script("return jQuery.active == 0;")
        print(f"document ready: [({type(document_ready).__name__}){document_ready}]")
        print(f"jquery  ready: [({type(jquery_ready).__name__}){jquery_ready}]")
        return document_ready and jquery_ready

def scroll(driver) -> None:
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(random.uniform(1.4, 5.8))

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
 
def get_soup_selenium(url):
    driver = webdriver.Chrome()
    atexit.register(driver.quit)
    driver.maximize_window()
    
    driver.get(url)
    WebDriverWait(driver, 20, 1).until(page_loaded(), f"Page could not load in {20} s.!")
    scroll(driver)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup

# html bez selenium (nie scrolluje)
def get_soup(url):
    
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'Accept-Language': 'en-US, en;q=0.5'
    }
    html = requests.get(url, headers=headers)

    '''
    filename = f'html_{datetime.datetime.now()}.txt'.replace(':', '-')
    file = open(filename, 'w+', encoding='utf-8')
    file.write(html.text)
    '''

    # soupify
    soup = BeautifulSoup(html.content, 'html.parser')
    return soup

def get_data(soup, date=None, n_of_adults=1, n_of_children=0):
    # find all hotel elements in the html
    hotels = soup.findAll('div', {'data-testid': 'property-card'})

    #file = open('hotel_test.txt', 'w+', encoding='utf-8')
    #file.write(hotels[1].prettify())

    hotels_data = []
    # loop over the hotel elements and extract data
    for hotel in hotels:
        # hotel info
        name = hotel.find('div', {'data-testid': 'title'}).text.strip()
        stars = len(hotel.find_all('span', {'class': 'fcd9eec8fb d31eda6efc c25361c37f'}))

        # price
        price = hotel.find('span', {'data-testid': 'price-and-discounted-price'}).text.replace(',', '').split()[1]

        # rating
        rating = hotel.find('div', {'class': 'a3b8729ab1 d86cee9b25'}).text.split()[-1]
        n_of_opinions = hotel.find('div', {'class': 'abf093bdfe f45d8e4c32 d935416c47'}).text.replace(',', '').split()[0]

        # distance to city center
        location = hotel.find('span', {'data-testid': 'distance'}).text
        distance = float(location.split()[0])
        if 'km' in location: distance *= 1000

        # room info
        room_type = soup.find('h4', class_='abf093bdfe e8f7c070a7').text.strip()
        #amenities = [item.text.strip() for item in soup.find_all('li', class_='a6a38de85e')]
        free_cancellation = soup.find('div', class_='abf093bdfe d068504c75') != None
        breakfast = soup.find('span', class_='a19404c4d7') != None

        # Append hotes_data with info about hotel
        hotels_data.append({
            'name': name,
            'stars': stars,
            'price': float(price),
            'rating': float(rating),
            'opinions': int(n_of_opinions),
            'distance_from_centre': distance,
            #'room_type': room_type,
            'free_cancellation': free_cancellation,
            'breakfast': breakfast
        })

    return hotels_data

def save_data(data):
    #turn into pd dataframe
    df = pd.DataFrame(data)
    print(df.head(5))

    #save as csv
    df.to_csv(f'data/data_{datetime.datetime.now()}.csv'.replace(':', '.'), header=True, index=False, encoding='utf-8')


def main():
    #url = create_url(city='Amsterdam', date = None)
    params = generate_params(city='Amsterdam', date_min_offset=30, date_max_offset=400, max_adults=4, max_children=2)

    url = create_url(params['city'], params['date'], params['adults'], params['children'])
    soup = get_soup_selenium(url)
    #soup = get_soup(url)

    hotels_data = get_data(soup)
    for log in hotels_data:
        log.update(params)
        #print(log)
    print(hotels_data[1])
    save_data(hotels_data)
    

if __name__ == "__main__":
    main()
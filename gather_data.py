import atexit
import datetime
import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
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

def generate_params(city: str, date_start: datetime.date, date_max_offset: int, max_adults: int, max_children: int) -> dict:
    
    date = date_start + datetime.timedelta(days=random.randint(0,date_max_offset))
    n_of_adults = random.randint(1, max_adults)
    n_of_children = random.randint(0, max_children)

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
        #print(f"document ready: [({type(document_ready).__name__}){document_ready}]")
        #print(f"jquery  ready: [({type(jquery_ready).__name__}){jquery_ready}]")
        return document_ready and jquery_ready

def scroll(driver) -> None:
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(random.uniform(1.5, 3.4))

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            driver.execute_script(f"scrollBy(0,{random.randint(-600, -500)});")
            time.sleep(random.uniform(1.5, 3.6))
            break

        last_height = new_height
 
def get_soup(driver, url):
    driver.get(url)
    WebDriverWait(driver, 15, 1).until(page_loaded(), f"Page could not load in {15} s.!")
    while True:
        scroll(driver)

        # load more
        time.sleep(random.uniform(1.7, 4))
        try:
            #load_more_button = driver.find_element(By.XPATH, "//button[.//span[text()='Load more results']]")
            load_more_button = driver.find_element(By.XPATH, "//button[@class='a83ed08757 c21c56c305 bf0537ecb5 f671049264 deab83296e af7297d90d']//span[text()='Load more results']")
            if not load_more_button: print('no button')
            else:
                load_more_button.click()
        except Exception as e:
            #print(f"Load more button could not be clicked: {e}")
            break

        time.sleep(random.uniform(1.5, 4))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
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
        price_elem = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
        price = price_elem.text.replace(',', '').split()[1] if price_elem else None

        # rating
        rating_elem = hotel.find('div', {'class': 'a3b8729ab1 d86cee9b25'})
        rating = rating_elem.text.split()[-1] if rating_elem else None
        opinions_elem = hotel.find('div', {'class': 'abf093bdfe f45d8e4c32 d935416c47'})
        n_of_opinions = opinions_elem.text.replace(',', '').split()[0] if opinions_elem else None

        # distance to city center
        location_elem = hotel.find('span', {'data-testid': 'distance'})
        distance = float(location_elem.text.split()[0]) if location_elem else None
        if 'km' in location_elem.text: distance *= 1000

        # room info
        room_type = soup.find('h4', class_='abf093bdfe e8f7c070a7').text.strip()
        #amenities = [item.text.strip() for item in soup.find_all('li', class_='a6a38de85e')]
        free_cancellation = soup.find('div', class_='abf093bdfe d068504c75') != None
        breakfast = soup.find('span', class_='a19404c4d7') != None

        # Append hotes_data with info about hotel
        hotels_data.append({
            'name': name,
            'stars': stars,
            'price': price,
            'price_per_person': round(float(price)/(n_of_adults + n_of_children), 2) if price else None,
            'rating': rating,
            'opinions': n_of_opinions,
            'distance_from_centre': distance,
            #'room_type': room_type,
            'free_cancellation': free_cancellation,
            'breakfast': breakfast
        })

    return hotels_data

def save_data(data, params):
    #turn into pd dataframe
    df = pd.DataFrame(data)
    #print(df.head(5))

    #save as csv
    df.to_csv(f'data/{params['city']}_{params['date'].strftime('%Y-%m-%d')}_a{params['adults']}_c{params['children']}.csv', header=True, index=False, encoding='utf-8')

def run_iteration(driver, url = None):
    # generate random url
    if not url: 
        params = generate_params(city='Amsterdam', date_start=datetime.date.today() + datetime.timedelta(days=30), date_max_offset=400, max_adults=9, max_children=0)
        url = create_url(params['city'], params['date'], params['adults'], params['children'])

    soup = get_soup(driver, url)

    hotels_data = get_data(soup, n_of_adults = params['adults'], n_of_children = params['children'])
    for log in hotels_data:
        log.update(params)

    #print(hotels_data[1])
    save_data(hotels_data, params)
        

def main():
    # set up driver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(), options=chrome_options)
    atexit.register(driver.quit)
    driver.maximize_window()

    n = 20
    for _ in range(n):
        run_iteration(driver)
        time.sleep(random.uniform(1.5, 4))

    driver.quit()

if __name__ == "__main__":
    main()
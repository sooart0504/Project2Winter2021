#################################
##### Name: Soo Ji Choi
##### Uniqname: soojc
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
import time
import secrets

base_url = 'https://www.nps.gov'
end_url = '/index.htm'
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}

def load_cache():
    '''Open cache file and load JSON into CACHE_DICT.
    If cache file doesn't exist, create a new cache dict.

    Parameters
    -------------------
    None

    Returns
    -------------------
    cache dict
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache_dict = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    '''Saves the current state of the cache

    Parameters
    -------------------
    cache_dict: dict

    Returns
    -------------------
    none
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache_dict)
    cache_file.write(contents_to_write)
    cache_file.close()


class NationalSite: #STEP 2
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.

    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''

    def __init__(self, name, address, zipcode, phone, category="No Category"):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        """Returns a string representation of name, category, address and zip
        per the following format:
        The format is <name> (<category>): <address> <zip>

        Example: Isle Royale (National Park): Houghton, MI 49931
        """

        return f"{self.name} ({self.category}): {self.address} {self.zipcode}"


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    state_dict = {}

    request_url = base_url + end_url

    #-----every request to website should be cached (key is url?)-----

    # WITHOUT CACHING:
    # response = requests.get(request_url)
    # soup = BeautifulSoup(response.text, 'html.parser')

    # WITH CACHING:
    if request_url in CACHE_DICT.keys():
        soup = BeautifulSoup(CACHE_DICT[request_url], 'html.parser')
        print("Using Cache...")
    else:
        CACHE_DICT[request_url] = requests.get(request_url).text
        soup = BeautifulSoup(CACHE_DICT[request_url], 'html.parser')
        save_cache(CACHE_DICT)
        print("Fetching...")
    # ----------------------------------------------------------------


    #find - find one item
    #find_all - find all items
    searching_div_class = soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch', role='menu')
    searching_li = searching_div_class.find_all('li', recursive=False) #recursive - don't look inside of the ...?

    #print(searching_ul)

    # sample list:
    # <a href="/state/al/index.htm" id="anch_10">Alabama</a>
    for each_state in searching_li:
        state_info = each_state.find('a')
        state_name = state_info.text.lower()
        state_path = state_info['href'] #url /state/al/index.htm

        state_url = base_url + state_path

        state_dict[state_name] = state_url #Creating a key value pair

    return state_dict



def get_site_instance(site_url): #STEP 2
    '''Make an instances from a national site URL.

    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov

    Returns
    -------
    instance
        a national site instance
    '''
    #-----every request to website should be cached (key is url?)-----

    if site_url in CACHE_DICT.keys():
        soup = BeautifulSoup(CACHE_DICT[site_url], 'html.parser')
        print("Using Cache...")
    else:
        CACHE_DICT[site_url] = requests.get(site_url).text
        soup = BeautifulSoup(CACHE_DICT[site_url], 'html.parser')
        save_cache(CACHE_DICT)
        print("Fetching...")

    # response = requests.get(site_url) #-----every request to website should be cached-----
    # soup = BeautifulSoup(response.text, 'html.parser')

    # <div class="Hero-titleContainer clearfix">
    hero_container = soup.find('div', class_='Hero-titleContainer clearfix')
    park_name = hero_container.find('a').text # <a href="/isro/" class="Hero-title " id="anch_10">Isle Royale</a>

    designation_container = hero_container.find('div', class_='Hero-designationContainer') # <div class="Hero-designationContainer">
    park_category = designation_container.find('span', class_='Hero-designation').text # <span class="Hero-designation">National Park</span>


    #there may be no address (implement try/except)
    address_container = soup.find('div', class_='vcard') # <div class="vcard">
    park_city = address_container.find('span', itemprop='addressLocality').text # <span itemprop="addressLocality">Houghton</span>
    park_state = address_container.find('span', itemprop='addressRegion', class_='region').text # <span itemprop="addressRegion" class="region">MI</span>

    park_address = f"{park_city}, {park_state}"

    park_zipcode = address_container.find('span', itemprop='postalCode', class_='postal-code').text.strip() # <span itemprop="postalCode" class="postal-code">49931     </span>
    park_phone = address_container.find('span', itemprop='telephone', class_='tel').text.strip() # <span itemprop="telephone" class="tel"> (906) 482-0984</span>

    #park_name
    #park_category
    #park_address
    #park_zipcode
    #park_phone
    site_instance = NationalSite(park_name, park_address, park_zipcode, park_phone, park_category)

    return site_instance



def get_sites_for_state(state_url): #STEP 3
    '''Make a list of national site instances from a state URL.

    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov

    Returns
    -------
    list
        a list of national site instances
    '''
    sites_list = []

    # STEP 3 FLOW:
    # ----------------------------------------------
    # Within main():
    # 1. User inputs state name
    # 2. search for state URL from state_dict within build_state_url_dict()
    # 3. use the key (state URL) as the parameter for get_sites_for_state()

    # Within get_sites_for_state():
    # 4. Locate all sites URLs within html of state site
    # 5. for every site in sites URLs, create NationalSite instances &
    #    append "[number] <name> (<type>):<address> <zip code>" into sites_list
    #    example: [1] Isle Royale (National Park): Houghton, MI 49931
    # 6. return sites_list

    if state_url in CACHE_DICT.keys():
        soup = BeautifulSoup(CACHE_DICT[state_url], 'html.parser')
        print("Using Cache...")
    else:
        CACHE_DICT[state_url] = requests.get(state_url).text
        soup = BeautifulSoup(CACHE_DICT[state_url], 'html.parser')
        save_cache(CACHE_DICT)
        print("Fetching...")

    # state_response = requests.get(state_url) #-----every request to website should be cached-----
    # state_soup = BeautifulSoup(state_response.text, 'html.parser')

    site_h3 = soup.find_all('h3')
    for each_site_url in site_h3:
        if each_site_url.find('a') is not None:
            site_path = each_site_url.find('a')['href']

            site_url = base_url + site_path

            sites_list.append(get_site_instance(site_url))

    return sites_list

def get_nearby_places(site_object): #STEP 4 (need to create a new function for this step)
    '''Obtain API data from MapQuest API.

    Parameters
    ----------
    site_object: object
        an instance of a national site

    Returns
    -------
    dict
        a converted API return from MapQuest API


    Constructing Search URL for MapQuest API:
    ---------------------------
    key: API key from secrets.py
    origin: Zip code of a national site (Use NationalSite instance attribute.)
    radius: Distance from the origin to search is 10 miles.
    maxMatches: The number of results returned in the response is 10.
    ambiguities: “ignore”
    outFormat: “json”
    '''

    API_BASE_URL = "http://www.mapquestapi.com/search/v2/radius?"
    key = f"key={secrets.API_KEY}"
    origin = f"origin={site_object.zipcode}"
    radius = "radius=10"
    maxMatches = "maxMatches=10"
    ambiguities = "ambiguities=ignore"
    outFormat = "outFormat=json"

    request_json = f"{API_BASE_URL}{key}&{origin}&{radius}&{maxMatches}&{ambiguities}&{outFormat}"

    if request_json in CACHE_DICT.keys():
        retrieved_json = CACHE_DICT[request_json]
        print("Using Cache...")
        #retrieved_json = json.loads(retrieved_json)

        return retrieved_json
    else:
        CACHE_DICT[request_json] = requests.get(request_json).json()
        save_cache(CACHE_DICT)
        retrieved_json = CACHE_DICT[request_json]
        print("Fetching...")
        #retrieved_json = json.loads(retrieved_json)

        return retrieved_json

def main():
    # print(build_state_url_dict())

    # test_park = 'https://www.nps.gov/isro/index.htm'
    # test = get_site_instance(test_park)
    # print(test.info())

    # STEP 3 FLOW:
    # ----------------------------------------------
    # Within main():
    # 1. User inputs state name
    # 2. search for state URL from state_dict within build_state_url_dict()
    # 3. use the key (state URL) as the parameter for get_sites_for_state()

    # Within get_sites_for_state():
    # 4. Locate all sites URLs within html of state site
    # 5. for every site in sites URLs, create NationalSite instances &
    #    append "[number] <name> (<type>):<address> <zip code>" into sites_list
    #    example: [1] Isle Royale (National Park): Houghton, MI 49931
    # 6. return sites_list

    INPUT_QUERY = input('Enter a state name (e.g. Michigan, michigan) or "exit": ').lower()
    state_url_dict = build_state_url_dict()

    while True:
        if INPUT_QUERY in state_url_dict.keys():
            state_url = state_url_dict[INPUT_QUERY]
            site_instance_list = get_sites_for_state(state_url)

            query_num = 0
            print("--------------------------------------------")
            print(f"List of National sites in {INPUT_QUERY.title()}")
            print("--------------------------------------------")

            input_state_name = INPUT_QUERY

            for each_instance in site_instance_list:
                query_num += 1
                print(f"[{query_num}] {each_instance.name} ({each_instance.category}): {each_instance.address} {each_instance.zipcode}")

            INPUT_QUERY = input('Choose the number for detailed search or "exit" or "back": ')


            if INPUT_QUERY.isnumeric():
                site_num = int(INPUT_QUERY)

                try:
                    print("--------------------------------------------")
                    print(f"Places near {site_instance_list[site_num-1].name}") #try&except for INPUT_QUERY
                    print("--------------------------------------------")
                    places_near_site = get_nearby_places(site_instance_list[int(INPUT_QUERY)-1])
                    nearby_results = places_near_site["searchResults"]

                    for each_place in nearby_results:
                    # ----------- if/else statement for blank string (assign variables to each key) ---------
                        if each_place['fields']['group_sic_code_name_ext'] != "":
                            place_category = each_place['fields']['group_sic_code_name_ext']
                        else:
                            place_category = "No category"

                        if each_place['fields']['address'] != "":
                            place_address = each_place['fields']['address']
                        else:
                            place_address = "No address"

                        if each_place['fields']['city'] != "":
                            place_city = each_place['fields']['city']
                        else:
                            place_city = "No city"

                        print(f"- {each_place['name']} ({place_category}): {place_address}, {place_city}")

                    INPUT_QUERY = input('Enter another state name (e.g. Michigan, michigan), "exit" or "back": ').lower()

                except:
                    print("[ERROR] Enter a proper number")
                    INPUT_QUERY = input('Choose the number for detailed search or "exit" or "back": ').lower()

            elif INPUT_QUERY == "back":
                INPUT_QUERY = input('Enter a state name (e.g. Michigan, michigan) or "exit": ').lower()


        elif INPUT_QUERY == "exit":
            print("Bye!")
            print("----- END OF PROGRAM -----")
            break

        elif INPUT_QUERY == "back":
            INPUT_QUERY = input('Enter a state name (e.g. Michigan, michigan) or "exit": ').lower()
            # query_num = 0
            # print("--------------------------------------------")
            # print(f"List of National sites in {input_state_name.title()}")
            # print("--------------------------------------------")

            # for each_instance in site_instance_list:
            #     query_num += 1
            #     print(f"[{query_num}] {each_instance.name} ({each_instance.category}): {each_instance.address} {each_instance.zipcode}")

            # INPUT_QUERY = input('Choose the number for detailed search or "exit" or "back": ')

        else:
            print("[ERROR] Enter a proper state name")
            INPUT_QUERY = input('Enter a state name (e.g. Michigan, michigan) or "exit": ').lower()





if __name__ == "__main__":
    CACHE_DICT = load_cache()
    main()
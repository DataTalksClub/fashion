import requests
from bs4 import BeautifulSoup
import bs4
import re


def init_attribute_holders(attributes_for_selection, attribute_values):
    for attribute in attributes_for_selection:
        attribute_values[attribute] = []


def update_attributes(soup_element, attributes_for_selection, attribute_values):
    soup_attribute_name = soup_element.find('span')['title']
    for attribute_name in attributes_for_selection:
        if attribute_name == soup_attribute_name:
            soup_value = soup_element.find('div')['title']
            attribute_values[soup_attribute_name].append(soup_value)
            return soup_attribute_name


def fill_in_not_updated_attributes(not_updated_attributes, attribute_values):
    for attribute in not_updated_attributes:
        attribute_values[attribute].append(None)


def scrap_item_page(link, attributes_for_selection, attribute_values):
    page = requests.get(link)
    # check the page status; if success then it should be 200
    if page.status_code != 200:
        return
    soup = BeautifulSoup(page.content, 'html.parser')
    # this selector gets the tag where the main image is located
    main_image_element = soup.select_one('img#J-dcv-image-trigger')
    #!TODO not all descriptions have an image, some have only video. The logic need to be updated for that case
    attribute_values["image_link"].append(main_image_element["data-src"])
    # the following element contains product details; 0 element is the list of details
    details = soup.select_one('div.do-entry-list')
    not_updates_attributes = set(attributes_for_selection)
    for detail in details:
        # There are strings in the details list too, this condition prevents them from scrapping
        if isinstance(detail, bs4.element.Tag):
            updated_attribute = update_attributes(detail, attributes_for_selection, attribute_values)
            if updated_attribute in not_updates_attributes:
                not_updates_attributes.remove(updated_attribute)
    # to make the length of a list of values the same for a postprocessing step, not present values are updated as well
    fill_in_not_updated_attributes(not_updates_attributes, attribute_values)
    print(attribute_values)
    return


def scrap_seller_page(init_link, attributes_for_selection, attribute_values):
    page = requests.get(init_link)
    seller_main_page = re.search("https://[\w\.]+", init_link).group(0)
    # check the page status; if success then it should be 200
    if page.status_code != 200:
        return
    soup = BeautifulSoup(page.content, 'html.parser')
    product_list = soup.select_one('div.component-product-list')
    items = product_list.select('div.product-info')
    item_links = []
    for item in items:
        item_links.append(seller_main_page + item.select_one('a.title-link')['href'])
    for item_link in item_links:
        scrap_item_page(item_link, attributes_for_selection, attribute_values)


def scrap_pages(init_link):
    attributes_for_selection = ["Style", "Collar", "Season", "Fabric type",
                                "Product Name", "Gender", "Product Type", "Item Type"]
    # to prevent the image link to be scrapped as a text attribute, an additional holder for the link is created
    all_attributes = attributes_for_selection + ["image_link"]
    attribute_values = {}
    init_attribute_holders(all_attributes, attribute_values)
    scrap_seller_page(init_link, attributes_for_selection, attribute_values)
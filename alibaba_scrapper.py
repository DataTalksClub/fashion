import requests
from bs4 import BeautifulSoup
import bs4
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By


def init_attribute_holders(attributes_for_selection, attribute_values):
    for attribute in attributes_for_selection:
        attribute_values[attribute] = []


def update_attribute(web_element, attributes_for_selection, attribute_values):
    try:
        scrapper_attribute_name = web_element.find_element_by_tag_name('span').get_attribute('title')
        for attribute_name in attributes_for_selection:
            if attribute_name == scrapper_attribute_name:
                scrapper_attribute_value = web_element.find_element_by_tag_name('div').text
                attribute_values[scrapper_attribute_name].append(scrapper_attribute_value)
                return scrapper_attribute_name
    except:
        return None

def fill_in_not_updated_attributes(not_updated_attributes, attribute_values):
    for attribute in not_updated_attributes:
        attribute_values[attribute].append(None)


def scrap_item(link, driver, attributes_for_selection, attribute_values):
    driver.get(link)
    # check the page status; if success then it should be 200
    # TODO modify for scrapper
    #if page.status_code != 200:
    #    return
    # this selector gets the tag where the main image is located
    main_image_element = driver.find_element_by_id('J-dcv-image-trigger')
    # to check if the image element exists'(some pages have video instead)
    if main_image_element is None:
        return
    attribute_values["image_link"].append(main_image_element.get_attribute("data-src"))
    # the following element contains product details; 0 element is the list of details
    details = driver.find_element_by_css_selector('div.do-entry-list').find_elements_by_css_selector('dl.do-entry-item')
    not_updates_attributes = set(attributes_for_selection)
    for detail in details:
        # There are strings in the details list too, this condition prevents them from scrapping
        updated_attribute = update_attribute(detail, attributes_for_selection, attribute_values)
        if updated_attribute is None:
            continue
        if updated_attribute in not_updates_attributes:
            not_updates_attributes.remove(updated_attribute)
    # to make the length of a list of values the same for a postprocessing step, not present values are updated as well
    fill_in_not_updated_attributes(not_updates_attributes, attribute_values)
    return


def get_next_page_link(driver, current_page_number):
    pagination_list = driver.find_element_by_css_selector('div.next-pagination-list')
    displayed_pages = pagination_list.find_elements_by_css_selector('a.next-pagination-item')
    for page in displayed_pages:
        # the next page number must be higher than the current.
        # since page number are shown in ascending order, this check will allow to select only the next page
        if int(page.text) > current_page_number:
            next_page_link = page.get_attribute("href")
            return next_page_link


def scrap_items(driver, attributes_for_selection, attribute_values):
    product_list = driver.find_element_by_css_selector('div.component-product-list')
    items = product_list.find_elements_by_css_selector('div.product-info')
    item_links = []
    for item in items:
        item_links.append(item.find_element_by_css_selector('a.title-link').get_attribute('href'))
    for item_link in item_links:
        scrap_item(item_link, driver, attributes_for_selection, attribute_values)


def scrap_items_page(item_list_link, current_page_number, attributes_for_selection, attribute_values):
    driver = webdriver.Chrome()
    driver.get(item_list_link)
    # TODO check how to do it in Selenium
    # check the page status; if success then it should be 200
    #if page.status_code != 200:
    #    return
    next_page_link = get_next_page_link(driver, current_page_number)
    scrap_items(driver, attributes_for_selection, attribute_values)
    return next_page_link


def scrap_init_seller_page(init_link, attributes_for_selection, attribute_values):
    # check the page status; if success then it should be 200
    #TODO check how to do it in Selenium
    #if page.status_code != 200:
    #    return

    # the initial page is the first page with items
    next_seller_page = init_link
    # initial page is 1
    current_page_number = 1
    while next_seller_page is not None and current_page_number < 3:
        next_seller_page = scrap_items_page(next_seller_page, current_page_number,
                                            attributes_for_selection, attribute_values)
        current_page_number += 1


def scrap_sellers(seller_links, tags_for_selection):
    # to prevent the image link to be scrapped as a text attribute, an additional holder for the link is created
    all_attributes = tags_for_selection + ["image_link"]
    attribute_values = {}
    init_attribute_holders(all_attributes, attribute_values)
    # tags for selection doesn't include image. Image is processed separately
    for link in seller_links:
        scrap_init_seller_page(link, tags_for_selection, attribute_values)
    print(pd.DataFrame.from_dict(attribute_values))
    pd.DataFrame.from_dict(attribute_values).to_csv("test_data.csv")
    return pd.DataFrame.from_dict(attribute_values)
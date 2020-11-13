from alibaba_scrapper import scrap_sellers
import config

def main():
    sellers_to_scrap = config.sellers_to_scrap
    tags_for_selection = config.tags_for_selection
    scrap_sellers(sellers_to_scrap, tags_for_selection)


if __name__ == '__main__':
    main()

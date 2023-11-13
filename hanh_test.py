from src.crawler.scholar import GgscholarCrawler
from src.utils.selenium_utils import get_driver
from src.config.config import settings
if __name__ == "__main__":
    tester = GgscholarCrawler(settings, "expert_alpha2", "./")
    tester.crawl_all_authors()
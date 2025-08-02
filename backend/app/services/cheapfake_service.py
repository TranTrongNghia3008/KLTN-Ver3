import os
import time
import re
import base64
import random
import concurrent.futures
from PIL import Image
from io import BytesIO
from fastapi import HTTPException
from app.config import *
from app.utils.chrome_driver import *
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


def search_relevant_links_cheapfake(query):
    driver = get_chrome_driver()
    driver.get(f'https://www.bing.com/search?q={query}')
    time.sleep(random.uniform(1, 10))

    articles = driver.find_elements(By.CSS_SELECTOR, "#b_results li.b_algo")
    link_articles = []

    for article in articles[:MINIMUM_K]:
        try:
            title_element = article.find_element(By.TAG_NAME, "h2").find_element(By.TAG_NAME, "a")
            title = title_element.text
            link = title_element.get_attribute('href')
            link_articles.append({'title': title, 'link': link})
        except Exception as e:
            print("Lỗi khi trích xuất bài viết:", e)
    driver.quit()
    return link_articles


def try_dismiss_popups(driver):
    try:
        popup_texts = ["Accept Cookies", "Accept All Cookies", "I Accept", "Agree", "Continue"]
        for text in popup_texts:
            try:
                btn = driver.find_element(
                    By.XPATH,
                    f"//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
                )
                btn.click()
                break
            except NoSuchElementException:
                continue
            except ElementClickInterceptedException:
                continue

        close_candidates = driver.find_elements(By.XPATH, "//button[contains(@class, 'close') or contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'close')]")
        for btn in close_candidates:
            try:
                btn.click()
                break
            except Exception:
                continue
    except Exception as e:
        print(f"Popup error: {e}")


def process_article_link(article, max_retries=5):
    article_crawl = {
        "title": article['title'],
        "src": article['link'],
        "pdf_path": ""
    }

    wait_time = 10
    for attempt in range(1, max_retries + 1):
        driver = get_chrome_driver()
        try:
            print(f"Attempt {attempt}: {article['link']}")
            driver.get(article['link'])
            time.sleep(wait_time)
            try_dismiss_popups(driver)

            safe_title = re.sub(r'[^a-zA-Z0-9\s]', '', article['title']).replace(" ", "_")
            pdf_path = f"./storage/pdf_files/{safe_title}.pdf"
            print_options = {'path': pdf_path, 'printBackground': True}
            pdf = driver.execute_cdp_cmd("Page.printToPDF", print_options)

            with open(pdf_path, 'wb') as f:
                f.write(base64.b64decode(pdf['data']))
            article_crawl["pdf_path"] = pdf_path
            break
        except Exception as e:
            print(f"Failed attempt {attempt}: {e}")
            wait_time += 5
        finally:
            driver.quit()

    return article_crawl


def crawl_articles(caption):
    try:
        link_articles = search_relevant_links_cheapfake(caption)
    except Exception as e:
        print(f"Search error: {e}")
        link_articles = []

    # Ưu tiên link có chứa caption
    # url_articles = [{'title': "Article from caption", 'link': f"https://www.bing.com/search?q={caption}"}]
    url_articles = link_articles
    url_articles = url_articles[:MINIMUM_K]

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(process_article_link, url_articles))

    return results


async def cheapfake_label_service(image_file, caption: str):
    try:
        image = Image.open(BytesIO(await image_file.read()))

        # Crawl
        crawled_articles = crawl_articles(caption)
        uploaded_files = []
        for art in crawled_articles:
            if os.path.exists(art["pdf_path"]):
                uploaded_files.append(client_gemini.files.upload(file=art["pdf_path"]))

        prompt = (
            """A news is considered fake if the tag of the article is one of these: 'Research In Progress', 'True', 'Mostly True', """
            "'Mixture', 'Mostly False', 'False', 'Unproven', 'Unfounded', 'Outdated', 'Miscaptioned', 'Correct Attribution', "
            "'Misattributed', 'Legend', 'Scam', 'Legit', 'Labeled Satire', 'Originated as Satire', 'Recall', 'Lost Legend', 'Fake'. "
            "Return 1 if the news in file is fake or the caption not included in the content, else return 0."
        )

        response = client_gemini.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, caption, prompt] + uploaded_files,
            config={
                'response_mime_type': 'text/x.enum',
                'response_schema': {
                    "type": "STRING",
                    "enum": ["0", "1"],
                },
                'safety_settings': [
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE,
                    ),
                ]
            }
        )


        label = response.text if response and hasattr(response, 'text') and response.text else "No response"

        # Trích title và src → trả về dưới dạng title + link
        url_articles = [{"title": art["title"], "link": art["src"]} for art in crawled_articles]

        return {"label": label, "url_articles": url_articles}

    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

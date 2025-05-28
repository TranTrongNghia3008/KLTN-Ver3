from app.services.search_informations import *
from app.config import *
from app.models.schemas import *
from app.utils.chrome_driver import *

def search_who(caption: str):
  driver = get_chrome_driver()

  prompt = f'https://www.who.int/home/search-results?indexCatalogue=genericsearchindex1&searchQuery={caption}&wordsMode=AnyWord'
  # print(prompt)
  driver.get(prompt)
  time.sleep(random.uniform(3, 3))

  articles = driver.find_elements(By.CLASS_NAME, 'sf-list-vertical__item')

  link_articles = []
  for article in articles[:MINIMUM_K]:
      title = article.find_element(By.CLASS_NAME, 'trimmed').text
      date = article.find_element(By.CLASS_NAME, 'sf-list-vertical__date').text
      if (date):
        date = date + ' - '
      title = date + title
      link = article.find_element(By.TAG_NAME, 'a').get_attribute('href')
      link_articles.append({
          'title': title,
          'link': link,
      })
  driver.quit()
  return link_articles

def pdf_to_text(url: str):
  pdf_text = ""
  if url:
      print(url)
      try:
          response = requests.get(url)
          if response.status_code == 200:
              filename = os.path.basename(url)
              filepath = f"/content/{filename}"
              with open(filepath, "wb") as file:
                  file.write(response.content)

          pdf_content = []
          with open(filepath, "rb") as pdf_file:
              reader = PdfReader(pdf_file)
              for page in reader.pages:
                  pdf_content.append(page.extract_text())
          pdf_text = "\n".join(pdf_content)

      except Exception as e:
          print(f"Lỗi khi trích xuất nội dung PDF: {e}")
  return pdf_text

def file_pdf_to_text(pdf_path: str):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n" if page.extract_text() else ""
    return text

def crawl_WHO_form_url(url: str, title: str):
    crawl = {
        "src": url,
        "paragraphs": []
    }

    if '.pdf' in url.lower():
      crawl["paragraphs"] = [{"content": pdf_to_text(url)}]
      return crawl


    driver = get_chrome_driver()
    driver.get(url)
    time.sleep(random.uniform(3, 3))

    all_elements = driver.find_elements(By.XPATH, ".//p | .//img | .//li | .//h2 | .//a")
    time.sleep(random.uniform(3, 3))
    for element in all_elements:
      if element.tag_name == "a":
          text_content = element.text.strip()
          if "Download" in text_content:
              download_url = element.get_attribute("href")
              crawl["paragraphs"] = [{"content": pdf_to_text(download_url)}]

              break

      if element.tag_name == "p":
          if element.find_elements(By.XPATH, ".//a"):
              continue
          text_content = element.get_attribute("innerText").strip()
          if text_content and text_content in ['Feature stories', 'Infographics', 'Videos', 'Events', 'Related links', 'Related', 'More']:
              break
          if text_content:
              crawl['paragraphs'].append({"content": text_content})
      elif element.tag_name == "li":
          if element.find_elements(By.XPATH, ".//a"):
            continue  # Bỏ qua nếu <li> chứa <a>
          text_content = element.text.strip()
          if text_content:
              crawl['paragraphs'].append({"content": text_content})
      elif element.tag_name == "img":
          img_url = element.get_attribute("src")
          if img_url:
              crawl['paragraphs'].append({"content": img_url})
      elif  element.tag_name == "h2":
          text_content = element.text.strip()
          if text_content and text_content in ['News', 'Publications', 'WHO documents', 'Our work']:
              break
    driver.quit()
    return crawl

def process_url(url: dict):
    crawl = {
        "src": url['link'],
        "paragraphs": []
    }

    if '.pdf' in url['link'].lower():
        crawl["paragraphs"] = [{"content": pdf_to_text(url['link'])}]
        print(f'Crawl Information of WHO:\n{crawl}')
        return crawl

    driver = get_chrome_driver()
    try:
        driver.get(url['link'])
        time.sleep(random.uniform(3, 5))

        report_list = driver.find_elements(By.CLASS_NAME, "card--list.matching-height--item")
        if report_list:
            report_urls = [item.find_element(By.XPATH, ".//a").get_attribute("href") for item in report_list[:MINIMUM_K]]
            driver.quit()

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as inner_executor:
                crawled_reports = list(inner_executor.map(crawl_WHO_form_url, report_urls, [""] * len(report_urls)))

            print(f'Crawl Information of WHO:\n{crawled_reports}')
            return crawled_reports

        report_list = driver.find_elements(By.CLASS_NAME, "sf-meeting-report-list__item")
        if report_list:
            report_urls = [item.get_attribute("href") for item in report_list[:MINIMUM_K]]
            driver.quit()

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as inner_executor:
                crawled_reports = list(inner_executor.map(crawl_WHO_form_url, report_urls, [""] * len(report_urls)))

            print(f'Crawl Information of WHO:\n{crawled_reports}')
            return crawled_reports

        crawl = crawl_WHO_form_url(url['link'], url['title'])
        print(f'Crawl Information of WHO:\n{crawl}')
        return crawl

    finally:
        driver.quit()

def crawl_WHO(urls: List[dict], crawl_json: List[dict]):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_url, urls))

    for result in results:
        if isinstance(result, list):
            crawl_json.extend(result)
        else:
            crawl_json.append(result)

# def crawl_WHO(urls: List[str], crawl_json: List[dict]):
#   for url in urls:
#     crawl = {
#         "src": url['link'],
#         "paragraphs": []
#     }
#     if '.pdf' in url['link'].lower():
#       crawl["paragraphs"] = [{"content": pdf_to_text(url['link'])}]
#       print(f'Crawl Information of WHO:\n{crawl}')
#       crawl_json.append(crawl)
#       continue
#     driver = webdriver.Chrome(options=chrome_options)
#     driver.get(url['link'])
#     time.sleep(random.uniform(3, 3))

#     report_list = driver.find_elements(By.CLASS_NAME, "card--list.matching-height--item")
#     if report_list:
#       report_urls = []
#       for item in report_list[:MINIMUM_K]:
#         report_url = item.find_element(By.XPATH, ".//a").get_attribute("href")
#         report_urls.append(report_url)
#       driver.quit()

#       for report_url in report_urls:
#         crawl = crawl_WHO_form_url(report_url, "")
#         print(f'Crawl Information of WHO:\n{crawl}')
#         crawl_json.append(crawl)
#       continue

#     report_list = driver.find_elements(By.CLASS_NAME, "sf-meeting-report-list__item")
#     if report_list:
#       report_urls = []
#       for item in report_list[:MINIMUM_K]:
#         report_url = item.get_attribute("href")
#         report_urls.append(report_url)
#       driver.quit()

#       for report_url in report_urls:
#         crawl = crawl_WHO_form_url(report_url, "")
#         print(f'Crawl Information of WHO:\n{crawl}')
#         crawl_json.append(crawl)
#       continue

#     crawl = crawl_WHO_form_url(url['link'], url['title'])

#     print(f'Crawl Information of WHO:\n{crawl}')

#     crawl_json.append(crawl)
#     driver.quit()

def process_other_link(other_link: LinkArticle):
    other_crawl = {
        "src": other_link.link,
        "paragraphs": []
    }

    driver = get_chrome_driver()
    try:
        driver.get(other_link.link)
        time.sleep(random.uniform(3, 5))
        all_elements = driver.find_elements(By.XPATH, ".//p")

        for element in all_elements:
            if element.tag_name == "p":
                text_content = element.get_attribute("innerText").strip()
                if text_content:
                    other_crawl['paragraphs'].append({"content": text_content})

        print(f'Crawl Information of Other Sites:\n{other_crawl}')
        return other_crawl

    finally:
        driver.quit()

def crawl_others(sentence: str, who_urls: List[str], crawl_json: List[dict], conversationsessionsID: str):
    query = analyze_prompt(sentence)
    print(query)
    url_others = search_relevant_links(query, MINIMUM_K, conversationsessionsID)

    who_links_set = {item['link'] for item in who_urls}

    url_others = [item for item in url_others if item.link not in who_links_set]

    url_others = url_others[:MINIMUM_K]

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_other_link, url_others))

    crawl_json.extend(results)

# def crawl_others(sentence: str, who_urls: List[str], crawl_json: List[dict], topK: int, conversationsessionsID: str):
  # query = analyze_prompt(sentence)
  # # print(query)
  # url_others = search_relevant_links(query, topK, conversationsessionsID)
  # count = 1
  # for other_link in url_others:
  #   if count > MINIMUM_K:
  #     break
  #   # if other_link == '' or other_link in who_urls:
  #   #   continue
  #   count += 1
  #   other_crawl = {
  #       "src": other_link,
  #       "paragraphs": []
  #   }

  #   try:
  #     driver = webdriver.Chrome(options=chrome_options)
  #     print(other_link)
  #     driver.get(other_link.link)
  #     time.sleep(random.uniform(3, 3))
  #     all_elements = driver.find_elements(By.XPATH, ".//p")

  #     for element in all_elements:
  #       if element.tag_name == "p":
  #           text_content = element.get_attribute("innerText").strip()
  #           if text_content:
  #               other_crawl['paragraphs'].append({"content": text_content})

  #     print(f'Crawl Information of Other Sites:\n{other_crawl}')

  #     crawl_json.append(other_crawl)
  #     driver.quit()
  #   except:
  #     print(f"Unable to crawl website: {other_link.link}")
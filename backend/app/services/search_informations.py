from app.config import *
from app.models.schemas import SearchQuery, LinkArticle
from app.database.connect import *
from app.utils.chrome_driver import *

def analyze_prompt(text: str):
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "You are an information extractor. Your job is to extract the site (if any) from the input text."
                " Only return a site if the input text explicitly includes a domain (like 'example.com', 'nytimes.com', etc.)."
                " If there is no site in the text, return an empty string for site."
            )},
            # {"role": "system", "content": "Extract the information. If site exists, return the domain name of the site. Otherwise return empty."},
            {"role": "user", "content": text},
        ],
        response_format=SearchQuery,
    )

    query = completion.choices[0].message.parsed

    return query

def search_relevant_links(query: SearchQuery, topK: int, conversationsessionsID: str):
    driver = get_chrome_driver()
    
    site = query.site.strip().lower() if query.site else ''
    if site and site not in ['n/a', 'none']:
        search_url = f'https://www.bing.com/search?q=site:{site} {query.query}'
    else:
        search_url = f'https://www.bing.com/search?q={query.query}'
    print(search_url)
    driver.get(search_url)

    # print(driver.page_source)
    time.sleep(10)

    articles = driver.find_elements(By.CSS_SELECTOR, "#b_results li.b_algo")
    link_articles = []
    
    if not articles:
        time.sleep(5)
        articles = driver.find_elements(By.CSS_SELECTOR, "#b_results li.b_algo")

    existing_links = set()
    existing_documents = db.articlefiles.find({"SessionID": conversationsessionsID})
    for doc in existing_documents:
        existing_links.add(doc["Link"])

    for article in articles[:min(topK, len(articles))]:
        title_element = article.find_element(By.TAG_NAME, "h2").find_element(By.TAG_NAME, "a")
        title = title_element.text
        link = title_element.get_attribute('href')

        if link not in existing_links:
            # link_articles.append({"title": title, "link": link})
            link_article = LinkArticle(
                title=title,
                link=link,
            )
            link_articles.append(link_article)
    print(link_articles)

    driver.quit()

    return link_articles

def convert_to_pdf(link_articles: List[LinkArticle], conversationsessionsID: str):
    file_paths = []
    links = []

    session_storage_path = f"{STORAGE_PATH}/{conversationsessionsID}"
    os.makedirs(session_storage_path, exist_ok=True)

    for article in link_articles:
        title = re.sub(r'[^a-zA-Z\s]', '', article.title)
        title = title.replace(" ", "_")
        pdf_path = f"{session_storage_path}/{title}.pdf"
        url = article.link

        existing_article = db.articlefiles.find_one({
            "Link": article.link
        })
        
        if existing_article:
            file_id = existing_article["FileId"]

            if not db.articlefiles.find_one({"SessionID": conversationsessionsID, "Link": article.link}):
                db.articlefiles.insert_one({
                    "SessionID": conversationsessionsID,
                    "Title": article.title,
                    "Link": article.link,
                    "FileId": file_id,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow(),
                })

            with open(pdf_path, 'wb') as f:
                f.write(fs.get(file_id).read())
            
            print(f"Tải file PDF từ MongoDB: {pdf_path}")
            file_paths.append(pdf_path)
            links.append(article)
            
            continue

    
        try: 
            driver = get_chrome_driver()
            # Access the webpage and create PDF
            driver.get(url)
            
            print_options = {'path': pdf_path, 'printBackground': True}
            pdf = driver.execute_cdp_cmd("Page.printToPDF", print_options)
            
            # Decode and save the PDF file
            pdf_data = base64.b64decode(pdf['data'])

            with open(pdf_path, 'wb') as f:
                f.write(pdf_data)
            driver.quit()

            file_id = fs.put(pdf_data, filename=pdf_path)

            db.articlefiles.insert_one({
                "SessionID": conversationsessionsID,
                "Title": article.title,
                "Link": article.link,
                "FileId": file_id, 
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            })

            file_paths.append(pdf_path)
            links.append(article) 
        except:
            print(f"Unable to crawl website: {url}")

    print(f"PDF files saved to: {file_paths}")

    return file_paths, links
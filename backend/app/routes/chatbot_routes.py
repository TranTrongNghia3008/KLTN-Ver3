from fastapi import APIRouter
from app.services.chatbot import *
from app.services.crawl_who import *
from app.services.refine_answer import *
from app.services.location_summarization import *
from app.services.split_sentences import *
from app.services.verify_information import *
from app.services.search_informations import *
from app.database.connect import db
from app.models.schemas import *
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/q-and-a", tags=["Chatbot"])

@router.post("/getLocationInformations")
async def get_location_informations(request: LocationRequest):
    link_articles = request.link_articles
    files_path = request.files_path
    conversationsessionsID = request.conversationsessionsID

    link_articles = parallel_processing(link_articles, files_path, conversationsessionsID)

    merged_locations = merge_locations(link_articles)

    for loc in merged_locations:
        loc_data = {
            "SessionID": ObjectId(conversationsessionsID),
            "administrative_area": loc.administrative_area,
            "country": loc.country,
            "continent": loc.continent,
            "lat": loc.lat,
            "lon": loc.lon,
            "links": loc.links,
            "summaries": loc.summaries,
            "sentiment": loc.sentiment,
            "__v": 0,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
        }

        db.locations.insert_one(loc_data)
    
    return merged_locations

@router.get("/getRelevantLinks")
async def get_relevant_links(text: str, topK: int, conversationsessionsID: str):
    query = analyze_prompt(text)
    print(query)
    
    # if not query.site:
    #     return JSONResponse(content={"message": "No site found in the text"}, status_code=400)
    
    links = search_relevant_links(query, topK, conversationsessionsID)
    file_paths, links = convert_to_pdf(links, conversationsessionsID)
    
    location_request = LocationRequest(
        link_articles=links,
        files_path=file_paths,
        conversationsessionsID=conversationsessionsID
    )
    
    locations = await get_location_informations(location_request)
    
    return {"query": query, "links": links, "file paths": file_paths, "locations": locations}

@router.post("/getResponse")
async def get_response(request: ResponseRequest):
    text = request.text
    isCrawl = request.isCrawl
    linkSpecific = request.linkSpecific
    topK = request.topK
    conversationsessionsID = request.conversationsessionsID
    
    session = db.conversationsessions.find_one({"_id": ObjectId(conversationsessionsID)})
    vector_store_id = session.get("VectorStoreID")
    assistant_id = session.get("AssistantID")
    history = session.get("History")

    if not assistant_id:
        isCrawl = True
        vector_store = create_vector_store(conversationsessionsID)
        vector_store_id = vector_store.id

        assistant = create_assistant(vector_store_id)
        assistant_id = assistant.id

    relevant_files = {"query": text, "links": [], "file paths": [], "locations": []}
    
    if linkSpecific.startswith("http://") or linkSpecific.startswith("https://"):
        custom_articles = LinkArticle(
            title=text,
            link=linkSpecific
        )
        relevant_files["links"] = [custom_articles]
        relevant_files["file paths"], relevant_files["links"] = convert_to_pdf([custom_articles], conversationsessionsID)
        
    elif isCrawl:
        relevant_files = await get_relevant_links(text=text, topK=topK, conversationsessionsID=conversationsessionsID)
    else:
        relevant_files = {}
    
    if relevant_files and relevant_files["file paths"]:
        if not vector_store_id:
            vector_store = create_vector_store(conversationsessionsID)
            vector_store_id = vector_store.id

        update_vector_store(vector_store_id, relevant_files["file paths"])
        assistant = create_assistant(vector_store_id)
        assistant_id = assistant.id
        
        db.conversationsessions.update_one(
            {"_id": ObjectId(conversationsessionsID)},
            {"$set": {"VectorStoreID": vector_store_id, "AssistantID": assistant_id}}
        )

    # qa_history = None if not session.get("History") else "\n".join(session.get("History"))

    filtered_history = [item for item in history if not item.startswith("Ref: ")]

    qa_history = None if not filtered_history else "\n".join(filtered_history)
    
    prompt = (
        f"The uploaded files are articles that were searched with the keyword '{text}'.\n"
        f"Pay attention to previous Q&A history (if any): \n{qa_history}\n"
        f"Given the query below, identify and return the key details explicitly mentioned that are necessary for information retrieval.\n\n"
        f"QUERY: '{text}'"
    )
        
    response = flow_qa(prompt, assistant_id)
    response = re.sub(r"【[^】]*source】", "", response)
    db.conversationsessions.update_one(
        {"_id": ObjectId(conversationsessionsID)},
        {"$push": {"History": f"User: {text}"}}
    )

    print(f"Response: {response}")
    ref_files = []
    splitted_sentences = split_into_sentences(response)
    filtered_sentences = filter_sentences(splitted_sentences)
    fact_check_results = fact_check_pipeline(filtered_sentences, ref_files, response, conversationsessionsID)

    old_message = response
    highlight_not_correct, link_not_correct, highlight_correct, link_correct, new_message = filter_the_output(fact_check_results, old_message)
    db.conversationsessions.update_one(
    {"_id": ObjectId(conversationsessionsID)},
    {
        "$push": {
            "History": f"""System: OldMessage:{old_message}
            HighlightNotCorrect: {highlight_not_correct}
            LinkNotCorrect: {link_not_correct}
            HighlightCorrect: {highlight_correct}
            LinkCorrect: {link_correct}
            NewMessage: {new_message}"""
        }
    }
)
    ref = relevant_files.get("links", []) 
    html_links = " ".join(
        f'<a href="{article.link}" target="_blank">{article.title}</a><br>'
        for article in ref
    )

    # Cập nhật vào trường History của conversationsessions trong MongoDB
    db.conversationsessions.update_one(
        {"_id": ObjectId(conversationsessionsID)},
        {"$push": {"History": f"Ref: {html_links}"}}
    )
    # print(relevant_files["locations"])
    # return ResponseModel(textAnswer=response, links=relevant_files["links"], locations=relevant_files["locations"], status="success")
    return {
        "textAnswer": response,
        "links": relevant_files.get("links", []),
        "locations": relevant_files.get("locations", []),
        "status": "success"
    }
from app.services.crawl_who import *
from app.config import *

def sentence_mapping_pipeline(filtered_sentence: str, original_answer: str, fact_check_result: FactCheck, crawl_json: List[dict]):
    label = fact_check_result.label
    explanation = fact_check_result.explanation
    revised_sentence = fact_check_result.revised_sentence
    evidence_urls = [item["src"] for item in crawl_json if "src" in item]

    prompt = f"""
        You are an AI specializing in paraphrase detection and claim verification.
        Your task is to identify the segment in `original_answer` that is most closely related to `filtered_sentence`
        by detecting paraphrasing or rewording.

        ### Input:
        - **Filtered Sentence (paraphrased version):** {filtered_sentence}
        - **Original Answer (source text):** {original_answer}

        ### Instructions:
        1. Identify the most relevant and continuous segment in `original_answer` that `filtered_sentence` paraphrases.
        2. Focus on **semantic similarity**, rather than requiring exact word matches.
        3. Ensure the extracted segment has the **same meaning** as `filtered_sentence`, even if it is worded differently.
        4. If no perfect match exists, find the **closest semantically relevant portion**.

        ### Output Format:
          sentence: "{filtered_sentence}",
          referenced_segment: "Extracted segment from original_answer."
    """
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI expert in claim verification."},
                {"role": "user", "content": prompt},
            ],
            response_format=SentenceMapping
        )
        result = response.choices[0].message.parsed

        result.label = label
        result.explanation = explanation
        result.evidence_urls = evidence_urls
        result.revised_sentence = revised_sentence

        return result

    except Exception as e:
        print(f"Problem with API: {e}")
        return SentenceMapping(
            sentence=filtered_sentence,
            referenced_segment="Not found",
            label=False,
            explanation="Error processing request.",
            evidence_urls=[]
        )

def fact_check_pipeline(filtered_sentences: List[str], crawl_json: List[dict], original_answer: str, conversationsessionsID: str, evidence_text="", maximum_characters=1000000):
    final_results = []

    for sentence in filtered_sentences:
        who_urls = search_who(sentence)
        if not who_urls:
            print(f"Can't find related articles for:\n{sentence}")

        crawl_WHO(who_urls, crawl_json)
        crawl_others(sentence, who_urls, crawl_json, conversationsessionsID)

        # article_texts = " ".join([article["paragraphs"][0]["content"] for article in crawl_json if article["paragraphs"]])
        article_texts = "\n".join(para["content"] for item in crawl_json for para in item["paragraphs"] if "content" in para)
        article_texts = article_texts[:maximum_characters]

        prompt = f"""
        You are a medical fact-checking expert. Your task is to determine whether the given sentence accurately represents medical information based on the provided reference documents.
        Note:
        - Ignore minor formatting issues (e.g., capitalization)
        - Do not classify a sentence as Fake only because it lacks some details.

        ### Input:
        - **Sentence:** {sentence}
        - **Documents:**
            {evidence_text}

        ### Instructions:
        1. Compare the sentence with the Reference Documents.
        2. Identify any modifications, distortions, or misinformation in the sentence compared to the reference materials. Nouns/noun phrases in the sentence may have been modified or some characters may have been added or removed to cause misunderstanding.
        3. Classify the sentence as:
          - **Fake (False)**: If it contains misleading, altered, or incorrect information. It contains nouns/noun phrases changed or added/removed characters.
          - **Real (True)**: If it aligns with the reference or is a valid inference or unlikely to be False.
        4. Provide a concise explanation supporting your decision.
        5. If the sentence is Fake, rewrite it correctly based on the reference materials without adding new information.

        ### Output Format:
          sentence: "{sentence}",
          explanation: "Reasoning for classification.",
          label: true/false,
          revised_sentence: "Corrected sentence if Fake, otherwise the original."

        **Additional Information**: {article_texts}
        """
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a medical fact-checking expert."},
                    {"role": "user", "content": prompt},
                ],
                response_format=FactCheck
            )
            result = response.choices[0].message.parsed
            result = sentence_mapping_pipeline(sentence, original_answer, result, crawl_json)

            print(result)
            final_results.append({"sentence": sentence, "status": result.label, "details": result})

        except Exception as e:
            print(f"Problem with API: {e}")

            result = "Unverified"
            final_results.append({"sentence": sentence, "status": result, "details": result})


        print(f"Result: {result}\n")

    return final_results
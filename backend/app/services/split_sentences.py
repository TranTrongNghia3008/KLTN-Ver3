from app.config import *
from app.utils.ner_pipeline import *

def get_entities(answer: str):
    entities = ner_pipe(answer)
    return entities

def call_gpt4(prompt: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates fact-checking prompts for medical entities."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=100,
    )
    return response.choices[0].message.content

def split_into_sentences(answer: str):
    entities = get_entities(answer)
    entity_texts = [entity['word'] for entity in entities]

    prompt = (
      f"You are an AI specializing in extracting precise factual statements in the medical domain. "
      f"Break down the following response into distinct sections with self-contained factual statements. "
      f"Ensure each fact is clear, concise, and medically accurate. "
      f"Use existing entities or extract additional ones as needed to **avoid vague references** like 'it' or 'this'. "
      f"Remove opinions, assumptions, and ambiguous references.\n\n"
      f"### Input:\n"
      f"Response: '{answer}'\n\n"
      f"Entities: {', '.join(entity_texts)}\n\n"
      f"### Output:\n"
      f"- Each fact should be a **complete and independent sentence**.\n"
      f"- Clarify any ambiguous terms by specifying the subject.\n"
      f"- Identify key medical terms if missing.\n"
      f"- Avoid redundancy while preserving all key details.\n\n"
      f"### Output Format:\n"
      f"Sentence 1\n"
      f"Sentence 2\n"
      f"Sentence 3 (etc.)"
  )


    gpt_response = call_gpt4(prompt)

    sentences = re.split(r'(?<=[.])\s+|\n+', gpt_response)
    return [sentence.strip() for sentence in sentences if sentence.strip()]

def check_sentence_for_verification(sentence: str):
    # Prompt 1: Check for medical relevance
    prompt_1 = f"Based on the following sentence, determine if it is related to the medical field. If yes, reply 'yes'. If not, reply 'no'. Sentence: '{sentence}'"
    medical_check = call_gpt4(prompt_1)

    # Prompt 2: Check for need of verification
    prompt_2 = f"Determine if the sentence contains information that needs to be verified. If the sentence seems like a general statement or obvious information, reply 'no'. If the sentence requires verification, reply 'yes'. Sentence: '{sentence}'"
    verification_check = call_gpt4(prompt_2)

    # Prompt 3: Check for specificity and detail
    prompt_3 = f"Determine if the sentence has enough detail to be verified. If the sentence has vague subjects (e.g., 'someone', 'a person'), reply 'no'. If the sentence has a clear and detailed subject, reply 'yes'. Sentence: '{sentence}'"
    specificity_check = call_gpt4(prompt_3)

    return medical_check, verification_check, specificity_check

def filter_sentences(sentences: List[str]):
    filtered_sentences = []

    for sentence in sentences:
        medical_check, verification_check, specificity_check = check_sentence_for_verification(sentence)

        # print(f"Sentence: '{sentence}'")
        # print(f"Medical Check: {medical_check}")
        # print(f"Verification Check: {verification_check}")
        # print(f"Specificity Check: {specificity_check}")
        # print()

        yes_count = sum([
            medical_check.lower() == 'yes',
            verification_check.lower() == 'yes',
            specificity_check.lower() == 'yes'
        ])

        if yes_count >= 2:
            filtered_sentences.append(sentence)

    return filtered_sentences
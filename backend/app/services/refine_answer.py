from app.config import *

def correct_answer(original_answer, correct_info, incorrect_info, revised_info):
  prompt = f"""
  You are tasked with revising an answer. Here is the information provided:

  1. Original Answer: {original_answer}

  2. Correct Information:
  {correct_info}

  3. Incorrect Information:
  {incorrect_info}

  4. Revised Information for Incorrect Information:
  {revised_info}

  Your task:
  - Remove all incorrect information from the original answer.
  - Replace incorrect information with the correct revised information.
  - Ensure the final answer remains coherent, clear, and accurate.

  Provide the revised answer below:
  """
  print(prompt)
  completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
            {"role": "system", "content": "You are a helpful assistant for correcting text."},
            {"role": "user", "content": prompt},
        ]
  )

  return completion.choices[0].message.content

def filter_the_output(fact_check_results, old_message):
  highlight_not_correct = ""
  link_not_correct = ""
  highlight_correct = ""
  link_correct = ""

  true_sentences = [item["details"].referenced_segment for item in fact_check_results if item["status"]]
  false_sentences = [item["details"].referenced_segment for item in fact_check_results if not item["status"]]
  revise_sentences = [item["details"].revised_sentence for item in fact_check_results if not item["status"]]
  new_message = correct_answer(old_message, true_sentences, false_sentences, revise_sentences)

  for result in fact_check_results:
      sentence = result['sentence']
      status = result['status']
      details = result.get('details', {})

      if details:
          referenced_segment = details.referenced_segment
          evidence_urls = details.evidence_urls

          if not evidence_urls:
              print("Empty evidence urls:", details)
              continue

          if status:  # If it is true
              if highlight_correct != "":
                  highlight_correct += ","
              highlight_correct += f"''{referenced_segment}''"

              if link_correct != "":
                  link_correct += ","
              link_correct += f"''{evidence_urls[0]}''"
              # link_correct += ", ".join([f"''{url}''" for url in evidence_urls])

          else:  # If it is wrong
              if highlight_not_correct != "":
                  highlight_not_correct += ","
              highlight_not_correct += f"''{referenced_segment}''"

              if link_not_correct != "":
                  link_not_correct += ","
              link_not_correct += f"''{evidence_urls[0]}''"
              # link_not_correct += ", ".join([f" '''{url}'''" for url in evidence_urls])
  
  highlight_not_correct += "."
  link_not_correct += "."
  highlight_correct += "."
  link_correct += "."

  return highlight_not_correct, link_not_correct, highlight_correct, link_correct, new_message

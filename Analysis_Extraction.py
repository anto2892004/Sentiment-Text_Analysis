                        # Content Extraction Using BeautifulSoup and requests 


import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

data = pd.read_excel('Input.xlsx')

os.makedirs("content", exist_ok=True)
def extract_article_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('title').get_text(strip=True)
        article = ' '.join([p.get_text(strip=True) for p in soup.find_all('p')])

        return title, article
    except Exception as e:
        print(f"Failed to extract {url}: {e}")
        return None, None

for index, row in data.iterrows():
    url_id = row['URL_ID']
    url = row['URL']

    title, article = extract_article_content(url)

    if title and article:
        with open(f"extracted_articles/{url_id}.txt", 'w', encoding='utf-8') as file:
            file.write(f"{title}\n\n{article}")

print("Data extraction complete. Files saved in 'content' folder.")


                                    # Content Analysis Phase





from textblob import TextBlob
import pandas as pd
import os
import syllapy
import readability


def load_article(url_id):
    try:
        with open(f"content/{url_id}.txt", 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return None

def analyze_text(text):
    blob = TextBlob(text)

    # Sentiment Analysis
    positive_score = sum(1 for word in text.split() if TextBlob(word).sentiment.polarity > 0)
    negative_score = sum(1 for word in text.split() if TextBlob(word).sentiment.polarity < 0)
    polarity_score = blob.sentiment.polarity
    subjectivity_score = blob.sentiment.subjectivity

    # Sentence Length Analysis
    sentences = text.split('.')
    avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences) if sentences else 0
    avg_words_per_sentence = avg_sentence_length 

    # Complex Word Count and Syllable Count
    complex_words = [word for word in text.split() if syllapy.count(word) > 2]
    complex_word_count = len(complex_words)
    total_words = len(text.split())
    syllables_per_word = sum(syllapy.count(word) for word in text.split()) / total_words if total_words else 0

    # FOG Index
    fog_index = 0.4 * (avg_sentence_length + (100 * (complex_word_count / total_words)))

    # Word Count
    word_count = total_words

    # Personal Pronouns (basic list for demonstration)
    personal_pronouns = sum(word.lower() in ['i', 'you', 'he', 'she', 'we', 'they'] for word in text.split())

    # Average Word Length
    avg_word_length = sum(len(word) for word in text.split()) / total_words if total_words else 0

    # Percentage of Complex Words
    percentage_complex_words = (complex_word_count / total_words) * 100 if total_words else 0

    return {
        "positive_score": positive_score,
        "negative_score": negative_score,
        "polarity_score": polarity_score,
        "subjectivity_score": subjectivity_score,
        "avg_sentence_length": avg_sentence_length,
        "percentage_complex_words": percentage_complex_words,
        "fog_index": fog_index,
        "avg_words_per_sentence": avg_words_per_sentence,
        "complex_word_count": complex_word_count,
        "word_count": word_count,
        "syllables_per_word": syllables_per_word,
        "personal_pronouns": personal_pronouns,
        "avg_word_length": avg_word_length
    }

def create_output_df(input_file):
    input_data = pd.read_excel(input_file)
    output_data = []

    for _, row in input_data.iterrows():
        url_id = row['URL_ID']
        text = load_article(url_id)
        if text:
            analysis_results = analyze_text(text)
            output_row = {**row.to_dict(), **analysis_results}
            output_data.append(output_row)

    output_df = pd.DataFrame(output_data)
    return output_df

def save_to_excel(df, output_file="Output Data Structure.xlsx"):
    df.to_excel(output_file, index=False)
    print("Analysis complete. Data saved to", output_file)

input_file = "Input.xlsx"
output_df = create_output_df(input_file)
save_to_excel(output_df)
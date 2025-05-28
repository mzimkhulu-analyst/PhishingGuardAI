import spacy
import pandas as pd
import re
from email.parser import BytesParser
from email import policy
import json
import os

nlp = spacy.load("en_core_web_sm")

def clean_email(text):
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Remove URLs
    text = re.sub(r"http[s]?://\S+", "", text)
    # Normalize whitespace
    text = " ".join(text.split())
    return text

def preprocess_email(email_text):
    cleaned = clean_email(email_text)
    doc = nlp(cleaned)
    tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return {"tokens": tokens, "entities": entities, "cleaned_text": cleaned}

def load_emails(file_path):
    processed = []
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
            # Use 'text' column if it exists, otherwise use the first column
            text_column = "text" if "text" in df.columns else df.columns[0]
            # Use 'label' column if it exists, otherwise default to "unknown"
            labels = df["label"].tolist() if "label" in df.columns else ["unknown"] * len(df)
            # Batch process with nlp.pipe for efficiency
            texts = df[text_column].tolist()
            for doc, label in zip(nlp.pipe(texts), labels):
                cleaned = clean_email(doc.text)
                tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
                entities = [(ent.text, ent.label_) for ent in doc.ents]
                processed.append({"tokens": tokens, "entities": entities, "cleaned_text": cleaned, "label": label})
        elif file_path.endswith(".eml"):
            with open(file_path, "rb") as f:
                email = BytesParser(policy=policy.default).parse(f)
                text = email.get_body(preferencelist=("plain", "html")).get_content()
                result = preprocess_email(text)
                result["label"] = "unknown"  # Default for .eml files
                processed.append(result)
        else:
            raise ValueError("Unsupported file format. Use .csv or .eml")
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return []
    except Exception as e:
        print(f"Error processing file: {e}")
        return []
    return processed

def save_emails(data, output_path="data/processed_emails.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved preprocessed emails to {output_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

# Example usage
if __name__ == "__main__":
    emails = load_emails("data/emails.csv")
    save_emails(emails)
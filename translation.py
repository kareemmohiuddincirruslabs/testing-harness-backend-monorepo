from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM, pipeline
import pandas as pd
import time

t5_tokenizer = AutoTokenizer.from_pretrained('t5-small')
t5_model = AutoModelForSeq2SeqLM.from_pretrained('t5-small')


checkpoint = "facebook/nllb-200-distilled-600M"
f200_model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
f200_tokenizer = AutoTokenizer.from_pretrained(checkpoint)

hel_model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-fr")
hel_tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-fr")


# ti_tokenizer = AutoTokenizer.from_pretrained("Unbabel/TowerInstruct-7B-v0.1")
# ti_model = AutoModelForCausalLM.from_pretrained("Unbabel/TowerInstruct-7B-v0.1")

source_lang = "eng_Latn"
target_lang = "fra_Latn"

df = pd.read_csv('data/clean_df.csv')
medf = pd.read_csv('data/clean_medf.csv')

# Function to generate translations
def generate_translation_t5(input_text):
    try:
        input_ids = t5_tokenizer.encode(input_text, return_tensors='pt')
        outputs = t5_model.generate(input_ids, max_length=50)
        output_text = t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return output_text
    except Exception as e:
        print(f"Error generating translation: {e}")
        return None
    
def generate_translation_f200(input_text):
    try:
        translator = pipeline("translation", model=f200_model, tokenizer=f200_tokenizer, src_lang=source_lang, tgt_lang=target_lang, max_length = 400)
        output = translator(input_text)
        output_text = output[0]["translation_text"]
        return output_text
    except Exception as e:
        print(f"Error generating translation: {e}")
        return None

def generate_translation_hel(input_text):
    try:
        translator = pipeline("translation", model=hel_model, tokenizer=hel_tokenizer, src_lang=source_lang, tgt_lang=target_lang, max_length = 400)
        output = translator(input_text)
        output_text = output[0]["translation_text"]
        return output_text
    except Exception as e:
        print(f"Error generating translation: {e}")
        return None

# Generate translations for each English sentence in the dataset
def translate(df):
    predicted_t5 = []
    predicted_f200 = []
    predicted_hel = []
    for english_sentence in df['en']:
        translated_text_t5 = generate_translation_t5(f"translate English to French: {english_sentence}")
        translated_text_f200 = generate_translation_f200(english_sentence)
        translated_text_hel = generate_translation_hel(english_sentence)
        if translated_text_t5:
            predicted_t5.append(translated_text_t5)
        if translated_text_f200:
            predicted_f200.append(translated_text_f200)
        if translated_text_hel:
            predicted_hel.append(translated_text_hel)
    return predicted_t5, predicted_f200, predicted_hel


start_time = time.time()

t5_df, f200_df, hel_df = translate(df)
prd_t5_df = pd.DataFrame(t5_df)
prd_f200_df = pd.DataFrame(f200_df)
prd_hel_df = pd.DataFrame(hel_df)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"DF took {elapsed_time} seconds to finish")

start_time = time.time()

t5_medf, f200_medf, hel_medf = translate(medf)
prd_t5_medf = pd.DataFrame(t5_medf)
prd_f200_medf = pd.DataFrame(f200_medf)
prd_hel_medf = pd.DataFrame(hel_medf)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"MEDF took {elapsed_time} seconds to finish")

prd_t5_df.to_csv("data/predicted_t5_df.csv", index=False)
prd_f200_df.to_csv("data/predicted_f200_df.csv", index=False)
prd_t5_medf.to_csv("data/predicted_t5_medf.csv", index=False)
prd_f200_medf.to_csv("data/predicted_f200_medf.csv", index=False)
prd_hel_df.to_csv("data/predicted_hel_df.csv", index=False)
prd_hel_medf.to_csv("data/predicted_hel_medf.csv", index=False)
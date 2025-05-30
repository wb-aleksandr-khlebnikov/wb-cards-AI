import os
import openai
import base64
import csv
import json
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI

# 🔐 Загружаем API-ключ из .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FOLDER_PATH = "./cards"
CSV_PATH = "results.csv"

HEADERS = [
    "Email", "Имя", "Фамилия", "Должность", "Город",
    "Тел", "Компания - назв", "Компания - сайт", "Сфера деятельности"
]

PROMPT = (
    "Извлеки контактные данные с визитки и верни ответ строго в формате JSON со следующими полями:\n"
    "{\n"
    "  \"Email\": \"\",\n"
    "  \"Имя\": \"\",\n"
    "  \"Фамилия\": \"\",\n"
    "  \"Должность\": \"\",\n"
    "  \"Город\": \"\",\n"
    "  \"Тел\": \"\",\n"
    "  \"Компания - назв\": \"\",\n"
    "  \"Компания - сайт\": \"\",\n"
    "  \"Сфера деятельности\": \"\"\n"
    "}\n"
    "Если данных нет — оставь поле пустым. Без пояснений, без форматирования в стиле ```json```."
)

# Очищаем Markdown-обёртки, если GPT всё же их добавил
def clean_json_response(raw):
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return raw.strip()

def analyze_image(image_path):
    try:
        with open(image_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": [
                        { "type": "text", "text": PROMPT },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )

        content = response.choices[0].message.content.strip()
        clean_content = clean_json_response(content)

        try:
            data = json.loads(clean_content)
            return [data.get(h, "") for h in HEADERS]
        except json.JSONDecodeError as e:
            return [f"❌ Ошибка парсинга JSON: {content}"] + [""] * (len(HEADERS) - 1)

    except Exception as e:
        return [f"❌ Ошибка API: {str(e)}"] + [""] * (len(HEADERS) - 1)

# 📁 Сканируем папку с визитками
image_files = sorted([
    f for f in os.listdir(FOLDER_PATH)
    if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
])

# 📤 Пишем результат в CSV
with open(CSV_PATH, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Файл"] + HEADERS)

    for filename in tqdm(image_files, desc="📎 Обработка визиток"):
        path = os.path.join(FOLDER_PATH, filename)
        row = analyze_image(path)
        writer.writerow([filename] + row)

print(f"\n✅ Готово! Таблица сохранена в: {CSV_PATH}")

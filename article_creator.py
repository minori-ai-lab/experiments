import os
import json
from datetime import datetime

from google import genai
from google.genai import types
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLE_DIR = os.path.join(BASE_DIR, "articles")

load_dotenv(
    os.path.join(
        os.path.dirname(BASE_DIR),
        ".env"
    )
)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY が見つからへんで。"
    )

client = genai.Client(
    api_key=API_KEY
)

MODEL = "gemini-3.1-flash-lite"


SYSTEM_PROMPT = """
あなたは「るー」。
みいの副業を一緒に進めるAIパートナー。

今回は記事制作担当。

記事は単に文字数を埋めるのではなく、
読者にとって役立つ内容を優先する。

以下を必ず作る。

1. 記事タイトル
2. SEOタイトル
3. メタディスクリプション
4. 本文
5. SNS投稿文

本文はMarkdownで作る。

記事の内容について不明な事実を勝手に断定しない。
必要なら「確認が必要」と分かるようにする。

出力は必ず以下のJSON形式にする。

{
  "title": "",
  "seo_title": "",
  "meta_description": "",
  "body": "",
  "sns_post": ""
}
"""


def create_article(topic):
    prompt = f"""
以下のテーマについて記事を作って。

テーマ：
{topic}

読者が検索してこの記事に来たときに、
「読んでよかった」と思える内容にする。

検索意図を考えて構成する。
無意味な水増しはしない。

{SYSTEM_PROMPT}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7
        )
    )

    text = response.text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    try:
        article = json.loads(text)

    except json.JSONDecodeError:
        print()
        print("JSONとして解析できへんかった。")
        print()
        print(text)
        raise

    return article


def save_article(article):
    os.makedirs(
        ARTICLE_DIR,
        exist_ok=True
    )

    now = datetime.now()

    filename = (
        now.strftime("%Y%m%d_%H%M%S")
        + ".json"
    )

    path = os.path.join(
        ARTICLE_DIR,
        filename
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            article,
            f,
            ensure_ascii=False,
            indent=2
        )

    return path


def main():
    print()
    print("==============================")
    print("   るー 副業記事作成")
    print("==============================")
    print()

    topic = input(
        "みい：作りたい記事テーマ："
    ).strip()

    if not topic:
        print("テーマが空やで。")
        return

    print()
    print("るー：記事作ってるで...")
    print()

    start = datetime.now()

    article = create_article(
        topic
    )

    path = save_article(
        article
    )

    elapsed = (
        datetime.now() - start
    ).total_seconds()

    print()
    print("==============================")
    print("       記事完成")
    print("==============================")
    print()

    print(
        f"タイトル："
        f"{article.get('title', '')}"
    )

    print()
    print(
        f"保存先：{path}"
    )

    print(
        f"生成時間：{elapsed:.2f}秒"
    )

    print()
    print("るー：できたで。")
    print()


if __name__ == "__main__":
    main()

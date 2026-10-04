import json
import os
import html
from http.server import HTTPServer, BaseHTTPRequestHandler


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARTICLE_DIR = os.path.join(
    BASE_DIR,
    "articles"
)

PUBLISHED_DIR = os.path.join(
    BASE_DIR,
    "published"
)

HOST = "127.0.0.1"
PORT = 8000


def get_latest_article():
    if not os.path.exists(ARTICLE_DIR):
        return None

    files = [
        f
        for f in os.listdir(ARTICLE_DIR)
        if f.endswith(".json")
    ]

    if not files:
        return None

    files.sort(reverse=True)

    path = os.path.join(
        ARTICLE_DIR,
        files[0]
    )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def markdown_to_html(text):
    lines = text.splitlines()

    result = []

    in_list = False

    for line in lines:

        line = line.strip()

        if not line:

            if in_list:
                result.append("</ul>")
                in_list = False

            continue

        if line.startswith("# "):

            result.append(
                "<h1>"
                + html.escape(line[2:])
                + "</h1>"
            )

        elif line.startswith("## "):

            result.append(
                "<h2>"
                + html.escape(line[3:])
                + "</h2>"
            )

        elif line.startswith("### "):

            result.append(
                "<h3>"
                + html.escape(line[4:])
                + "</h3>"
            )

        elif line.startswith("* "):

            if not in_list:
                result.append("<ul>")
                in_list = True

            result.append(
                "<li>"
                + html.escape(line[2:])
                + "</li>"
            )

        elif line.startswith("- "):

            if not in_list:
                result.append("<ul>")
                in_list = True

            result.append(
                "<li>"
                + html.escape(line[2:])
                + "</li>"
            )

        else:

            if in_list:
                result.append("</ul>")
                in_list = False

            result.append(
                "<p>"
                + html.escape(line)
                + "</p>"
            )

    if in_list:
        result.append("</ul>")

    return "\n".join(result)


def build_page(article):

    title = html.escape(
        article.get(
            "title",
            ""
        )
    )

    seo_title = html.escape(
        article.get(
            "seo_title",
            ""
        )
    )

    meta_description = html.escape(
        article.get(
            "meta_description",
            ""
        )
    )

    body = markdown_to_html(
        article.get(
            "body",
            ""
        )
    )

    sns_post = html.escape(
        article.get(
            "sns_post",
            ""
        )
    )

    return f"""<!DOCTYPE html>
<html lang="ja">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>{seo_title}</title>

<meta name="description"
      content="{meta_description}">

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    background: #f3f4f6;
    color: #222;
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Hiragino Kaku Gothic ProN",
        "Yu Gothic",
        sans-serif;
}}

.topbar {{
    position: sticky;
    top: 0;
    z-index: 10;

    background: #111827;
    color: white;

    padding: 14px 20px;

    display: flex;
    justify-content: space-between;
    align-items: center;

    gap: 12px;
}}

.topbar-title {{
    font-weight: bold;
}}

.status {{
    font-size: 13px;
    opacity: 0.8;
}}

.actions {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}}

button {{
    border: 0;
    border-radius: 8px;

    padding: 10px 16px;

    cursor: pointer;

    font-weight: bold;
}}

.reload {{
    background: #374151;
    color: white;
}}

.publish {{
    background: #facc15;
    color: #111827;
}}

.container {{
    max-width: 900px;

    margin: 32px auto;

    padding: 0 18px;
}}

.article {{
    background: white;

    padding: 42px;

    border-radius: 14px;

    box-shadow:
        0 4px 18px rgba(
            0,
            0,
            0,
            0.08
        );
}}

.article h1 {{
    font-size: 34px;

    line-height: 1.45;

    margin-top: 0;
}}

.article h2 {{
    margin-top: 42px;

    padding-bottom: 8px;

    border-bottom:
        2px solid #e5e7eb;
}}

.article h3 {{
    margin-top: 30px;
}}

.article p,
.article li {{
    font-size: 17px;

    line-height: 2;
}}

.article ul {{
    padding-left: 28px;
}}

.info {{
    margin-top: 24px;

    padding: 18px;

    background: #f9fafb;

    border:
        1px solid #e5e7eb;

    border-radius: 10px;
}}

.info strong {{
    display: block;

    margin-bottom: 8px;
}}

.sns {{
    white-space: pre-wrap;
}}

.message {{
    max-width: 900px;

    margin: 20px auto 0;

    padding: 0 18px;

    font-weight: bold;
}}

.success {{
    color: #15803d;
}}

.error {{
    color: #b91c1c;
}}

@media (max-width: 700px) {{

    .article {{
        padding: 24px 18px;
    }}

    .article h1 {{
        font-size: 27px;
    }}

    .article p,
    .article li {{
        font-size: 16px;
    }}
}}

</style>

</head>

<body>

<div class="topbar">

    <div class="topbar-title">
        るー｜記事プレビュー
    </div>

    <div class="actions">

        <button
            class="reload"
            onclick="location.reload()">
            最新記事を読み直す
        </button>

        <form
            method="POST"
            action="/publish">

            <button
                class="publish"
                type="submit">
                公開する
            </button>

        </form>

    </div>

</div>

<div class="message">

    <div id="message"></div>

</div>

<div class="container">

    <div class="article">

        {body}

        <div class="info">

            <strong>
                SEOタイトル
            </strong>

            {seo_title}

        </div>

        <div class="info">

            <strong>
                メタディスクリプション
            </strong>

            {meta_description}

        </div>

        <div class="info sns">

            <strong>
                SNS投稿文
            </strong>

            {sns_post}

        </div>

    </div>

</div>

</body>

</html>
"""


def publish_article():

    article = get_latest_article()

    if article is None:
        raise RuntimeError(
            "公開できる記事がないで。"
        )

    os.makedirs(
        PUBLISHED_DIR,
        exist_ok=True
    )

    page = build_page(
        article
    )

    path = os.path.join(
        PUBLISHED_DIR,
        "index.html"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(page)

    return path


class PreviewHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        article = get_latest_article()

        if article is None:

            content = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>るー</title>
</head>
<body>
<h1>記事がまだないで</h1>
</body>
</html>
"""

        else:

            content = build_page(
                article
            )

        data = content.encode(
            "utf-8"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(data))
        )

        self.end_headers()

        self.wfile.write(
            data
        )

    def do_POST(self):

        if self.path != "/publish":

            self.send_response(
                404
            )

            self.end_headers()

            return

        try:

            path = publish_article()

            self.send_response(
                303
            )

            self.send_header(
                "Location",
                "/?published=1"
            )

            self.end_headers()

            print()
            print(
                "[公開用ファイル生成]"
            )

            print(path)

        except Exception as e:

            print(
                f"[公開失敗] {e}"
            )

            self.send_response(
                500
            )

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )

            self.end_headers()

            self.wfile.write(
                str(e).encode(
                    "utf-8"
                )
            )

    def log_message(
        self,
        format,
        *args
    ):

        return


def main():

    print()

    print(
        "=============================="
    )

    print(
        "      るー 記事プレビュー"
    )

    print(
        "=============================="
    )

    print()

    print(
        f"http://{HOST}:{PORT}"
    )

    print()

    print(
        "記事を確認して、"
        "OKなら「公開する」を押してな。"
    )

    print()

    print(
        "公開先："
        f"{PUBLISHED_DIR}"
    )

    print()

    print(
        "終了：Ctrl+C"
    )

    print()

    server = HTTPServer(
        (
            HOST,
            PORT
        ),
        PreviewHandler
    )

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print()
        print(
            "プレビュー終了。"
        )

    finally:

        server.server_close()


if __name__ == "__main__":
    main()

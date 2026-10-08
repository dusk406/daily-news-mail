"""Build a Chinese daily news trend brief from GDELT and send it with AgentMail."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import escape

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
AGENTMAIL_URL = (
    "https://api.agentmail.to/v0/inboxes/"
    "thankfulproduct663@agentmail.to/messages/send"
)
RECIPIENT = "wuque_061@163.com"
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_json(url, headers=None, timeout=45):
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_articles():
    params = {
        "query": '("artificial intelligence" OR technology OR economy OR markets '
                 'OR employment OR education OR geopolitics OR China OR climate)',
        "mode": "ArtList",
        "format": "json",
        "maxrecords": "50",
        "timespan": "24h",
        "sort": "HybridRel",
    }
    url = GDELT_URL + "?" + urllib.parse.urlencode(params)
    data = get_json(url, headers={"User-Agent": "daily-news-mail/1.0"})
    articles = data.get("articles") or []
    seen = set()
    cleaned = []
    for article in articles:
        title = (article.get("title") or "").strip()
        link = (article.get("url") or "").strip()
        if not title or not link or link in seen:
            continue
        seen.add(link)
        cleaned.append({
            "title": title[:400],
            "url": link,
            "source": (article.get("domain") or "").strip(),
            "published": (article.get("seendate") or "").strip(),
            "language": (article.get("language") or "").strip(),
        })
    if not cleaned:
        raise RuntimeError("GDELT returned no usable articles; refusing to send an empty brief.")
    return cleaned[:30]


def generate_brief(articles):
    api_key = os.environ["OPENAI_API_KEY"]
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    prompt = f"""请根据下方最近24小时的新闻标题和来源，写一份中文《每日趋势简报》。
时间：{now}

读者关注：AI与科技、软件开发、中国经济与金融、就业与教育、国际社会与政策、地缘政治，以及这些变化对未来趋势和普通人生活/工作的影响。请筛选最重要的3至6条，避免只是罗列标题和重复报道。

每条简报都要有清楚的小标题，并覆盖：
- 事实：只陈述标题和来源能支持的内容；资料不足时明确写“标题信息有限，细节待核实”，不要补造数字、引语或事件细节。
- 背景：区分已知背景与推断，不确定处标明。
- 为什么重要：解释可能的趋势或连锁影响。
- 对普通人的影响：具体说明可能影响谁、通过什么渠道；没有明显影响就直说。
- 值得关注：给出接下来可观察的信号。

开头用几句话概括今天最值得注意的趋势；结尾列出“今日观察清单”（2至4项）。中文表达简洁、审慎。不要把相关性写成因果，也不要给个性化投资建议。每条新闻附上对应来源域名和原文链接。
只使用提供的新闻材料，不声称已经阅读全文或独立核实。"""

    payload = {
        "model": MODEL,
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": "你是一名谨慎的新闻趋势编辑，严格区分事实与推断。"},
            {"role": "user", "content": prompt + "\n\n新闻素材：\n" +
             json.dumps(articles, ensure_ascii=False)},
        ],
    }
    request = urllib.request.Request(
        OPENAI_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    data = get_json(request.full_url, headers=request.headers)
    text = data["choices"][0]["message"]["content"].strip()
    if not text:
        raise RuntimeError("OpenAI returned an empty brief.")
    return text


def send_email(brief):
    api_key = os.environ["AGENTMAIL_API_KEY"]
    date = datetime.now().astimezone().strftime("%Y年%m月%d日")
    payload = {
        "to": RECIPIENT,
        "subject": f"每日趋势简报｜{date}",
        "text": brief,
    }
    request = urllib.request.Request(
        AGENTMAIL_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            print(f"AgentMail accepted message (HTTP {response.status}).")
            # Do not print response bodies: they can contain private message metadata.
    except urllib.error.HTTPError as error:
        # Avoid echoing request headers or secrets into Actions logs.
        print(f"AgentMail request failed (HTTP {error.code}).", file=sys.stderr)
        raise


def main():
    articles = fetch_articles()
    print(f"Collected {len(articles)} GDELT article records.")
    brief = generate_brief(articles)
    print(f"Generated brief ({len(brief)} characters).")
    send_email(brief)


if __name__ == "__main__":
    main()

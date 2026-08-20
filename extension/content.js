function getMetaContent(selector) {
  const element = document.querySelector(selector);
  return element ? element.getAttribute("content") || "" : "";
}

function getFirstText(selectors) {
  for (const selector of selectors) {
    const element = document.querySelector(selector);

    if (element) {
      const text = element.textContent.trim();

      if (text) {
        return text;
      }
    }
  }

  return "";
}

function getArticleTitle() {
  return (
    getMetaContent('meta[property="og:title"]') ||
    getMetaContent('meta[name="twitter:title"]') ||
    getFirstText([
      "h1",
      "article h1",
      '[itemprop="headline"]'
    ]) ||
    document.title ||
    ""
  );
}

function getPublisher() {
  return (
    getMetaContent('meta[property="og:site_name"]') ||
    getMetaContent('meta[name="publisher"]') ||
    window.location.hostname
  );
}

function getAuthor() {
  return (
    getMetaContent('meta[name="author"]') ||
    getMetaContent('meta[property="article:author"]') ||
    getFirstText([
      '[rel="author"]',
      '[itemprop="author"]',
      ".author",
      ".byline"
    ])
  );
}

function getPublicationDate() {
  return (
    getMetaContent('meta[property="article:published_time"]') ||
    getMetaContent('meta[name="date"]') ||
    getMetaContent('meta[name="publish-date"]') ||
    getMetaContent('meta[itemprop="datePublished"]') ||
    ""
  );
}

function getArticleText() {
  const article = document.querySelector("article");

  if (article) {
    return article.innerText.trim();
  }

  const main = document.querySelector("main");

  if (main) {
    return main.innerText.trim();
  }

  const paragraphs = Array.from(document.querySelectorAll("p"))
    .map((paragraph) => paragraph.innerText.trim())
    .filter(Boolean);

  return paragraphs.join("\n\n").trim();
}

function extractArticle() {
  return {
    title: getArticleTitle(),
    publisher: getPublisher(),
    author: getAuthor(),
    publication_date: getPublicationDate(),
    url: window.location.href,
    text: getArticleText()
  };
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type !== "VERIFY_ARTICLE") {
    return;
  }

  const article = extractArticle();

  if (!article.title && !article.text) {
    sendResponse({
      success: false,
      error: "We couldn't reliably identify the article on this page."
    });

    return;
  }

  sendResponse({
    success: true,
    article
  });
});

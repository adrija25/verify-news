function extractPageData() {
  const title =
    document.querySelector("meta[property='og:title']")?.content ||
    document.querySelector("h1")?.innerText ||
    document.title ||
    "";

  const description =
    document.querySelector("meta[name='description']")?.content ||
    document.querySelector("meta[property='og:description']")?.content ||
    "";

  const author =
    document.querySelector("meta[name='author']")?.content ||
    document.querySelector("[rel='author']")?.innerText ||
    "";

  const publishedTime =
    document.querySelector("meta[property='article:published_time']")?.content ||
    document.querySelector("time")?.getAttribute("datetime") ||
    document.querySelector("time")?.innerText ||
    "";

  const article =
    document.querySelector("article") ||
    document.querySelector("[role='main']") ||
    document.querySelector("main");

  const articleText = article
    ? article.innerText
    : document.body.innerText;

  return {
    url: window.location.href,
    title: title.trim(),
    description: description.trim(),
    author: author.trim(),
    publishedTime: publishedTime.trim(),
    articleText: articleText.trim()
  };
}


chrome.runtime.onMessage.addListener(
  function (message, sender, sendResponse) {

    if (message?.action === "extractPageData") {
      sendResponse({
        success: true,
        data: extractPageData()
      });
    }

    return true;
  }
);

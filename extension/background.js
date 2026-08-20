chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type !== "ARTICLE_EXTRACTED") {
    return;
  }

  sendResponse({
    success: true,
    article: message.article || null
  });
});

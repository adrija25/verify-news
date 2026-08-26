chrome.runtime.onMessage.addListener(
  function (message, sender, sendResponse) {

    if (message?.action === "getCurrentPageData") {
      chrome.tabs.query(
        {
          active: true,
          currentWindow: true
        },
        function (tabs) {

          if (!tabs || !tabs[0]?.id) {
            sendResponse({
              success: false,
              error: "No active tab found."
            });
            return;
          }

          chrome.tabs.sendMessage(
            tabs[0].id,
            {
              action: "extractPageData"
            },
            function (response) {

              if (chrome.runtime.lastError) {
                sendResponse({
                  success: false,
                  error: chrome.runtime.lastError.message
                });
                return;
              }

              sendResponse(response);
            }
          );
        }
      );

      return true;
    }
  }
);

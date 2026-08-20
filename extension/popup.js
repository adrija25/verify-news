const BACKEND_URL = "http://127.0.0.1:8000";

const verifyArticleButton = document.getElementById("verifyArticleButton");
const verifyClaimButton = document.getElementById("verifyClaimButton");
const submitClaimButton = document.getElementById("submitClaimButton");
const historyButton = document.getElementById("historyButton");

const claimSection = document.getElementById("claimSection");
const claimInput = document.getElementById("claimInput");

const statusIndicator = document.getElementById("statusIndicator");
const statusText = document.getElementById("statusText");

function setBackendStatus(connected) {
  if (connected) {
    statusIndicator.style.background = "#16a34a";
    statusText.textContent = "Backend: Connected";
  } else {
    statusIndicator.style.background = "#dc2626";
    statusText.textContent = "Backend: Offline";
  }
}

async function checkBackend() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/health`, {
      method: "GET"
    });

    if (!response.ok) {
      throw new Error("Backend health check failed.");
    }

    setBackendStatus(true);
  } catch (error) {
    setBackendStatus(false);
  }
}

verifyArticleButton.addEventListener("click", () => {
  chrome.tabs.query(
    {
      active: true,
      currentWindow: true
    },
    (tabs) => {
      const activeTab = tabs[0];

      if (!activeTab || !activeTab.id) {
        return;
      }

      chrome.tabs.sendMessage(
        activeTab.id,
        {
          type: "VERIFY_ARTICLE"
        },
        () => {
          if (chrome.runtime.lastError) {
            statusText.textContent =
              "Unable to read this page. Try verifying a claim manually.";
          }
        }
      );
    }
  );
});

verifyClaimButton.addEventListener("click", () => {
  claimSection.hidden = false;
  claimInput.focus();
});

submitClaimButton.addEventListener("click", () => {
  const claim = claimInput.value.trim();

  if (!claim) {
    statusText.textContent = "Enter a claim before verifying.";
    claimInput.focus();
    return;
  }

  statusText.textContent = "Claim verification will be connected next.";
});

historyButton.addEventListener("click", () => {
  statusText.textContent = "Verification history will be connected next.";
});

checkBackend();

const API_BASE_URL = "http://localhost:8000";

const claimInput = document.getElementById("claim");
const verifyButton = document.getElementById("verifyButton");

const statusElement = document.getElementById("status");
const resultElement = document.getElementById("result");

const verdictElement = document.getElementById("verdict");
const confidenceElement = document.getElementById("confidence");
const explanationElement = document.getElementById("explanation");


function showStatus(message) {
  statusElement.textContent = message;
  statusElement.style.display = "block";
}


function hideStatus() {
  statusElement.style.display = "none";
}


function showResult(data) {
  verdictElement.textContent = formatVerdict(data.verdict);

  confidenceElement.textContent =
    formatConfidence(data.confidence);

  explanationElement.textContent =
    data.explanation || "No explanation available.";

  resultElement.style.display = "block";
}


function hideResult() {
  resultElement.style.display = "none";
}


function formatVerdict(verdict) {
  if (!verdict) {
    return "UNVERIFIED";
  }

  return verdict.replaceAll("_", " ");
}


function formatConfidence(confidence) {
  if (!confidence) {
    return "Unknown";
  }

  return (
    confidence.charAt(0) +
    confidence.slice(1).toLowerCase()
  );
}


async function verifyClaim() {
  const claim = claimInput.value.trim();

  hideResult();

  if (!claim) {
    showStatus("Please enter a claim to verify.");
    return;
  }

  verifyButton.disabled = true;

  showStatus("Checking available evidence...");

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/verify/claim`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          claim: claim
        })
      }
    );


    let data = null;

    try {
      data = await response.json();
    } catch (error) {
      data = null;
    }


    if (!response.ok) {
      const message =
        data && data.detail
          ? data.detail
          : "The verification request failed.";

      throw new Error(message);
    }


    hideStatus();

    showResult(data);

  } catch (error) {

    hideResult();

    if (error instanceof TypeError) {

      showStatus(
        "Verify News could not connect to the backend. " +
        "Make sure the FastAPI server is running."
      );

    } else {

      showStatus(
        error.message ||
        "Something went wrong while verifying the claim."
      );
    }

  } finally {

    verifyButton.disabled = false;
  }
}


verifyButton.addEventListener(
  "click",
  verifyClaim
);


claimInput.addEventListener(
  "keydown",
  function (event) {

    if (
      event.key === "Enter" &&
      (event.ctrlKey || event.metaKey)
    ) {
      verifyClaim();
    }

  }
);

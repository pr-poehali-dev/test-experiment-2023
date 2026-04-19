const ENDPOINT = "https://errors.poehali.dev/api/report";

export function initErrorReporter() {
  window.addEventListener("unhandledrejection", (event) => {
    reportError(String(event.reason));
  });

  window.onerror = (message, source, lineno, colno, error) => {
    reportError(error?.stack ?? String(message));
  };
}

function reportError(stack: string) {
  fetch(ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      stack,
      url: window.location.href,
      userAgent: navigator.userAgent,
      screen: `${screen.width}x${screen.height}`,
    }),
  }).catch(() => {});
}

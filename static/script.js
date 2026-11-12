const uploadForm = document.getElementById("uploadForm");
const askForm = document.getElementById("askForm");
uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const status = document.getElementById("uploadStatus");
  status.textContent = "Indexing...";
  const body = new FormData();
  body.append("file", document.getElementById("document").files[0]);
  try {
    const response = await fetch("/api/upload", {method: "POST", body});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Upload failed");
    status.textContent = `Indexed ${data.filename}: ${data.chunks} chunks`;
  } catch (error) {status.textContent = error.message;}
});
askForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const status = document.getElementById("askStatus");
  const answer = document.getElementById("answer");
  const sources = document.getElementById("sources");
  status.textContent = "Searching and verifying...";
  answer.textContent = "";
  sources.replaceChildren();
  try {
    const response = await fetch("/api/ask", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({question: document.getElementById("question").value})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Request failed");
    answer.textContent = data.answer;
    status.textContent = `Verified: ${data.verified ? "Yes" : "No"} | Retrieved: ${data.retrieved_count} | Relevant: ${data.relevant_count}`;
    data.sources.forEach((source) => {
      const article = document.createElement("article");
      const heading = document.createElement("strong");
      heading.textContent = `${source.source} (${source.id})`;
      const excerpt = document.createElement("p");
      excerpt.textContent = source.text;
      article.append(heading, excerpt);
      sources.append(article);
    });
  } catch (error) {status.textContent = error.message;}
});

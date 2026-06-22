const BOT_NAME = "Einstein";
const USER_NAME = "User";

const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("message-input");
const sendButtonEl = document.getElementById("send-button");
const resetButtonEl = document.getElementById("reset-button");
const statusEl = document.getElementById("status");

let chatHistory = [];

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

function appendMessage(sender, message) {
  const row = document.createElement("div");
  row.className = `message-row ${sender === USER_NAME ? "user" : "bot"}`;

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  const senderEl = document.createElement("span");
  senderEl.className = "sender";
  senderEl.textContent = sender;

  const textEl = document.createElement("span");
  textEl.textContent = message;

  bubble.appendChild(senderEl);
  bubble.appendChild(textEl);
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setLoading(isLoading) {
  sendButtonEl.disabled = isLoading;
  inputEl.disabled = isLoading;
  resetButtonEl.disabled = isLoading;
}

async function sendMessage(message) {
  setLoading(true);
  setStatus("Einstein is thinking...");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        chat_history: chatHistory,
        bot_name: BOT_NAME,
        user_name: USER_NAME,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }

    chatHistory.push({ sender: USER_NAME, message });
    chatHistory.push({ sender: data.sender || BOT_NAME, message: data.message });
    appendMessage(data.sender || BOT_NAME, data.message);
    setStatus("");
  } catch (error) {
    console.error(error);
    setStatus(error.message || "Something went wrong", true);
  } finally {
    setLoading(false);
    inputEl.focus();
  }
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = inputEl.value.trim();
  if (!message) return;

  inputEl.value = "";
  appendMessage(USER_NAME, message);
  await sendMessage(message);
});

inputEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    formEl.requestSubmit();
  }
});

resetButtonEl.addEventListener("click", () => {
  chatHistory = [];
  messagesEl.innerHTML = "";
  setStatus("");
  appendMessage(BOT_NAME, "Hi, I’m Einstein. What would you like to talk about?");
  inputEl.focus();
});

appendMessage(BOT_NAME, "Hi, I’m Einstein. What would you like to talk about?");
inputEl.focus();

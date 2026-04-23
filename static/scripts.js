document.addEventListener("DOMContentLoaded", () => {
  const chatBody = document.querySelector(".chat-body");
  const messageInput = document.querySelector(".message-input");
  const sendMessageButton = document.querySelector("#send-message");
  const chatbotToggler = document.querySelector("#chatbot-toggler");
  const closeChatbot = document.querySelector("#close-chatbot");
  const messageForm = document.querySelector(".message-form");
  const heroChatOpen = document.querySelector("#hero-chat-open");

  if (!chatBody || !messageInput || !sendMessageButton || !chatbotToggler || !closeChatbot || !messageForm) {
    console.error("Chatbot UI initialization failed: missing DOM elements.");
    return;
  }

  const API_URL = "/get";
  const initialInputHeight = messageInput.scrollHeight;

  const createMessageElement = (content, ...classes) => {
    const div = document.createElement("div");
    div.classList.add("message", ...classes);
    div.innerHTML = content;
    return div;
  };

  const scrollToBottom = () => {
    chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
  };

  const generateBotResponse = async (incomingMessageDiv, promptMessage) => {
    const messageElement = incomingMessageDiv.querySelector(".message-text");
    const formData = new FormData();
    formData.append("msg", promptMessage);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Server error");

      const botResponse = await response.text();
      messageElement.innerText = botResponse;
    } catch (error) {
      console.error(error);
      messageElement.innerText = "Sorry, I couldn't process your request. Please try again.";
      messageElement.style.color = "#ff0000";
    } finally {
      incomingMessageDiv.classList.remove("thinking");
      scrollToBottom();
    }
  };

  const handleOutgoingMessage = (e) => {
    e.preventDefault();

    const message = messageInput.value.trim();
    if (!message) return;

    messageInput.value = "";
    messageInput.style.height = `${initialInputHeight}px`;

    const userMessageDiv = createMessageElement(
      `<div class="message-content">
        <div class="message-bubble">${message}</div>
        <span class="message-time">${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
      </div>`,
      "user-message"
    );

    chatBody.appendChild(userMessageDiv);
    scrollToBottom();

    const botMessageDiv = createMessageElement(
      `<div class="bot-avatar">
          <span class="material-symbols-rounded">health_and_safety</span>
        </div>
        <div class="message-content">
          <div class="message-bubble bot-bubble">
            <div class="message-text">
              <div class="thinking-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </div>
          </div>
          <span class="message-time">typing...</span>
        </div>`,
      "bot-message",
      "thinking"
    );

    chatBody.appendChild(botMessageDiv);
    scrollToBottom();
    generateBotResponse(botMessageDiv, message);
  };

  messageForm.addEventListener("submit", handleOutgoingMessage);
  sendMessageButton.addEventListener("click", handleOutgoingMessage);

  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      handleOutgoingMessage(e);
    }
  });

  messageInput.addEventListener("input", () => {
    messageInput.style.height = `${initialInputHeight}px`;
    messageInput.style.height = `${Math.min(messageInput.scrollHeight, 120)}px`;
  });

  chatbotToggler.addEventListener("click", () => {
    document.body.classList.toggle("show-chatbot");
  });

  if (heroChatOpen) {
    heroChatOpen.addEventListener("click", () => {
      document.body.classList.add("show-chatbot");
      document.body.scrollIntoView({ behavior: "smooth" });
    });
  }

  closeChatbot.addEventListener("click", () => {
    document.body.classList.remove("show-chatbot");
  });
});

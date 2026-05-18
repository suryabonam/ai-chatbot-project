import { useState } from "react";
import "./App.css";

import Header from "./components/Header";
import ChatBox from "./components/ChatBox";
import InputBox from "./components/InputBox";

import Login from "./components/Login";
import Signup from "./components/Signup";

function App() {

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // Authentication states
  const [showLogin, setShowLogin] = useState(true);
  const [showSignup, setShowSignup] = useState(false);

  // ---------------- LOGIN PAGE ----------------

  if (showLogin === true && showSignup === false) {
    return (
      <Login
        setShowLogin={setShowLogin}
        setShowSignup={setShowSignup}
      />
    );
  }

  // ---------------- SIGNUP PAGE ----------------

  if (showSignup === true) {
    return (
      <Signup
        setShowLogin={setShowLogin}
        setShowSignup={setShowSignup}
      />
    );
  }

  // ---------------- SEND MESSAGE ----------------

  const sendMessage = async () => {

    if (!input.trim()) return;

    // Save input before clearing
    const userText = input;

    // User message object
    const userMessage = {
      sender: "user",
      text: userText
    };

    // Add user message to chat
    setMessages((prev) => [...prev, userMessage]);

    // Clear input instantly
    setInput("");

    // Show typing indicator
    setLoading(true);

    try {

      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: userText
        })
      });

      const data = await response.json();

      // Bot response
      const botMessage = {
        sender: "bot",
        text: data.response
      };

      setMessages((prev) => [...prev, botMessage]);

    } catch (error) {

      console.error(error);

      const errorMessage = {
        sender: "bot",
        text: "Error connecting to server"
      };

      setMessages((prev) => [...prev, errorMessage]);
    }

    // Stop typing
    setLoading(false);
  };

  // ---------------- CLEAR CHAT ----------------

  const clearChat = () => {
    setMessages([]);
  };

  // ---------------- LOGOUT ----------------

  const logout = () => {

    setShowLogin(true);
    setShowSignup(false);

    setMessages([]);
    setInput("");
  };

  // ---------------- MAIN CHATBOT UI ----------------

  return (
    <div className="app">

      <div className="chat-container">

        <Header
          clearChat={clearChat}
          logout={logout}
        />

        {messages.length === 0 ? (

          <div className="welcome-screen">

            <h2>🐟 Welcome to Aquaculture AI Assistant</h2>

            <p>Ask me about:</p>

            <ul>
              <li>Fish Farming</li>
              <li>Shrimp Feeding</li>
              <li>Water Quality</li>
              <li>Fish Diseases</li>
              <li>Pond Management</li>
            </ul>

          </div>

        ) : (

          <ChatBox
            messages={[
              ...messages,
              ...(loading
                ? [{ sender: "bot", text: "Bot is typing..." }]
                : [])
            ]}
          />

        )}

        <InputBox
          input={input}
          setInput={setInput}
          sendMessage={sendMessage}
        />

      </div>

    </div>
  );
}

export default App;
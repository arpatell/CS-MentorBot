function addMessage(role, content) {
    var chatLog = document.getElementById("chat-log");
    var messageDiv = document.createElement("div");
    messageDiv.className = "message " + role + "-message";
    messageDiv.textContent = content;
    chatLog.appendChild(messageDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
}

function askQuestion() {
    var questionInput = document.getElementById("question");
    var question = questionInput.value;
    addMessage("user", "> " + question);

    addMessage("assistant", "CS MentorBot is typing...");

    fetch("/api/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: question })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            replaceMessage("CS MentorBot is typing...", "Error: " + data.message);
        } else {
            var response = data.response;
            replaceMessage("CS MentorBot is typing...", response);
        }
    })
    .catch(error => {
        console.error("Error fetching response:", error);
    });

    questionInput.value = ""; 
    return false;
}

function replaceMessage(originalMessage, newMessage) {
    var chatLog = document.getElementById("chat-log");
    var messages = chatLog.children;
    for (var i = 0; i < messages.length; i++) {
        if (messages[i].textContent === originalMessage) {
            messages[i].textContent = newMessage;
            break;
        }
    }
}

function updateChatLog(previousQuestionsAndAnswers) {
    for (var i = 0; i < previousQuestionsAndAnswers.length; i++) {
        var question = previousQuestionsAndAnswers[i][0];
        var answer = previousQuestionsAndAnswers[i][1];
        addMessage("user", "> " + question);
        addMessage("assistant", answer);
    }
}
function clearChat() {
    var chatLog = document.getElementById("chat-log");
    chatLog.innerHTML = "";
    previous_questions_and_answers = [];
}

window.onload = function() {
    var previousQuestionsAndAnswers = JSON.parse('{{ previous_questions_and_answers | tojson | safe }}');
    updateChatLog(previousQuestionsAndAnswers);
};
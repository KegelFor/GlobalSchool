document.addEventListener("DOMContentLoaded", function () {
    let messagesContainer = document.createElement("div");
    messagesContainer.id = "messages-container";
    document.body.appendChild(messagesContainer);

    let djangoMessages = document.querySelectorAll(".alert");

    djangoMessages.forEach(function (message) {
        messagesContainer.appendChild(message);
        setTimeout(function () {
            message.style.opacity = "0";
            message.style.transform = "translateY(-20px)";
            setTimeout(function () {
                message.remove();
            }, 500);
        }, 3000);
    });
});






$(document).ready(function() {
    setupWebSocket();
});

function setupWebSocket() {
    // Токен теперь передается через cookies, поэтому не нужно вручную добавлять его в URL
    const socket = new WebSocket('ws://' + window.location.host + '/ws/notifications/');

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        addNotification(data);
    };

    socket.onopen = function(e) {
        console.log("Соединение WebSocket установлено.");
    };

    socket.onclose = function(e) {
        console.log("Соединение WebSocket закрыто.");
    };

    socket.onerror = function(e) {
        console.error("Ошибка WebSocket:", e);
    };
}

function addNotification(data) {
    const notificationList = $('#notification-list');
    const newNotification = `
        <li class="notification-item" data-id="${data.id}">
            ${data.message} - ${data.created_at}
            <button class="close-notification" onclick="closeNotification(this)">×</button>
        </li>`;
    notificationList.prepend(newNotification); // Добавляем в начало списка
}

window.closeNotification = function(button) {
    $(button).parent().remove();
};
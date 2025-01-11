// static/js/notifications.js

const userId = document.body.getAttribute('data-user-id'); // Получите ID пользователя
const socket = new WebSocket(`ws://${window.location.host}/ws/notifications/`);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    alert(data.message); // Показать уведомление
};

// Обработка открытия соединения
socket.onopen = function(e) {
    console.log("Соединение WebSocket установлено.");
};

// Обработка закрытия соединения
socket.onclose = function(e) {
    console.log("Соединение WebSocket закрыто.");
};

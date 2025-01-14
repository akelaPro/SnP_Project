const userId = document.body.getAttribute('data-user-id'); // Получите ID пользователя
const socket = new WebSocket(`ws://${window.location.host}/ws/notifications/`);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    addNotification(data); // Добавить уведомление в список
};

socket.onopen = function(e) {
    console.log("Соединение WebSocket установлено.");
};

socket.onclose = function(e) {
    console.log("Соединение WebSocket закрыто.");
};

// Функция для добавления уведомления в список
function addNotification(data) {
    const notificationList = document.getElementById('notification-list');
    const newNotification = document.createElement('li');
    newNotification.className = 'notification-item';
    newNotification.setAttribute('data-id', data.id);
    newNotification.innerHTML = `${data.message} - ${data.created_at} <button class="close-notification" onclick="closeNotification(this)">×</button>`;
    notificationList.appendChild(newNotification);
}

// Функция для закрытия уведомления
function closeNotification(button) {
    const notificationItem = button.parentElement;
    notificationItem.remove(); // Удалить элемент из DOM
    // Здесь вы можете добавить AJAX-запрос для удаления уведомления с сервера, если это необходимо
}

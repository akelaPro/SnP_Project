document.addEventListener('DOMContentLoaded', function() {
    const socket = new WebSocket('ws://127.0.0.1:8000/ws/notifications/');

    socket.onmessage = function(e) {
        console.log("Получено сообщение:", e.data); // Отладка
        const data = JSON.parse(e.data);
        addNotification(data);
    };

    socket.onopen = function(e) {
        console.log("Соединение WebSocket установлено.");
    };

    socket.onclose = function(e) {
        console.log("Соединение WebSocket закрыто.");
    };

    function addNotification(data) {
        const notificationList = document.getElementById('notification-list');
        if (!notificationList) {
            console.error("Элемент с id 'notification-list' не найден.");
            return;
        }

        const newNotification = document.createElement('li');
        newNotification.className = 'notification-item';
        newNotification.innerHTML = `${data.message} - ${data.created_at} <button class="close-notification" onclick="closeNotification(this)">×</button>`;
        notificationList.appendChild(newNotification);
    }

    window.closeNotification = function(button) {
        const notificationItem = button.parentElement; // Получаем родительский элемент (li)
        if (notificationItem) {
            notificationItem.remove(); // Удаляем элемент уведомления
        } else {
            console.error("Не удалось найти элемент уведомления для удаления.");
        }
    };
});

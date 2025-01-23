const socket = new WebSocket('ws://127.0.0.1:8080/ws/notifications/');


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

function addNotification(data) {
    const notificationList = document.getElementById('notification-list');
    const newNotification = document.createElement('li');
    newNotification.className = 'notification-item';
    newNotification.innerHTML = `${data.message} - ${data.created_at} <button class="close-notification" onclick="closeNotification(this)">×</button>`;
    notificationList.appendChild(newNotification);
}

function closeNotification(button) {
    const notificationItem = button.parentElement;
    notificationItem.remove(); 
}

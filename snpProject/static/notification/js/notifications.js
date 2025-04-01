$(document).ready(function() {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        alert("Пожалуйста, войдите в систему, чтобы видеть уведомления.");
        window.location.href = '/login/'; 
        return;
    }

    const socket = new WebSocket(`ws://127.0.0.1:8000/ws/notifications/?token=${token}`);

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
        const notificationList = $('#notification-list');
        const newNotification = `
            <li class="notification-item" data-id="${data.id}">
                ${data.message} - ${data.created_at}
                <button class="close-notification" onclick="closeNotification(this)">×</button>
            </li>`;
        notificationList.append(newNotification);
    }

    window.closeNotification = function(button) {
        $(button).parent().remove(); 
    };
});

$(document).ready(function() {
    verifyTokenAndSetupWebSocket();
});

async function verifyTokenAndSetupWebSocket() {
    try {
        const response = await fetch('/api/auth/verify/', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();
        
        if (data.is_authenticated) {
            setupWebSocket();
            loadInitialNotifications();
        } else {
            console.error("Пользователь не авторизован");
        }
    } catch (error) {
        console.error("Ошибка при проверке токена:", error);
    }
}

function setupWebSocket() {
    const socket = new WebSocket('ws://' + window.location.host + '/ws/notifications/');

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        addNotification(data);
    };

    socket.onopen = function(e) {
        console.log("WebSocket соединение установлено");
    };

    socket.onclose = function(e) {
        console.log("WebSocket соединение закрыто");
    };

    socket.onerror = function(e) {
        console.error("Ошибка WebSocket:", e);
    };
}

async function loadInitialNotifications() {
    try {
        const response = await fetch('/api/notifications/', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error('Не удалось загрузить уведомления');
        }

        const notifications = await response.json();
        console.log("Получены уведомления:", notifications); // Добавьте для отладки
        notifications.forEach(notification => {
            addNotification(notification);
        });
    } catch (error) {
        console.error("Ошибка при загрузке уведомлений:", error);
    }
}

function addNotification(data) {
    const notificationList = document.getElementById('notification-list');
    if (!notificationList) {
        console.error("Элемент notification-list не найден");
        return;
    }

    const newNotification = document.createElement('li');
    newNotification.className = 'notification-item';
    newNotification.dataset.id = data.id;
    
    newNotification.innerHTML = `
        ${data.message} - ${new Date(data.created_at).toLocaleString()}
        <button class="close-notification" onclick="closeNotification(this)">×</button>
    `;
    
    newNotification.addEventListener('click', function() {
        markNotificationAsRead(data.id);
    });
    
    notificationList.prepend(newNotification);
}

async function markNotificationAsRead(notificationId) {
    try {
        await fetch(`/notification/${notificationId}/mark_as_read/`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        });
    } catch (error) {
        console.error("Ошибка при отметке уведомления как прочитанного:", error);
    }
}

window.closeNotification = function(button) {
    const notificationItem = button.parentElement;
    const notificationId = notificationItem.dataset.id;
    
    // Опционально: можно отправить запрос на удаление
    // fetch(`/notification/${notificationId}/`, { method: 'DELETE' });
    
    notificationItem.remove();
};
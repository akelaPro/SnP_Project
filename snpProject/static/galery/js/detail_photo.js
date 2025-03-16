$(document).ready(function() {
    const photoId = window.location.pathname.split('/').filter(Boolean).pop();
    let accessToken = localStorage.getItem('accessToken');
    let refreshToken = localStorage.getItem('refreshToken'); // Единое имя переменной
    console.log("Initial accessToken:", accessToken); // Log initial accessToken
    console.log("Initial refreshToken:", refreshToken);

    // Элементы UI
    const commentForm = $('#comment-form');
    const likeButton = $('#like-button');
    const unlikeButton = $('#unlike-button');
    const loginPromptComment = $('#login-prompt-comment');
    const loginPromptLike = $('#login-prompt-like');
    const deletePhotoButton = $('#delete-photo-button');
    const restorePhotoButton = $('#restore-photo-button');
    const photoActions = $('#photo-actions');
    const timerDiv = $('#timer');
    const showAllCommentsButton = $('#show-all-comments-button');
    const hideAllCommentsButton = $('#hide-all-comments-button');

    let allCommentsLoaded = false;
    let tokenRefreshTimeout; // Для хранения таймера обновления токена
    let isRefreshing = false;
    let failedQueue = [];

    // ================== Auth System ==================

    function processQueue(error, token = null) {
        console.log("Processing queue:", failedQueue.length, "items. Error:", error); // Log queue processing
        failedQueue.forEach(prom => {
            if (error) {
                prom.reject(error);
            } else {
                prom.resolve(token);
            }
        });
        failedQueue = [];
    }

    // Перехватчик AJAX-запросов
    $.ajaxPrefilter(function(options, originalOptions, jqXHR) {
        if (!options.headers) options.headers = {};
        if (accessToken) {
            options.headers['Authorization'] = 'Bearer ' + accessToken;
            console.log("Adding Authorization header:", accessToken); // Log adding auth header
        }
    });

    // Глобальный обработчик ошибок
    $(document).ajaxError(function(event, jqXHR, ajaxSettings, thrownError) {
        console.log("AJAX Error:", jqXHR.status, ajaxSettings.url, thrownError); // Log AJAX errors
        if (jqXHR.status === 401 && !ajaxSettings._retry) {
            const originalOptions = ajaxSettings;
            console.log("Token expired. Attempting refresh..."); // Log token expiration

            if (isRefreshing) {
                console.log("Refresh already in progress. Adding to queue."); // Log queueing
                return new Promise(function(resolve, reject) {
                    failedQueue.push({ resolve, reject });
                }).then(token => {
                    console.log("Using refreshed token from queue."); // Log using token from queue
                    originalOptions.headers['Authorization'] = 'Bearer ' + token;
                    return $.ajax(originalOptions);
                }).catch(reject);
            }

            isRefreshing = true;
            originalOptions._retry = true;

            refreshTokenRequest()
                .then(newTokens => {
                    console.log("Token refreshed successfully.");
                    accessToken = newTokens.access;
                    refreshToken = newTokens.refresh; // Было refreshTokenValue
                    localStorage.setItem('accessToken', accessToken);
                    localStorage.setItem('refreshToken', refreshToken);
                    console.log("New accessToken:", accessToken); // Log new accessToken
                    originalOptions.headers['Authorization'] = 'Bearer ' + accessToken;
                    processQueue(null, accessToken);
                    isRefreshing = false;
                    scheduleTokenRefresh(120); // Обновляем таймер (2 минуты)
                    return $.ajax(originalOptions);
                })
                .catch(error => {
                    console.error("Error refreshing token:", error); // Log refresh errors
                    processQueue(error, null);
                    isRefreshing = false;
                    localStorage.removeItem('accessToken');
                    localStorage.removeItem('refreshToken');
                    console.log("Redirecting to login..."); // Log redirect
                    window.location.href = "{% url 'galery:login_template' %}";
                });
        }
    });

    function scheduleTokenRefresh(expiresIn) {
        if (tokenRefreshTimeout) clearTimeout(tokenRefreshTimeout);
        const refreshTime = (expiresIn - 30) * 1000; // Обновляем за 30 сек до истечения
        console.log("Scheduling token refresh in", refreshTime / 1000, "seconds"); // Log scheduling
        tokenRefreshTimeout = setTimeout(refreshTokenRequest, refreshTime);
    }

    // Глобальная функция refreshToken (объявление только здесь!)
    function refreshTokenRequest() { // Переименовано чтобы избежать конфликта
        return new Promise((resolve, reject) => {
            const currentRefreshToken = localStorage.getItem('refreshToken');
            if (!currentRefreshToken) {
                console.error("No refresh token found. Redirecting to login.");
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
                window.location.href = "{% url 'galery:login_template' %}";
                return reject("No refresh token");
            }

            const data = JSON.stringify({ refresh: currentRefreshToken });
            console.log("Attempting to refresh token...");

            $.ajax({
                url: '/api/refresh/',
                method: 'POST',
                contentType: 'application/json',
                data,
                headers: { 'X-CSRFToken': '{{ csrf_token }}' },
                success: function(data) {
                    console.log("Token refresh success:", data);
                    localStorage.setItem('accessToken', data.access);
                    localStorage.setItem('refreshToken', data.refresh);
                    accessToken = data.access; // Обновляем переменную верхнего уровня
                    refreshToken = data.refresh; // Обновляем переменную верхнего уровня
                    scheduleTokenRefresh(120);
                    resolve(data);
                },
                error: function(xhr) {
                    console.error("Failed to refresh token:", xhr);
                    localStorage.removeItem('refreshToken');
                    localStorage.removeItem('accessToken');
                    console.log("Redirecting to login after refresh failure...");
                    window.location.href = "{% url 'galery:login_template' %}";
                    reject(xhr);
                }
            });
        });
    }

    // ================== UI Functions ==================
    function updateAuthUI() {
        if (accessToken) {
            commentForm.show();
            likeButton.show();
            loginPromptComment.hide();
            loginPromptLike.hide();
        } else {
            commentForm.hide();
            likeButton.hide();
            unlikeButton.hide();
            loginPromptComment.show();
            loginPromptLike.show();
        }
    }

    // ================== Photo Loading ==================
    function loadPhotoDetails() {
        console.log("Loading photo details...");
        $.ajax({
            url: `/api/photos/${photoId}/?include_deleted=true`,
            method: 'GET',
            success: function(photo) {
                console.log("Photo details loaded successfully."); 
                $('#photo-title').text(photo.title);
                $('#photo-image').attr('src', photo.image || '');
                $('#photo-author').text(photo.author.username);
                $('#photo-author-avatar').attr('src', photo.author.avatar || '');
                $('#photo-description').text(photo.description);
                $('#votes-count').text(photo.votes_count || 0);

                window.canEdit = photo.can_edit;

                if (window.canEdit) {
                    if (photo.moderation === '1' && photo.deleted_at) {
                        deletePhotoButton.hide();
                        restorePhotoButton.show();
                    } else {
                        deletePhotoButton.show();
                        restorePhotoButton.hide();
                    }
                    photoActions.show();
                } else {
                    photoActions.hide();
                }

                if (photo.moderation === '1') {
                    handlePhotoDeletionTimer(photo.deletedAt);
                } else {
                    timerDiv.empty();
                }

                loadInitialComments();

                // Добавляем логику для отображения кнопок лайка/анлайка
                if (photo.has_liked) {
                    $('#like-button').hide();
                    $('#unlike-button').show().data('voteId', photo.votes[0] ? photo.votes[0] : null); // Assuming first vote is the user's
                } else {
                    $('#like-button').show();
                    $('#unlike-button').hide();
                }
            },
            error: function(xhr) {
                console.error('Ошибка при загрузке фотографии:', xhr.responseText);
                photoActions.hide();
            }
        });
    }

    function handlePhotoDeletionTimer(deletedAt) {
        const deleteTime = new Date(deletedAt).getTime() + 35000;
        const timerInterval = setInterval(updateTimer, 1000);

        function updateTimer() {
            const now = new Date().getTime();
            const remaining = deleteTime - now;

            if (remaining > 0) {
                const seconds = Math.floor(remaining / 1000);
                timerDiv.html(`
                    <div class="alert alert-warning">
                        Фото будет удалено через ${seconds} сек.
                        <button id="cancel-delete" class="btn btn-sm btn-success">Отменить</button>
                    </div>
                `);
            } else {
                timerDiv.html('<div class="alert alert-danger">Фото удалено</div>');
                clearInterval(timerInterval);
                deletePhotoButton.hide();
                restorePhotoButton.hide();
            }
        }

        updateTimer();
    }

    $('#delete-photo-button').click(function() {
        $.ajax({
            url: `/api/photos/${photoId}/delete_photo/`,
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            success: function() {
                window.location.href = '/galery/profile/';
            },
            error: function(xhr) {
                console.error('Ошибка при удалении фотографии:', xhr.responseText);
                alert('Ошибка при удалении фотографии.');
            }
        });
    });

    $('#restore-photo-button').click(function() {
        $.ajax({
            url: `/api/photos/${photoId}/restore_photo/`,
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            success: function(response) {
                loadPhotoDetails();
            },
            error: function(xhr) {
                console.error('Ошибка при восстановлении фотографии:', xhr.responseText);
                try {
                    const errorData = JSON.parse(xhr.responseText);
                    alert('Ошибка при восстановлении фотографии: ' + (errorData.detail || 'Неизвестная ошибка'));
                } catch (e) {
                    alert('Ошибка при восстановлении фотографии: ' + xhr.responseText);
                }
            }
        });
    });


    // ================== Comments System ==================
    function loadInitialComments() {
        console.log("Loading initial comments..."); // Log comment load start
        $.get(`/api/comments/?photo=${photoId}`)
            .done(comments => {
                console.log("Initial comments loaded successfully."); // Log success
                const commentsList = $('#comments-list');
                commentsList.empty();

                const rootComments = comments.filter(comment => !comment.parent);
                rootComments.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

                const initialRootComments = rootComments.slice(0, 2);

                initialRootComments.forEach(comment => {
                    commentsList.append(buildCommentHTML(comment, comments));
                });

                // Показываем кнопку "Показать все комментарии", если есть больше 2 корневых комментариев
                showAllCommentsButton.toggle(rootComments.length > 2);
            })
            .fail(xhr => console.error('Ошибка при загрузке комментариев:', xhr.responseText));
    }

    function loadAllComments() {
        console.log("Loading all comments..."); 
        $.get(`/api/comments/?photo=${photoId}`)
            .done(comments => {
                console.log("All comments loaded successfully."); 
                const commentsList = $('#comments-list');
                commentsList.empty();

              
                const rootComments = comments.filter(comment => !comment.parent);
                rootComments.forEach(comment => {
                    commentsList.append(buildCommentHTML(comment, comments));
                });

                showAllCommentsButton.hide();
                hideAllCommentsButton.show();
                allCommentsLoaded = true;
            })
            .fail(xhr => console.error('Ошибка при загрузке всех комментариев:', xhr.responseText));
    }

    function buildCommentHTML(comment, allComments, level = 0) {
        let html = `
            <li id="comment-${comment.id}" style="margin-left: ${level * 30}px">
                ${comment.text} - ${comment.author.username}
                <button class="reply-button" data-comment-id="${comment.id}">Ответить</button>`;

        const replies = allComments.filter(c => c.parent === comment.id);
        if (replies.length > 0) {
            const repliesVisible = localStorage.getItem(`repliesVisible-${comment.id}`) === 'true';
            html += `
                <button class="toggle-replies-button" data-comment-id="${comment.id}">
                    ${repliesVisible ? 'Скрыть ответы' : 'Показать ответы'}
                </button>
                <ul class="replies" id="replies-${comment.id}" ${repliesVisible ? '' : 'style="display: none;"'}>
                    ${replies.map(reply => buildCommentHTML(reply, allComments, level + 1)).join('')}
                </ul>`;
        }

        return html + '</li>';
    }

    $(document).on('submit', '[id^="reply-form-"]', function(e) {
        console.log('Форма ответа отправлена');
        e.preventDefault();
        const parentId = $(this).data('parent-id');
        const text = $(this).find('.reply-text').val();

        const data = JSON.stringify({
            text: text,
            photo: photoId,
            parent: parentId
        });

        $.ajax({
            url: `/api/comments/`,
            type: 'POST',
            contentType: 'application/json',
            data,
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            success: function() {
                loadInitialComments();
                $(this).find('textarea').val('');
            }
        });
    });

    $(document).on('click', '.reply-button', function() {
        const commentId = $(this).data('comment-id');
        const replyForm = `
            <form id="reply-form-${commentId}" class="reply-form" data-parent-id="${commentId}">
                <textarea class="reply-text"></textarea>
                <button type="submit">Отправить ответ</button>
                <button type="button" class="cancel-reply">Отменить</button>
            </form>
        `;
        $(this).after(replyForm);
    });

    $(document).on('click', '.cancel-reply', function() {
        $(this).closest('.reply-form').remove();
    });

    function hideAllComments() {
        $('#comments-list').empty();
        showAllCommentsButton.show();
        hideAllCommentsButton.hide();
        loadInitialComments();
    }

    // ================== Event Handlers ==================

    showAllCommentsButton.click(function() {
        loadAllComments();
    });


    hideAllCommentsButton.click(function() {
        hideAllComments();
    });

    $(document).on('click', '.toggle-replies-button', function() {
        const commentId = $(this).data('comment-id');
        const repliesContainer = $(`#replies-${commentId}`);
        const newVisibility = !repliesContainer.is(':visible');

        repliesContainer.toggle(newVisibility);
        $(this).text(newVisibility ? 'Скрыть ответы' : 'Показать ответы');
        localStorage.setItem(`repliesVisible-${commentId}`, newVisibility);
    });

    $('#comment-form').submit(function(e) {
        e.preventDefault();
        const text = $(this).find('textarea').val();
        const data = JSON.stringify({ text, photo: photoId });
        $.ajax({
            url: `/api/comments/`,
            type: 'POST',
            contentType: 'application/json',
            data,
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            success: () => {
                loadInitialComments();
                $(this).find('textarea').val('');
            }
        });
    });

    $('#like-button').click(function() {
        const data = JSON.stringify({ photo: photoId });

        // Check if accessToken exists
        if (!accessToken) {
            console.error('Токен доступа отсутствует');
            window.location.href = "{% url 'galery:login_template' %}";
            return;
        }

        $.ajax({
            url: `/api/votes/`,
            method: 'POST', // Используем POST для создания лайка
            data,
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}' // Отправляем CSRF-токен
            },
            success: function(response) {
                const voteId = response.id;
                $('#votes-count').text(parseInt($('#votes-count').text()) + 1);
                $('#like-button').hide(); 
                $('#unlike-button').show().data('voteId', voteId); 
            },
            error: function(xhr) {
                console.error('Ошибка при постановке лайка:', xhr.responseText);
            }
        });
    });

    $('#unlike-button').click(function() {
        const voteId = $(this).data('voteId');
        $.ajax({
                url: `/api/votes/${voteId}/`,
                type: 'DELETE',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                },
            })
            .done(() => {
                $('#votes-count').text(parseInt($('#votes-count').text()) - 1);
                $(this).hide();
                $('#like-button').show();
            })
            .fail(function(xhr) {
                console.error('Ошибка при удалении лайка:', xhr.responseText);
            });
    });


    // ================== Initialization ==================
    loadPhotoDetails();
    updateAuthUI();
    if (accessToken) {
        scheduleTokenRefresh(120);
    }
});
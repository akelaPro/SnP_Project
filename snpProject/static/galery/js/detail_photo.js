$(document).ready(function() {
    const photoId = window.location.pathname.split('/').filter(Boolean).pop();
    let accessToken = localStorage.getItem('accessToken');
    let refreshToken = localStorage.getItem('refreshToken');
    console.log("Initial accessToken:", accessToken);
    console.log("Initial refreshToken:", refreshToken);

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
    let tokenRefreshTimeout;
    let isRefreshing = false;
    let failedQueue = [];

    // Auth System (Your existing auth logic)
    function processQueue(error, token = null) {
        console.log("Processing queue:", failedQueue.length, "items. Error:", error);
        failedQueue.forEach(prom => {
            if (error) {
                prom.reject(error);
            } else {
                prom.resolve(token);
            }
        });
        failedQueue = [];
    }

    $.ajaxPrefilter(function(options, originalOptions, jqXHR) {
        if (!options.headers) options.headers = {};
        if (accessToken) {
            options.headers['Authorization'] = 'Bearer ' + accessToken;
            console.log("Adding Authorization header:", accessToken);
        }
    });

    $(document).ajaxError(function(event, jqXHR, ajaxSettings, thrownError) {
        console.log("AJAX Error:", jqXHR.status, ajaxSettings.url, thrownError);
        if (jqXHR.status === 401 && !ajaxSettings._retry) {
            const originalOptions = ajaxSettings;
            console.log("Token expired. Attempting refresh...");

            if (isRefreshing) {
                console.log("Refresh already in progress. Adding to queue.");
                return new Promise(function(resolve, reject) {
                    failedQueue.push({ resolve, reject });
                }).then(token => {
                    console.log("Using refreshed token from queue.");
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
                    refreshToken = newTokens.refresh;
                    localStorage.setItem('accessToken', accessToken);
                    localStorage.setItem('refreshToken', refreshToken);
                    console.log("New accessToken:", accessToken);
                    originalOptions.headers['Authorization'] = 'Bearer ' + accessToken;
                    processQueue(null, accessToken);
                    isRefreshing = false;
                    scheduleTokenRefresh(120);
                    return $.ajax(originalOptions);
                })
                .catch(error => {
                    console.error("Error refreshing token:", error);
                    processQueue(error, null);
                    isRefreshing = false;
                    localStorage.removeItem('accessToken');
                    localStorage.removeItem('refreshToken');
                    console.log("Redirecting to login...");
                    window.location.href = "{% url 'galery:login_template' %}";
                });
        }
    });

    function scheduleTokenRefresh(expiresIn) {
        if (tokenRefreshTimeout) clearTimeout(tokenRefreshTimeout);
        const refreshTime = (expiresIn - 30) * 1000;
        console.log("Scheduling token refresh in", refreshTime / 1000, "seconds");
        tokenRefreshTimeout = setTimeout(refreshTokenRequest, refreshTime);
    }

    function refreshTokenRequest() {
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
                    accessToken = data.access;
                    refreshToken = data.refresh;
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


    // UI Functions
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

    // Photo Loading
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

                // Заполняем форму редактирования
                $('#edit-title').val(photo.title);
                $('#edit-description').val(photo.description);

                window.canEdit = photo.can_edit;

                if (window.canEdit) {
                    // Условие для отображения кнопок
                    if (photo.moderation === '1' && photo.deleted_at) {
                        deletePhotoButton.hide();
                        restorePhotoButton.show();
                    } else {
                        deletePhotoButton.show();
                        restorePhotoButton.hide();
                    }
                    photoActions.show();
                    $('#edit-photo-button').show(); // Показываем кнопку редактирования
                } else {
                    photoActions.hide();
                    $('#edit-photo-button').hide(); // Скрываем кнопку редактирования
                }
            },
            error: function(xhr) {
                console.error('Ошибка при загрузке фотографии:', xhr.responseText);
                photoActions.hide();
            }
        });
    }
    
    $('#delete-photo-button').click(function() {
        $.ajax({
            url: `/api/photos/${photoId}/`,
            method: 'DELETE',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            success: function() {
                deletePhotoButton.hide();
                restorePhotoButton.show();
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
                loadPhotoDetails(); // Обновляем информацию о фото, включая отображение кнопок
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

    // Comments System
    function loadInitialComments() {
        console.log("Loading initial comments...");
        $.get(`/api/comments/?photo=${photoId}`)
            .done(comments => {
                console.log("Initial comments loaded successfully.");
                const commentsList = $('#comments-list');
                commentsList.empty();

                const rootComments = comments.filter(comment => !comment.parent);
                rootComments.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

                const initialRootComments = rootComments.slice(0, 2);

                initialRootComments.forEach(comment => {
                    commentsList.append(buildCommentHTML(comment, comments));
                });

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
        const replies = allComments.filter(c => c.parent === comment.id);
        const repliesVisible = localStorage.getItem(`repliesVisible-${comment.id}`) === 'true';
        let html = `
            <li id="comment-${comment.id}" style="margin-left: ${level * 30}px; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px;">
                <div>
                    <strong>${comment.author.username}</strong>: ${comment.text}
                </div>
                <div style="font-size: smaller; color: #888;">
                    ${new Date(comment.created_at).toLocaleString()}
                    <button class="reply-button btn btn-sm btn-outline-secondary" data-comment-id="${comment.id}">Ответить</button>
                    
                    
                </div>
        `;

        if (comment.can_delete) {
            html += `
                <div style="margin-top: 5px;">
                <button class="edit-comment-button btn btn-sm btn-outline-primary" data-comment-id="${comment.id}">Редактировать</button>
                <button class="delete-comment-button btn btn-sm btn-outline-danger" data-comment-id="${comment.id}">Удалить</button>
                </div>
            `;
        }
        if (replies.length > 0) {
            html += `
                <button class="toggle-replies-button btn btn-sm btn-link" data-comment-id="${comment.id}">
                    ${repliesVisible ? 'Скрыть ответы' : 'Показать ответы'}
                </button>
                <ul class="replies" id="replies-${comment.id}" ${repliesVisible ? '' : 'style="display: none;"'}>
                    ${replies.map(reply => buildCommentHTML(reply, allComments, level + 1)).join('')}
                </ul>`;
        }

        html += '</li>';
        return html;
    }


    function showEditForm(commentId, currentText) {
        const commentElement = $(`#comment-${commentId}`);
        const editForm = `
            <div id="edit-form-${commentId}" style="margin-top: 10px;">
                <textarea class="edit-comment-text form-control" rows="3">${currentText}</textarea>
                <button class="save-edit-button btn btn-sm btn-primary" data-comment-id="${commentId}">Сохранить</button>
                <button class="cancel-edit-button btn btn-sm btn-secondary" data-comment-id="${commentId}">Отменить</button>
            </div>
        `;
        commentElement.append(editForm);
        commentElement.find('.edit-comment-text').focus();
    }

    function hideEditForm(commentId) {
        $(`#edit-form-${commentId}`).remove();
    }

    $(document).on('click', '.edit-comment-button', function() {
        const commentId = $(this).data('comment-id');
        const commentElement = $(`#comment-${commentId}`);
        const currentText = commentElement.find('div:first-child').text().split(': ').slice(1).join(': ');

        if ($(`#edit-form-${commentId}`).length) {
            return;  // Если форма уже открыта, ничего не делаем
        }
        showEditForm(commentId, currentText);
    });

    $(document).on('click', '.save-edit-button', function() {
        const commentId = $(this).data('comment-id');
        const newText = $(this).closest('div').find('.edit-comment-text').val();
        console.log('Saving edit for comment:', commentId, 'with text:', newText);
        const data = JSON.stringify({ text: newText })
        $.ajax({
            url: `/api/comments/${commentId}/`,
            method: 'PATCH',
            contentType: 'application/json',
            data: data,
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            success: function() {
                loadInitialComments(); // Обновляем список комментов
            },
            error: function(xhr) {
                console.error('Ошибка при редактировании комментария:', xhr.responseText);
                alert('Ошибка при редактировании комментария: ' + xhr.responseText);
            }
        });
        hideEditForm(commentId);
    });

    $(document).on('click', '.cancel-edit-button', function() {
        const commentId = $(this).data('comment-id');
        hideEditForm(commentId);
    });


    $(document).on('click', '.delete-comment-button', function() {
        const commentId = $(this).data('comment-id');
        if (!confirm('Вы уверены, что хотите удалить этот комментарий?')) {
            return;
        }
        $.ajax({
            url: `/api/comments/${commentId}/`,
            method: 'DELETE',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            success: function() {
                loadInitialComments(); // Обновляем список комментов
            },
            error: function(xhr) {
                console.error('Ошибка при удалении комментария:', xhr.responseText);
                alert('Ошибка при удалении комментария: ' + xhr.responseText);
            }
        });
    });

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
                $(this).remove();  // Remove the form
            },
            error: function(xhr) {
                console.error('Ошибка при создании ответа:', xhr.responseText);
                alert('Ошибка при создании ответа: ' + xhr.responseText);
            }
        });
    });

    $(document).on('click', '.reply-button', function() {
        const commentId = $(this).data('comment-id');
        const replyFormId = `reply-form-${commentId}`;
        if ($(`#${replyFormId}`).length) {
            return; // If form is already open, don't add another one
        }
        const replyForm = `
            <form id="${replyFormId}" class="reply-form" data-parent-id="${commentId}" style="margin-top: 5px;">
                <textarea class="reply-text form-control" placeholder="Ваш ответ..."></textarea>
                <div style="margin-top: 5px;">
                    <button type="submit" class="btn btn-sm btn-primary">Отправить ответ</button>
                    <button type="button" class="cancel-reply btn btn-sm btn-secondary">Отменить</button>
                </div>
            </form>
        `;
        $(this).closest('div').after(replyForm); // Insert form after the comment's content div
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

    // Event Handlers
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

        if (!accessToken) {
            console.error('Токен доступа отсутствует');
            window.location.href = "{% url 'galery:login_template' %}";
            return;
        }

        $.ajax({
            url: `/api/votes/`,
            method: 'POST',
            data,
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
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

    $('#edit-photo-button').click(function() {
        // Показываем форму редактирования
        $('#edit-photo-form').toggle();
    });

    // Обработчик для формы редактирования фотографии
    $('#edit-photo-form').submit(function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        $.ajax({
            url: `/api/photos/${photoId}/`,
            method: 'PATCH',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            success: function(response) {
                alert('Фотография успешно обновлена и отправлена на модерацию.');
                loadPhotoDetails(); // Обновляем информацию о фото
                $('#edit-photo-form').hide(); // Скрываем форму после успешного обновления
            },
            error: function(xhr) {
                console.error('Ошибка при обновлении фотографии:', xhr.responseText);
                alert('Ошибка при обновлении фотографии: ' + xhr.responseText);
            }
        });
    });


    // Initialization
    loadPhotoDetails();
    updateAuthUI();
    if (accessToken) {
        scheduleTokenRefresh(120);
    }
});
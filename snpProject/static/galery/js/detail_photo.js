$(document).ready(function() {
    const photoId = window.location.pathname.split('/').filter(Boolean).pop();
    const loginUrl = $('#login-data').data('login-url');

    const commentForm = $('#comment-form');
    const likeButton = $('#like-button');
    const unlikeButton = $('#unlike-button');
    const loginPromptComment = $('#login-prompt-comment');
    const loginPromptLike = $('#login-prompt-like');
    const deletePhotoButton = $('#delete-photo-button');
    const restorePhotoButton = $('#restore-photo-button');
    const photoActions = $('#photo-actions');
    const showAllCommentsButton = $('#show-all-comments-button');
    const hideAllCommentsButton = $('#hide-all-comments-button');

    let allCommentsLoaded = false;
    let tokenRefreshTimeout;
    let isRefreshing = false;
    let failedQueue = [];

    // Проверка аутентификации через API
    function checkAuth() {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/api/auth/verify/',
                method: 'GET',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                success: function(response) {
                    resolve(response.is_authenticated);
                },
                error: function(xhr) {
                    if (xhr.status === 401) {
                        resolve(false);
                    } else {
                        reject(xhr);
                    }
                }
            });
        });
    }

    // Заголовки для запросов
    function getAuthHeaders() {
        return {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/json'
        };
    }

    // Обновление UI в зависимости от статуса аутентификации
    function updateAuthUI(isAuthenticated) {
        if (isAuthenticated) {
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

    // Обработка ошибки аутентификации
    function handleAuthError() {
        updateAuthUI(false);
        window.location.href = loginUrl;
    }

    // Обновление токена
    function refreshTokenRequest() {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/api/refresh/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                success: function() {
                    resolve();
                },
                error: function(xhr) {
                    reject(xhr);
                }
            });
        });
    }

    // Обработка очереди запросов
    function processQueue(error, token = null) {
        failedQueue.forEach(promiseData => {
            if (error) {
                promiseData.reject(error);
            } else {
                promiseData.resolve(token);
            }
        });
        failedQueue = [];
    }

    // Обработчик AJAX ошибок
    $(document).ajaxError(function(event, jqXHR, ajaxSettings, thrownError) {
        if (jqXHR.status === 401 && !ajaxSettings._retry) {
            const originalOptions = ajaxSettings;

            if (isRefreshing) {
                return new Promise(function(resolve, reject) {
                    failedQueue.push({ resolve, reject });
                }).then(function() {
                    return $.ajax(originalOptions);
                });
            }

            isRefreshing = true;
            originalOptions._retry = true;

            refreshTokenRequest()
                .then(function() {
                    processQueue(null);
                    return $.ajax(originalOptions);
                })
                .catch(function(error) {
                    processQueue(error, null);
                    handleAuthError();
                })
                .finally(function() {
                    isRefreshing = false;
                });
        }
    });

    // Загрузка данных фотографии
    function loadPhotoDetails() {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: `/api/photos/${photoId}/?include_deleted=true`,
                method: 'GET',
                headers: getAuthHeaders(),
                success: function(photo) {
                    $('#photo-title').text(photo.title);
                    $('#photo-image').attr('src', photo.image || '');
                    $('#photo-author').text(photo.author.username);
                    $('#photo-author-avatar').attr('src', photo.author.avatar || '');
                    $('#photo-description').text(photo.description);
                    $('#votes-count').text(photo.votes.length || 0);

                    $('#edit-title').val(photo.title);
                    $('#edit-description').val(photo.description);

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
                        $('#edit-photo-button').show();
                    } else {
                        photoActions.hide();
                        $('#edit-photo-button').hide();
                    }

                    if (photo.has_liked === true) {
                        $('#like-button').hide();
                        const userVoteId = photo.votes.find(vote => vote);
                        $('#unlike-button').show().data('voteId', userVoteId);
                    } else {
                        $('#like-button').show();
                        $('#unlike-button').hide().data('voteId', null);
                    }

                    resolve(photo);
                },
                error: function(xhr) {
                    reject(xhr);
                }
            });
        });
    }

    // Удаление фотографии
    $('#delete-photo-button').click(function() {
        if (!confirm("Вы уверены, что хотите удалить эту фотографию?")) return;

        $.ajax({
            url: `/api/photos/${photoId}/`,
            method: 'DELETE',
            headers: getAuthHeaders(),
            success: function() {
                $('#delete-photo-button').hide();
                $('#restore-photo-button').show();
            },
            error: function(xhr) {
                alert(xhr.responseJSON?.detail || 'Ошибка при удалении фотографии');
            }
        });
    });

    // Восстановление фотографии
    $('#restore-photo-button').click(function() {
        $.ajax({
            url: `/api/photos/${photoId}/restore_photo/`,
            method: 'POST',
            headers: getAuthHeaders(),
            success: function() {
                loadPhotoDetails();
            },
            error: function(xhr) {
                alert(xhr.responseJSON?.detail || 'Ошибка при восстановлении фотографии');
            }
        });
    });

    // Система комментариев
    function loadInitialComments() {
        return new Promise((resolve, reject) => {
            $.get(`/api/comments/?photo=${photoId}`)
                .done(comments => {
                    const commentsList = $('#comments-list');
                    commentsList.empty();

                    const rootComments = comments.filter(comment => !comment.parent);
                    rootComments.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

                    const initialRootComments = rootComments.slice(0, 2);

                    initialRootComments.forEach(comment => {
                        commentsList.append(buildCommentHTML(comment, comments));
                    });

                    showAllCommentsButton.toggle(rootComments.length > 2);
                    resolve();
                })
                .fail(reject);
        });
    }

    function loadAllComments() {
        $.get(`/api/comments/?photo=${photoId}`)
            .done(comments => {
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
            .fail(xhr => console.error('Ошибка при загрузке всех комментариев:', xhr));
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
            </div>`;

        if (comment.can_delete) {
            html += `
            <div style="margin-top: 5px;">
                <button class="edit-comment-button btn btn-sm btn-outline-primary" data-comment-id="${comment.id}">Редактировать</button>
                <button class="delete-comment-button btn btn-sm btn-outline-danger" data-comment-id="${comment.id}">Удалить</button>
            </div>`;
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

    // Обработчики событий
    $(document).on('click', '.edit-comment-button', function() {
        const commentId = $(this).data('comment-id');
        const commentElement = $(`#comment-${commentId}`);
        const currentText = commentElement.find('div:first-child').text().split(': ').slice(1).join(': ');

        if ($(`#edit-form-${commentId}`).length) return;

        const editForm = `
        <div id="edit-form-${commentId}" style="margin-top: 10px;">
            <textarea class="edit-comment-text form-control" rows="3">${currentText}</textarea>
            <button class="save-edit-button btn btn-sm btn-primary" data-comment-id="${commentId}">Сохранить</button>
            <button class="cancel-edit-button btn btn-sm btn-secondary" data-comment-id="${commentId}">Отменить</button>
        </div>`;
        commentElement.append(editForm);
    });

    $(document).on('click', '.save-edit-button', function() {
        const commentId = $(this).data('comment-id');
        const newText = $(this).closest('div').find('.edit-comment-text').val();

        $.ajax({
            url: `/api/comments/${commentId}/`,
            method: 'PATCH',
            contentType: 'application/json',
            data: JSON.stringify({ text: newText }),
            headers: getAuthHeaders(),
            success: function() {
                loadInitialComments();
            },
            error: function(xhr) {
                alert('Ошибка при редактировании комментария: ' + xhr.responseText);
            }
        });
    });

    $(document).on('click', '.cancel-edit-button', function() {
        const commentId = $(this).data('comment-id');
        $(`#edit-form-${commentId}`).remove();
    });

    $(document).on('click', '.delete-comment-button', function() {
        const commentId = $(this).data('comment-id');
        if (!confirm('Вы уверены, что хотите удалить этот комментарий?')) return;

        $.ajax({
            url: `/api/comments/${commentId}/`,
            method: 'DELETE',
            headers: getAuthHeaders(),
            success: function() {
                loadInitialComments();
            },
            error: function(xhr) {
                alert('Ошибка при удалении комментария: ' + xhr.responseText);
            }
        });
    });

    $(document).on('click', '.reply-button', function() {
        const commentId = $(this).data('comment-id');
        const replyFormId = `reply-form-${commentId}`;
        if ($(`#${replyFormId}`).length) return;

        const replyForm = `
        <form id="${replyFormId}" class="reply-form" data-parent-id="${commentId}" style="margin-top: 5px;">
            <textarea class="reply-text form-control" placeholder="Ваш ответ..."></textarea>
            <div style="margin-top: 5px;">
                <button type="submit" class="btn btn-sm btn-primary">Отправить ответ</button>
                <button type="button" class="cancel-reply btn btn-sm btn-secondary">Отменить</button>
            </div>
        </form>`;
        $(this).closest('div').after(replyForm);
    });

    $(document).on('click', '.cancel-reply', function() {
        $(this).closest('.reply-form').remove();
    });

    $(document).on('submit', '[id^="reply-form-"]', function(e) {
        e.preventDefault();
        const parentId = $(this).data('parent-id');
        const text = $(this).find('.reply-text').val();

        $.ajax({
            url: `/api/comments/`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                text: text,
                photo: photoId,
                parent: parentId
            }),
            headers: getAuthHeaders(),
            success: function() {
                loadInitialComments();
            },
            error: function(xhr) {
                alert('Ошибка при создании ответа: ' + xhr.responseText);
            }
        });
    });

    // Лайки
    $('#like-button').click(function() {
        $.ajax({
            url: `/api/votes/`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ photo: photoId }),
            headers: getAuthHeaders(),
            success: function(response) {
                loadPhotoDetails();
            },
            error: function(xhr) {
                if (xhr.status === 400 && xhr.responseJSON?.detail === 'Вы уже поставили лайк этой фотографии.') {
                    loadPhotoDetails();
                } else {
                    alert('Ошибка при постановке лайка: ' + xhr.responseText);
                }
            }
        });
    });

    $('#unlike-button').click(function() {
        const voteId = $(this).data('voteId');
        $.ajax({
            url: `/api/votes/${voteId}/`,
            type: 'DELETE',
            headers: getAuthHeaders(),
            success: function() {
                loadPhotoDetails();
            },
            error: function(xhr) {
                alert('Ошибка при удалении лайка: ' + xhr.responseText);
            }
        });
    });

    // Редактирование фотографии
    $('#edit-photo-button').click(function() {
        $('#edit-photo-form').toggle();
    });

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
            success: function() {
                alert('Фотография успешно обновлена и отправлена на модерацию.');
                loadPhotoDetails();
                $('#edit-photo-form').hide();
            },
            error: function(xhr) {
                alert('Ошибка при обновлении фотографии: ' + xhr.responseText);
            }
        });
    });

    // Инициализация
    checkAuth()
        .then(function(isAuthenticated) {
            updateAuthUI(isAuthenticated);
            return loadPhotoDetails();
        })
        .then(function() {
            return loadInitialComments();
        })
        .catch(function(error) {
            console.error("Ошибка при инициализации:", error);
        });
});
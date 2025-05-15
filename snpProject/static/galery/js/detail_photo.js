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
    let currentUserId = null;
    let allCommentsLoaded = false;
    let tokenRefreshTimeout;
    let isRefreshing = false;
    let failedQueue = [];

    async function initialize() {
        try {
            // 1. Проверяем аутентификацию
            const authData = await checkAuth();
            currentUserId = authData.user_id;
            console.log("Authenticated with user ID:", currentUserId);
            console.log("Current user ID after checkAuth:", currentUserId); // New debug line
            
            // 2. Обновляем UI в зависимости от аутентификации
            updateAuthUI(authData.is_authenticated);
            
            // 3. Загружаем данные о фото
            console.log("Current user ID before loadPhotoDetails:", currentUserId); // New debug line
            const photo = await loadPhotoDetails();
            console.log("Photo loaded with has_liked:", photo.has_liked);
            
            // 4. Загружаем комментарии
            await loadInitialComments();

            // Initialize Like Buttons
            initializeLikeButtons();

            console.log("Initialization complete");
        } catch (error) {
            console.error("Initialization failed:", error);
            handleAuthError();
        }
    }

    // Запускаем инициализацию
    initialize();

   function updateLikeButtons(hasLiked) {
    console.log("updateLikeButtons called with:", hasLiked);
    console.log("Updating like buttons - hasLiked:", hasLiked, "currentUserId:", currentUserId);
    
    if (!currentUserId) {
        $('#like-button').hide();
        $('#unlike-button').hide();
        return;
    }

    $('#like-button').toggle(!hasLiked);
    $('#unlike-button').toggle(hasLiked);
} 

    function checkAuth() {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: '/api/auth/verify/',
            method: 'GET',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            success: function(response) {
                console.log("Auth verification success:", response);
                currentUserId = response.user_id;
                resolve({
                    is_authenticated: response.is_authenticated,
                    user_id: response.user_id
                });
            },
            error: function(xhr) {
                console.error("Auth verification error:", xhr);
                if (xhr.status === 401) {
                    resolve({ is_authenticated: false, user_id: null });
                } else {
                    reject(xhr);
                }
            }
        });
    });
}

    function getAuthHeaders() {
        return {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/json'
        };
    }

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

    function handleAuthError() {
        updateAuthUI(false);
        window.location.href = loginUrl;
    }

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
                        const isDeleted = String(photo.moderation) === '1' && photo.deleted_at;

                        if (isDeleted) {
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

                    console.log("loadPhotoDetails - photo.has_liked:", photo.has_liked, "currentUserId:", currentUserId);
                    updateLikeButtons(photo.has_liked);
                    resolve(photo);
                },
                error: function(xhr) {
                    console.error("loadPhotoDetails - error:", xhr);
                    reject(xhr);
                }
            });
        });
    }

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


    commentForm.on('submit', function(e) {
        e.preventDefault();

        const formData = {
            text: commentForm.find('textarea[name="text"]').val(),
            photo: photoId
        };

        $.ajax({
            url: '/api/comments/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            headers: getAuthHeaders(),
            success: function() {
                commentForm.find('textarea').val('');
                loadInitialComments();
            },
            error: function(xhr) {
                alert('Ошибка при добавлении комментария: ' + (xhr.responseJSON?.detail || xhr.statusText));
            }
        });
    });


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

    $('#show-all-comments-button').on('click', function() {
        loadAllComments();
    });

    $('#hide-all-comments-button').on('click', function() {
        loadInitialComments();
        hideAllCommentsButton.hide();
        showAllCommentsButton.show();
    });

    $(document).on('click', '.toggle-replies-button', function() {
        const commentId = $(this).data('comment-id');
        const repliesContainer = $(`#replies-${commentId}`);
        const isVisible = repliesContainer.is(':visible');

        repliesContainer.toggle();

        $(this).text(isVisible ? 'Показать ответы' : 'Скрыть ответы');

        localStorage.setItem(`repliesVisible-${commentId}`, !isVisible);
    });
    
    $('#like-button').click(async function() {
        if (!currentUserId) {
            showToast("Для оценки необходимо авторизоваться", "error");
            return;
        }

        try {
            const response = await $.ajax({
                url: '/api/votes/',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ photo: photoId }),
                headers: getAuthHeaders()
            });
            
            // After successful like, immediately update the state
            updateLikeButtons(true);
            await loadPhotoDetails(); // To update the counter and has_liked state

        } catch (xhr) {
            if (xhr.status === 400 && xhr.responseJSON.vote_id) {
                updateLikeButtons(true);
                showToast('Вы уже лайкали эту фотографию', 'info');
            } else {
                const errorMsg = xhr.responseJSON?.detail || 'Ошибка при постановке лайка';
                showToast(errorMsg, 'error');
            }
        }
    });

    $('#unlike-button').click(async function() {
        if (!currentUserId) {
            showToast("Для оценки необходимо авторизоваться", "error");
            return;
        }

        try {
            await $.ajax({
                url: `/api/votes/by-photo/${photoId}/`,
                method: 'DELETE',
                headers: getAuthHeaders()
            });
            
            // After successful unlike, immediately update the state
            updateLikeButtons(false);
            await loadPhotoDetails(); // To update the counter and has_liked state
        } catch (xhr) {
            const errorMsg = xhr.responseJSON?.detail || 'Ошибка при удалении лайка';
            showToast(errorMsg, 'error');
        }
    });

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

    // Function to initialize like buttons
    function initializeLikeButtons() {
        console.log("Initializing like buttons...");
        if (currentUserId !== null) {
            console.log("Current user ID:", currentUserId);
            $.ajax({
                url: `/api/photos/${photoId}/`,
                method: 'GET',
                headers: getAuthHeaders(),
                success: function(photo) {
                    console.log("Photo details loaded for like button init:", photo.has_liked);
                    updateLikeButtons(photo.has_liked);
                },
                error: function(xhr) {
                    console.error("Error loading photo details for like button init:", xhr);
                    // Handle error, potentially hide the buttons or show an error message
                }
            });
        } else {
            console.log("User not authenticated, hiding like buttons.");
            updateLikeButtons(false); // Ensure buttons are hidden if not logged in
        }
    }

    checkAuth()
    .then(function(authData) {
        console.log("Auth completed, user ID:", authData.user_id);
        currentUserId = authData.user_id;
        return new Promise(resolve => setTimeout(resolve, 100)); // 100ms delay
    })
    .then(function() {
        return loadPhotoDetails();
    })
    .then(function(photo) {
        console.log("Photo details loaded, has_liked:", photo.has_liked);
        initializeLikeButtons(); // Initialize like buttons after loading photo details
        return loadInitialComments();
    })
    .catch(function(error) {
        console.error("Initialization error:", error);
        handleAuthError();
    });
});
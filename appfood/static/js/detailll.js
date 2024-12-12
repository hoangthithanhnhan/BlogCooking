$(document).on('submit', '.like-form', function(e) {
    e.preventDefault();
    var $form = $(this);
    var $button = $form.find('button');
    var $likeCount = $('#like-count');
    
    $.ajax({
        type: 'POST',
        url: $form.attr('action'),
        data: $form.serialize(),
        success: function(response) {
            if (response.liked) {
                $button.removeClass('btn-primary').addClass('btn-danger').text('Đã Thích');
            } else {
                $button.removeClass('btn-danger').addClass('btn-primary').text('Yêu Thích');
            }
            $likeCount.text(response.total_likes + ' người thích bài viết này');
        },
        error: function() {
            alert('Có lỗi xảy ra. Vui lòng thử lại.');
        }
    });
});
$(document).on('submit', '.comment-form', function(e) {
    e.preventDefault();
    var $form = $(this);
    var $content = $form.find('textarea[name="content"]');
    var recipeId = $form.data('recipe-id');

    $.ajax({
        type: 'POST',
        url: '/add-comment/' + recipeId + '/',
        data: $form.serialize(),
        success: function(response) {
            // Thêm comment mới vào danh sách comment
            $('#comments-list').append(
                '<div class="comment">' +
                '<p><strong>' + response.comment.user + '</strong> (' + response.comment.created_at + '):</p>' +
                '<p>' + response.comment.content + '</p>' +
                '</div>'
            );
            $content.val('');  // Xóa nội dung trong textarea
        },
        error: function(error) {
            alert('Có lỗi xảy ra. Vui lòng thử lại.');
        }
    });
});

function request() {
    var searchId = parseInt($("#searchIdText").val());
    if (isNaN(searchId)) {
        alert(searchId + "不是数字");
        return
    }
    $.ajax({
        type: "GET",
        url: window.location.protocol + '//' + window.location.host + '/get_book_tag?bookId=' + searchId,
        dataType: "json",
        contentType: 'application/json;charset=UTF-8',
        success: function (r) {
            var humanTagElement = ''
            if (r.status == 'failed') {
                alert(r.msg);
                $('#bookId').html('');
                $('#title').html('');
                $('#actor').html('');
                $("#bookTag").html('');
                $('#movieTag').html('');
                return
            }
            $('#bookId').html(r.book_id);
            $('#title').html(r.title);
            $('#actor').html(r.actor);
            bookTagElement = ''
            bookTagList = r.book_tag
            for (var i = 0; i < bookTagList.length; i++) {
                bookTagElement += '<tr class="active">' +
                    '<td>' + bookTagList[i] + '</td>' +
                    '<td> <a class="del" value="' + bookTagList[i] + '">删除</a> </td>' +
                    '</tr>'
            }
            $("#bookTag").empty();
            $("#bookTag").append(bookTagElement);

            movieTagElement = ''
            movieTagList = r.movie_tag
            for (var i = 0; i < movieTagList.length; i++) {
                movieTagElement += '<tr class="active">' +
                    '<td>' + movieTagList[i] + '</td>' +
                    '<td> <a class="del" value="' + movieTagList[i] + '">删除</a> </td>' +
                    '</tr>'
            }
            $("#bookMovieTag").empty();
            $("#bookMovieTag").append(movieTagElement);
        },
        error: function (xhr) {
            alert('网络异常')
        }
    })
}

function addBookTag() {
    var searchId = parseInt($("#bookId").html());
    var bookTag = $("#addTagText").val();
    $.ajax({
        type: "GET",
        url: window.location.protocol + '//' + window.location.host + '/add_book_tag?bookId=' + searchId + '&bookTag=' + bookTag,
        dataType: "json",
        contentType: 'application/json;charset=UTF-8',
        success: function (r) {
            if (r.status == 'failed') {
                alert(r.msg);
                return
            }
            alert(r.msg);
            request();
        },
        error: function (xhr) {
            alert('网络异常')
        }
    })
}

function delBookTag() {
    var searchId = parseInt($("#bookId").html());
    var bookTag = $(this).parent().prev().html();
    $.ajax({
        type: "GET",
        url: window.location.protocol + '//' + window.location.host + '/del_book_tag?bookId=' + searchId + '&bookTag=' + bookTag,
        dataType: "json",
        contentType: 'application/json;charset=UTF-8',
        success: function (r) {
            if (r.status == 'failed') {
                alert(r.msg);
                return
            }
            alert(r.msg);
            request();
        },
        error: function (xhr) {
            alert('网络异常')
        }
    })
}

function addMovieTag() {
    var searchId = parseInt($("#bookId").html());
    var movieTag = $("#addMovieTagText").val();
    $.ajax({
        type: "GET",
        url: window.location.protocol + '//' + window.location.host + '/add_movie_tag?bookId=' + searchId + '&movieTag=' + movieTag,
        dataType: "json",
        contentType: 'application/json;charset=UTF-8',
        success: function (r) {
            if (r.status == 'failed') {
                alert(r.msg);
                return
            }
            alert(r.msg);
            request();
        },
        error: function (xhr) {
            alert('网络异常')
        }
    })
}

function delMovieTag() {
    var searchId = parseInt($("#bookId").html());
    var movieTag = $(this).parent().prev().html();
    $.ajax({
        type: "GET",
        url: window.location.protocol + '//' + window.location.host + '/del_movie_tag?bookId=' + searchId + '&movieTag=' + movieTag,
        dataType: "json",
        contentType: 'application/json;charset=UTF-8',
        success: function (r) {
            if (r.status == 'failed') {
                alert(r.msg);
                return
            }
            alert(r.msg);
            request();
        },
        error: function (xhr) {
            alert('网络异常')
        }
    })
}


$(document).ready(function () {
    $("#searchId").click(request);
    $('#bookTag').on('click', '.del', delBookTag());
    $("#addTag").click(addBookTag());
    $("#addMovieTag").click(addMovieTag());
    $('#bookMovieTag').on('click', '.del', delMovieTag());
    var searchId = $("#searchIdText").val();
    if (searchId != '') {
        request();
    }
});

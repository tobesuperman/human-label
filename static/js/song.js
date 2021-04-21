function request() {
    var search_id = parseInt($("#search_id_text").val());
    if (isNaN(search_id)) {
        alert(search_id + "不是数字");
        return
    }
    $.ajax({
        type: "GET",
        url: window.location.protocol + '//' + window.location.host + '/get_song_label?SongId=' + search_id,
        dataType: "json",
        contentType: 'application/json;charset=UTF-8',
        success: function (r) {
            var human_label_element = ''
            if (r.status == 'failed') {
                alert(r.msg);
                $('#songid').html('');
                $('#songname').html('');
                $('#actor').html('');
                $("#song_label").html('');
                $('#movie_label').html('');
                return
            }
            $('#songid').html(r.song_id);
            $('#songname').html(r.title);
            $('#actor').html(r.actor);
            song_label_element = ''
            song_label_list = r.song_label
            for (var i = 0; i < song_label_list.length; i++) {
                song_label_element += '<tr class="active">' +
                    '<td>' + song_label_list[i] + '</td>' +
                    '<td> <a class="del" value="' + song_label_list[i] + '">删除</a> </td>' +
                    '</tr>'
            }
            $("#song_label").empty();
            $("#song_label").append(song_label_element);

            movie_label_element = ''
            movie_tag_list = r.movie_tag
            for (var i = 0; i < movie_tag_list.length; i++) {
                movie_label_element += '<tr class="active">' +
                    '<td>' + movie_tag_list[i] + '</td>' +
                    '<td> <a class="del" value="' + movie_tag_list[i] + '">删除</a> </td>' +
                    '</tr>'
            }
            $("#song_movie_label").empty();
            $("#song_movie_label").append(movie_label_element);
        },
        error: function (xhr) {
            alert('网络异常')
        }
    })
}

function add_song_label() {
    var search_id = parseInt($("#songid").html());
    var song_tag = $("#add_label_text").val();
    $.ajax({
        type: "GET",
        url: window.location.protocol + '//' + window.location.host + '/add_song_label?SongId=' + search_id + '&SongTag=' + song_tag,
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

function del_song_label() {
    var search_id = parseInt($("#songid").html());
    var song_tag = $(this).parent().prev().html();
    $.ajax({
        type: "GET",
        url: window.location.protocol + '//' + window.location.host + '/del_song_label?SongId=' + search_id + '&SongTag=' + song_tag,
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

function add_movie_label() {
    var search_id = parseInt($("#songid").html());
    var movie_tag = $("#add_movie_label_text").val();
    $.ajax({
        type: "GET",
        url: window.location.protocol + '//' + window.location.host + '/add_movie_label?SongId=' + search_id + '&MovieTag=' + movie_tag,
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

function del_movie_label() {
    var search_id = parseInt($("#songid").html());
    var movie_tag = $(this).parent().prev().html();
    $.ajax({
        type: "GET",
        url: window.location.protocol + '//' + window.location.host + '/del_movie_label?SongId=' + search_id + '&MovieTag=' + movie_tag,
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
    $("#search_id").click(request);
    $('#song_label').on('click', '.del', del_song_label);
    $("#add_label").click(add_song_label);
    $("#add_movie_label").click(add_movie_label);
    $('#song_movie_label').on('click', '.del', del_movie_label);
    var search_id = $("#search_id_text").val();
    if (search_id != '') {
        request();
    }
});

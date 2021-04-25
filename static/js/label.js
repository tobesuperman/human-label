var pageSize = 8;
var page = 1;
var keyword = '';
var lastSearch = null;
var data = null;
var totNum = 0;

function request() {
    $("#result").empty();
    keyword = $("#searchTagText").val();
    page = parseInt($("#pageIndex").val());
    if (lastSearch == keyword) {
    } else {
        page = 1;
        $("#pageIndex").val(1)
        $("#pageIndex").text(1)
    }
    lastSearch = keyword;
    $.ajax({
        type: "GET",
        url: './get_tag?pageIndex=' + page + '&pageSize=8&keyword=' + keyword,
        dataType: "json",
        contentType: 'application/json;charset=UTF-8',
        success: function (r) {
            if (r.status == 'failed') {
                alert(r.msg)
            }
            totNum = r.total;
            data = r.tags;
            var _html = ''
            for (var i = 0; i < data.length; i++) {
                if (data[i].type == '主题（系统自带）' || data[i].type == '体裁（系统自带）') {
                    _html += '<tr class="active">' +
                        '<td>' + data[i].name + '</td>' +
                        '<td>' + data[i].type + '</td>' +
                        '<td> 不可修改 </td>' +
                        '</tr>'
                    continue
                }
                // if (data[i].type == '人工添加') {
                //
                // }
                _html += '<tr class="active">' +
                    '<td>' + data[i].name + '</td>' +
                    '<td>' + data[i].type + '</td>' +
                    '<td> <a class="del">删除</a> </td>' +
                    '</tr>'
            }
            $("#result").append(_html);
        },
        error: function (xhr) {
            alert('网络异常')
        }
    })
}

function del() {
    var tagName = $(this).parent().prev().prev().html();
    $.ajax({
        type: "GET",
        url: './del_tag?delTag=' + tagName,
        dataType: "json",
        contentType: 'application/json;charset=UTF-8',
        success: function (r) {
            alert(r.msg);
            request();
        },
        error: function (xhr) {
            alert('网络异常')
        }
    })
}

$('#result').on('click', '.del', del);

$("#searchTag").click(function () {
        request();
    }
);

function add() {
    var addTag = $("#addTagText").val();
    $.ajax({
        type: "GET",
        url: './add_tag?addTag=' + addTag,
        dataType: "json",
        contentType: 'application/json;charset=UTF-8',
        success: function (r) {
            alert(r.msg);
            request();
        },
        error: function (xhr) {
            alert('网络异常')
        }
    })
}

$("#addTag").click(function () {
        add();
    }
);

$("#prePage").click(function () {
    page = parseInt($("#pageIndex").val());
    if (page <= 1) {
        alert("没有上一页了!");
    } else {
        $("#pageIndex").val(page - 1);
        $("#pageIndex").text(page - 1)
        request();
    }

});

$("#nextPage").click(function () {
    page = parseInt($("#pageIndex").val());
    if (pageSize * page > totNum) {
        alert("没有下一页了");
    } else {
        $("#pageIndex").val(page + 1);
        $("#pageIndex").text(page + 1)
        request();
    }
});

request();

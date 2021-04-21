var pageSize = 8;
var page = 1;
var keyword = '';
var last_search = null;
var data = null;
var totNum = 0;

function request() {
    $("#result").empty();
    keyword = $("#search_tag_text").val();
    page = parseInt($("#pageNum").val());
    if (last_search == keyword) {
    } else {
        page = 1;
        $("#pageNum").val(1)
        $("#pageNum").text(1)
    }
    last_search = keyword;
    $.ajax({
        type: "GET",
        url: './get_label?PageIndex=' + page + '&PageSize=8&SearchWord=' + keyword,
        dataType: "json",
        contentType: 'application/json;charset=UTF-8',
        success: function (r) {
            if (r.status == 'failed') {
                alert(r.msg)
            }
            totNum = r.total;
            data = r.labels;
            var _html = ''
            for (var i = 0; i < data.length; i++) {
                if (data[i].type == '系统自带') {
                    _html += '<tr class="active">' +
                        '<td>' + data[i].name + '</td>' +
                        '<td>' + data[i].type + '</td>' +
                        '<td> 不可修改 </td>' +
                        '</tr>'
                }
                if (data[i].type == '人工添加') {
                    _html += '<tr class="active">' +
                        '<td>' + data[i].name + '</td>' +
                        '<td>' + data[i].type + '</td>' +
                        '<td> <a class="del">删除</a> </td>' +
                        '</tr>'
                }
            }
            $("#result").append(_html);
        },
        error: function (xhr) {
            alert('网络异常')
        }
    })
}

function del() {
    var tagname = $(this).parent().prev().prev().html();
    $.ajax({
        type: "GET",
        url: './del_label?DelTag=' + tagname,
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

$("#search_tag").click(function () {
        request();
    }
);

function add() {
    var addword = $("#add_tag_text").val();
    $.ajax({
        type: "GET",
        url: './add_label?AddTag=' + addword,
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

$("#add_tag").click(function () {
        add();
    }
);

$("#prepage").click(function () {
    page = parseInt($("#pageNum").val());
    if (page <= 1) {
        alert("没有上一页了!");
    } else {
        $("#pageNum").val(page - 1);
        $("#pageNum").text(page - 1)
        request();
    }

});

$("#nextpage").click(function () {
    page = parseInt($("#pageNum").val());
    if (pageSize * page > totNum) {
        alert("没有下一页了");
    } else {
        $("#pageNum").val(page + 1);
        $("#pageNum").text(page + 1)
        request();
    }
});

request();

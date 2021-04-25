var pageSize = 8;
var page = 1;
var keyword = '';
var lastSearch = null;
var data = null;
var totNum = 0;

function request() {
    $("#result").empty();
    // $("#res").addClass("hidden");
    keyword = $("#key").val();
    page = parseInt($("#pageIndex").val());
    if (lastSearch == keyword) {
    } else {
        page = 0;
        $("#pageNum").val(0)
    }
    lastSearch = keyword;
    $.ajax({
        type: "GET",
        url: './search_song?keyword='
            + keyword + '&pageIndex=' + page + '&pageSize=8',
        dataType: "json",
        contentType: 'application/json;charset=UTF-8',
        success: function (r) {
            console.log(r.Result);
            // console.log(r.Result.totalNum);
            data = r.Result.list;
            totNum = r.Result.totalNum;

            var _html = '';
            for (var i = 0; i < data.length; i++) {

                var bookId = data[i].id
                var tagUrl = window.location.protocol + '//' + window.location.host + '/book_tag?bookId=' + bookId
                //var musicStoreFilepath = data[i].music_storefilepath;
                //var ringStoreFilepath = data[i].ring_storefilepath;
                //var buzzStoreFilepath = data[i].buzz_storefilepath;

                // console.log(ringStoreFilepath)

                /*var playUrl = "";
                if(musicStoreFilepath!=""){
                    playUrl =  musicStoreFilepath.split("|")[0];
                }else if(ringStoreFilepath != ""){
                    playUrl = ringStoreFilepath.split("|")[0];
                }else{
                    playUrl = buzzStoreFilepath.split("|")[0];
                }

                console.log(playUrl);

                playUrl = "http://res.ctmus.cn/" +  playUrl.substr(playUrl.indexOf("audio"), playUrl.length);*/

                // console.log(playUrl);

                _html += '<tr class="active">' +
                    '<td>' + data[i].title + '</td>' +
                    '<td>' + data[i].singer + '</td>' + "<td><a target=\"view_window\" href=\"" + tagUrl + '">' + '标签信息' + '</a></td>' +
                    '</tr>'
            }
            $("#result").append(_html);
            var obj = document.getElementById("spanTotalNum");
            obj.innerText = "共" + r.Result.totalNum + "首";

            var defObj = document.getElementById("defSlot");
            defObj.innerText = "确定槽: " + JSON.stringify(r.Result.confirm_slot);

            var undefObj = document.getElementById("undefSlot");
            undefObj.innerText = "非确定槽: " + JSON.stringify(r.Result.unconfirm_solt);
        },
        error: function (xhr) {
            alert("网络异常")
        }
    })
}

$("#btn").click(function () {
        request();
    }
);


$("#key").bind('keydown', function (event) {
    if (event.keyCode == "13") {
        request();
    }
});


$("#prePage").click(function () {
    page = parseInt($("#pageIndex").val());
    if (page <= 0) {
        alert("没有上一页了!");
    } else {
        $("#pageIndex").val(page - 1);
        request();
    }

});

$("#nextPage").click(function () {
    page = parseInt($("#pageIndex").val());
    if (pageSize * (page + 1) >= totNum) {
        alert("没有下一页了");
    } else {
        $("#pageIndex").val(page + 1);
        request();
    }
});

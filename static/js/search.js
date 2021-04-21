var pageSize = 8;
var page = 1;
var keyword = '';
var last_search = null;
var data = null;
var totNum = 0;

function request() {
    $("#result").empty();
    // $("#res").addClass("hidden");
    keyword = $("#key").val();
    page = parseInt($("#pageNum").val());
    if (last_search == keyword) {
    } else {
        page = 0;
        $("#pageNum").val(0)
    }
    last_search = keyword;
    $.ajax({
        type: "GET",
        url: './search_song?keyword='
            + keyword + '&pagenum=' + page + '&pagesize=8',
        dataType: "json",
        contentType: 'application/json;charset=UTF-8',
        success: function (r) {
            console.log(r.Result);
            // console.log(r.Result.totalNum);
            data = r.Result.list;
            totNum = r.Result.totalNum;

            var _html = '';
            for (var i = 0; i < data.length; i++) {

                var song_id = data[i].id
                var label_url = window.location.protocol + '//' + window.location.host + '/song_label?songid=' + song_id
                //var music_storefilepath = data[i].music_storefilepath;
                //var ring_storefilepath = data[i].ring_storefilepath;
                //var buzz_storefilepath = data[i].buzz_storefilepath;

                // console.log(ring_storefilepath)

                /*var playUrl = "";
                if(music_storefilepath!=""){
                    playUrl =  music_storefilepath.split("|")[0];
                }else if(ring_storefilepath != ""){
                    playUrl = ring_storefilepath.split("|")[0];
                }else{
                    playUrl = buzz_storefilepath.split("|")[0];
                }

                console.log(playUrl);

                playUrl = "http://res.ctmus.cn/" +  playUrl.substr(playUrl.indexOf("audio"), playUrl.length);*/

                // console.log(playUrl);

                _html += '<tr class="active">' +
                    '<td>' + data[i].title + '</td>' +
                    '<td>' + data[i].singer + '</td>' +
                    '<td>' + '<a target="view_window" href="' + label_url + '">' + '标签信息' + '</a></td>' +
                    '</tr>'
            }
            $("#result").append(_html);
            var obj = document.getElementById("spanTotalNum");
            obj.innerText = "共" + r.Result.totalNum + "首";

            var obj_def = document.getElementById("def_slot");
            obj_def.innerText = "确定槽: " + JSON.stringify(r.Result.confirm_slot);

            var obj_undef = document.getElementById("undef_slot");
            obj_undef.innerText = "非确定槽: " + JSON.stringify(r.Result.unconfirm_solt);
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


$("#prepage").click(function () {
    page = parseInt($("#pageNum").val());
    if (page <= 0) {
        alert("没有上一页了!");
    } else {
        $("#pageNum").val(page - 1);
        request();
    }

});

$("#nextpage").click(function () {
    page = parseInt($("#pageNum").val());
    if (pageSize * (page + 1) >= totNum) {
        alert("没有下一页了");
    } else {
        $("#pageNum").val(page + 1);
        request();
    }
});
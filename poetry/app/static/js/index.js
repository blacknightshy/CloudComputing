/**
 * Created by fandy on 2019/5/8.
 */
var pageNO = 0;
var where = 1;
var datetime = 1;
var block_flag = true;
var cookie_flag = true;
$(
    function () {
        // var lis = $('#where > li');
        // for(var i=0;i<lis.length;i++){
        //     var clas = lis[i].attr('class');
        //     if(clas == 'active'){
        //         where = lis[i].attr('value');
        //     }
        // }
        // var liss = $('#datetime > li');
        // for(var j=0;j<liss.length;j++){
        //     var clas = lis[i].attr('class');
        //     if(clas == 'active'){
        //         datetime = lis[i].attr('value');
        //     }
        // }
        getwangzhi();
        getmovie(2);
    }
);
function setCookie(name,value)
{
    if(cookie_flag){
            if(!confirm('确认看过？请确认未开启无痕模式！否则无法保存cookie，关闭浏览器再次访问将无法实现该功能。下次进入该页面将不再为您展示改电影，如需再次展示请清除cookie！')){
                return false;
            }else {
               cookie_flag = false;
            }
    }
    var Days = 30;
    var exp = new Date();
    exp.setTime(exp.getTime() + Days*24*60*60*1000);
    document.cookie = name + "="+ escape (value) + ";expires=" + exp.toGMTString();
    return true;
}
function getCookie(name)
{
    var arr,reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)");

    if(arr=document.cookie.match(reg))

        return unescape(arr[2]);
    else
        return null;
}

$(window).scroll(
    function() {
        var scrollTop = $(this).scrollTop();
        var scrollHeight = $(document).height();
        var windowHeight = $(this).height();
        if (scrollTop + windowHeight + 50 >= scrollHeight) {
            let last_scrollTop = $(document).scrollTop();
            pageNO ++;
            getmovie(2);
            $(document).scrollTop(last_scrollTop);
        }
    });
function getwangzhi() {
    $.ajax({
        type: "get",
        url: "/movie/index",
        dataType:"json",
        success: function (data) {
            ul = "";
            for(var key in data){
                if(key.substr(-1)=='2'){
                    ul += "<li class=\"active\"><a>"+data[key]+"<span class='label label-badge label-success'></span></a></li>";
                }else {
                    ul += "<li><a>"+data[key]+"<span class='label label-badge label-success'></span></a></li>";
                }
            }
            $('#nav').html(ul);
        }
    });
}

function show(name,value) {
    if(name=='where'){
        lis = $('#where > li');
        for (var i=1;i<=lis.length;i++){
            if(i==value){
                $('#where > li:nth-child('+i.toString()+')').attr('class','active');
            }else {
                $('#where > li:nth-child('+i.toString()+')').attr('class','');
            }
        }
        where = value;
    }
    if(name=='datetime'){
        datetime = value;
        lis = $('#datetime > li');
        for (var i=1;i<=lis.length;i++){
            var fuck = value * 10;
            value = parseInt(fuck/10);
            var xiao = fuck % 10;
            if(i==value){
                if(xiao != 0){
                    liss = $('#year > li');
                    for (var j=1;j<=lis.length;j++) {
                        if(j==xiao) {
                            $('#year > li:nth-child('+j.toString()+')').attr('class','active');
                        }else {
                            $('#year > li:nth-child('+j.toString()+')').attr('class','');
                        }
                    }
                    }
                $('#datetime > li:nth-child('+i.toString()+')').attr('class','active');
            }else {
                $('#datetime > li:nth-child('+i.toString()+')').attr('class','');
            }
             value = datetime;
        }

    }
    pageNO = 0;
    block_flag = true;
    $('.items').html('');
    getmovie(2);
   $(document).scrollTop(0);
}

function getmovie(type) {
    var movie_name = '';
    if(type==1){
        block_flag = true;
        pageNO = 0;
        movie_name = $('#inputSearchExample3').val();
        $('.items').html('');
        $('#inputSearchExample3').val('');
    }
    if(block_flag){
        $.ajax({
        type: "post",
        url: "/movie/getmovie",
        data: {'pageNO':pageNO,'where':where,'datetime':datetime,'movie_name':movie_name},
        success: function (json) {
            var data = JSON.parse(json);
            var b = $.isEmptyObject(data);
            if(b){
                  $(".items").append("<h3 style='margin: 0 auto'>未找到该电影！</h3>");
            }
            if(data.code==0){
                  if ($('.items > h3').text()!=""){
                      return;
                  }
                  $(".items").append("<h3 style='margin: 0 auto'>别再往下看了，我也是有底线的！</h3>");
                  block_flag = false;
                  return;
            }
            var div_info = '';
            for(var i in data){
                var cookie_value = getCookie(data[i].movie_name);
                if(cookie_value!=null&&cookie_value!=''){
                    continue;
                }
                div_info += "<div class='item'> <div class='item-content'><div class='media pull-left'>";
                var play_addr = '';
                var fuck = ['btn btn-danger','btn btn-success','btn btn-primary'];
                var total_arr = data[i].total.split(' ');
                var total_watch = '';
                if(total_arr.length==2){
                    total_watch += '周末票房：' + total_arr[0] + ' 累计票房：'+ total_arr[1]
                }else {
                    total_watch += '累计票房：'+ total_arr[0]
                }
                for (var j in data[i].playAddr){
                    play_addr += '<a target="_blank" class="'+fuck[j]+'" type="button" href="'+data[i].playAddr[j]+'">播放</a>'
                }
                div_info += "<img src='"+data[i].img_addr+"'  class='img-thumbnail' alt='"+data[i].movie_name+"'></div><div class='text'><h1>"+data[i].movie_name+"</h1><h3>"+total_watch+"</h3><h4>评分："+data[i].grade+"</h4>"+play_addr+"</br><button class='btn' type='button' onclick='if(setCookie(\""+data[i].movie_name+"\",\""+data[i].movie_name+"\")){this.className=\"hidden\";}'>看过</button></div></div>";
            }
            $('.items').append(div_info);
        }
    });
    }
    if(type==1){
        block_flag = false;
    }
}
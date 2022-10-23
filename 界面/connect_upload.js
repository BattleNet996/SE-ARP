/*
@Time    : 2021/7/14 9:05 上午
@Author  : Tang Jiaxin
文件上传功能，向服务器上传文件
*/

function connect_upload()
{
    var file = document.getElementById("file_form");
    var file_name = file["input_file"].value;
    if(!file_name)
    {
        $("p#response").text("请选择文件！");
        return;
    }
    var index1 = file_name.lastIndexOf("_");
    var index2 = file_name.indexOf(".zip");
    var app_name = file_name.substring(index1 + 1, index2);
    var formData = new FormData(file);
    formData.append("app", app_name);
    formData.append("cookie", window.localStorage["cookie"]);
    $.ajax(
        {
            url: "http://114.212.189.166:8001/file_upload",
            type: "post",
            data: formData,
            dataType: "json",
            processData: false,
            contentType: false,
            xhr: function()
            {
                myXhr = $.ajaxSettings.xhr();
                if(myXhr.upload)
                {
                    myXhr.upload.addEventListener("progress", 
                    progressHandlingFunction, false);
                }
                return myXhr;
            },
            beforeSend: function()
            {
                ot = new Date().getTime();
                oloaded = 0;
            },
            success: function(message)
            {
                state = message["state"];
                if(state == 200)
                    $("p#response").text("文件上传成功");
                else
                    $("p#response").text("文件上传失败：" + message["msg"]);
                var return_button = document.getElementById("return");
                return_button.style.visibility = "visible";
            },
            error: function()
            {
                $("p#response").text("服务器连接失败");
                var return_button = document.getElementById("return");
                return_button.style.visibility = "visible";
            }
        }
    )
    function progressHandlingFunction(evt)
    {
        var nt = new Date().getTime();
        var pertime = (nt - ot) / 1000;
        ot = new Date().getTime();
        var perload = evt.loaded - oloaded;
        oloaded = evt.loaded;
        var speed = perload / pertime;
        speed = speed.toFixed(1);
        var resttime = ((evt.total - evt.loaded) / speed).toFixed(1);
        var percent = evt.loaded / evt.total * 100;
        $("p#response").text("当前速度：" + (speed / 1024).toFixed(2) 
        + "KB/s，剩余时间：" + resttime + "s，当前进度：" 
        + percent.toFixed(2) + "%");
    }
    var return_button = document.getElementById("return");
    return_button.style.visibility = "hidden";
}
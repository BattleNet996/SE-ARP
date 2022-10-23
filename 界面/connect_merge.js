/*
@Time    : 2021/7/13 14:49 下午
@Author  : Tang Jiaxin
向服务器发送文件合并和保存合并好的文件的请求
*/

//向服务器发送文件合并请求
function connect_merge()
{
    var items = document.getElementsByClassName("checkbox");
    var files = {"files": []};
    for(let i = 0; i < items.length; i++)
    {
        if(!items[i].checked)
            continue;
        var t = items[i].value.split(" ");
        var app = t[0];
        var file = t[1];
        if(!files["app"])
            files["app"] = app;
        else if(app != files["app"])
        {
            alert("选择的模型不属于同一APP");
            return;
        }
        files["files"].push(file);
    }
    if(files["files"].length < 2)
    {
        alert("请至少选择两个待合并的模型");
        return;
    }
    var timer = self.setInterval("connect_merge_process()", 1000);
    $.ajax(
        {
            url: "http://114.212.189.166:8001/file_merge",
            type: "post",
            dataType: "json",
            data: JSON.stringify(files),
            contentType:'application/json; charset=utf-8',
            success: function(message)
            {
                var state = message["state"];
                var tempname = message["file"];
                if(state == 200)
                {
                    window.clearInterval(timer);
                    display_result(tempname, app);
                }                    
                else
                {
                    window.clearInterval(timer);
                    alert("合并失败：" + message["msg"]);
                }                    
            },
            error: function()
            {
                window.clearInterval(timer);
                alert("服务器连接失败");
            }
        }
    )
    var button1 = document.getElementById("button1");
    button1.style.visibility = "hidden";
    var button2 = document.getElementById("button2");
    button2.style.visibility = "hidden";
    var merge_info = document.getElementById("merge");
    merge_info.style.visibility = "visible";
}

function connect_merge_process()
{
    $.ajax(
        {
            url: "http://114.212.189.166:8001/merge_process",
            type: "post",
            success: function(message)
            {
                var state = message["state"];
                if(state == 200)
                    $("p#merge").text(message["process"]);
                else
                    alert("合并失败：" + message["msg"]);
            },
            error: function()
            {
                alert("服务器连接失败");
            }
        }
    )
}

//向服务器发送保存合并好的文件的请求
function connect_save_result(tempname, filename, app)
{
    $.ajax(
        {
            url: "http://114.212.189.166:8001/save_result",
            type: "post",
            dataType: "json",
            data: JSON.stringify({'tempname': tempname,
            'filename': filename, 'app': app, 
            'cookie': window.localStorage["cookie"]}),
            contentType:'application/json; charset=utf-8',
            success: function(message)
            {
                var state = message["state"];
                if(state == 200)
                    merge_file();
                else
                    alert("保存失败：" + message["msg"]);
            },
            error: function()
            {
                alert("服务器连接失败");
            }
        }
    )
}

//向服务器发送删除合并好的文件的请求
function connect_delete_result(tempname)
{
    $.ajax(
        {
            url: "http://114.212.189.166:8001/abort_result",
            type: "post",
            dataType: "json",
            data: JSON.stringify({'tempname': tempname}),
            contentType:'application/json; charset=utf-8',
            success: function(message)
            {
                var state = message["state"];
                if(state == 200)
                    merge_file();
                else
                    alert("删除失败：" + message["msg"]);
            },
            error: function()
            {
                alert("服务器连接失败");
            }
        }
    )
}

//从模型合并界面跳转到结果展示界面，并展示合并结果
function display_result(tempname, app)
{
    window.location.assign("result.html?display_file="+ tempname
    + "&display_app=" + app);
}

//从结果展示界面跳转到模型合并界面
function merge_file()
{
    window.location.assign("merge.html");
}

//将合并完成后的文件保存至服务器
function save_result()
{
    var button1 = document.getElementById("button1");
    button1.style.visibility = "hidden";
    var button2 = document.getElementById("button2");
    button2.style.visibility = "hidden";
    var button3 = document.getElementById("button3");
    button3.style.visibility = "hidden";
    var button4 = document.getElementById("button4");
    button4.style.visibility = "hidden";
    var form = document.getElementById("form");
    form.style.visibility = "visible";
}

//放弃合并结果
function abort_result()
{
    var url = document.URL;
    var index1 = url.indexOf("display_file=");
    var index2 = url.indexOf("display_app=");
    var tempname = url.substring(index1 + 13, index2 - 1);
    connect_delete_result(tempname);
}

//取消保存
function cancel_save()
{
    var button1 = document.getElementById("button1");
    button1.style.visibility = "visible";
    var button2 = document.getElementById("button2");
    button2.style.visibility = "visible";
    var button3 = document.getElementById("button3");
    button3.style.visibility = "visible";
    var button4 = document.getElementById("button4");
    button4.style.visibility = "visible";
    var form = document.getElementById("form");
    form.style.visibility = "hidden";
}

//确认保存
function save()
{
    filename = document.getElementById("file_name");
    if(!filename.value)
    {
        alert("请输入文件名称");
        return;
    }
    var url = document.URL;
    var index1 = url.indexOf("display_file=");
    var index2 = url.indexOf("display_app=");
    var tempname = url.substring(index1 + 13, index2 - 1);
    var app = url.substring(index2 + 12);
    connect_save_result(tempname, filename.value, app);
}
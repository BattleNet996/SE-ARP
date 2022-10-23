/*
@Time    : 2021/7/13 15:11 下午
@Author  : Tang Jiaxin
文件下载与展示功能
*/

//以提交表单的形式从服务器下载文件
function download_file(file)
{
    var url = "http://114.212.189.166:8001/file_download";
    var requestForm = document.createElement("form");
    requestForm.action = url;
    requestForm.method = "post";
    var input = document.createElement("input");
    input.type = "hidden";
    input.name = "fileName";
    input.value = file;
    requestForm.appendChild(input);
    $(document.body).append(requestForm);
    requestForm.submit();
    requestForm.remove();
}

//从服务器下载一个文件
function connect_download_file()
{
    var url = document.URL;
    var index1 = url.indexOf("display_file=");
    var index2 = url.indexOf("display_app=");
    var file = "";
    if(index2 == -1)
        file = url.substring(index1 + 13);
    else
        file = url.substring(index1 + 13, index2 - 1);
    $.ajax(
        {
            url: "http://114.212.189.166:8001/file_download",
            type: "get",
            success: function()
            {
                download_file(file);
            },
            error: function()
            {
                alert("服务器连接失败");
            }
        }
    )
}

//从服务器获取一个文件的内容
function connect_display_file()
{
    var url = document.URL;
    var index1 = url.indexOf("display_file=");
    var index2 = url.indexOf("display_app=");
    var file = "";
    if(index2 == -1)
        file = url.substring(index1 + 13);
    else
        file = url.substring(index1 + 13, index2 - 1);
    $.ajax(
        {
            url: "http://114.212.189.166:8001/file_display",
            type: "post",
            dataType: "json",
            data: JSON.stringify({"file": file}),
            contentType:'application/json; charset=utf-8',
            success: function(message)
            {
                state = message["state"];
                if(state == 200)
                {
                    data = message["data"];
                    $("p#response").html(data);
                }
                else
                    $("p#response").text("结果获取失败：" + message["msg"]);
            },
            error: function()
            {
                $("p#response").text("服务器连接失败");
            }
        }
    )
}

//从服务器获取可视化界面
function connect_graph_display()
{
    var url = document.URL;
    var index = url.indexOf("display_file=");
    var file = url.substring(index + 13);
    $.ajax(
        {
            url: "http://114.212.189.166:8001/file_graph",
            type: "post",
            dataType: "json",
            data: JSON.stringify({"file": file}),
            contentType:'application/json; charset=utf-8',
            success: function(message)
            {
                state = message["state"];
                if(state == 200)
                {
                    data = message["data"];
                    document.write(data);
                }
                else
                    alert("可视化结果获取失败：" + message["msg"]);
            },
            error: function()
            {
                $("p#response").text("服务器连接失败");
            }
        }
    )
}

//跳转到可视化页面
function graph_display()
{
    var url = document.URL;
    var index1 = url.indexOf("display_file=");
    var index2 = url.indexOf("display_app=");
    var file = "";
    if(index2 == -1)
        file = url.substring(index1 + 13);
    else
        file = url.substring(index1 + 13, index2 - 1);
    window.location.assign("graph.html?display_file=" + file);
}

//展示一个文件列表
function display_file_list(file_list, show_input)
{
    var table = document.getElementById("table");
    table.innerHTML = "<th>编号</th><th>所属APP</th><th>文件名称</th><th>提交时间</th>";
    var index = 1;
    for(var app in file_list)
    {
        var files = file_list[app];
        for(let i = 0; i < files.length; i++)
        {
            var file = files[i]["file"];
            var time = files[i]["time"];
            var arr = file.split('/');
            var filename = arr[arr.length - 2];
            table.innerHTML += ("<tr>" 
            + "<td>" + index + "</td>"
            + "<td>" + app + "</td>"
            + "<td><a href='javascript:void(0);' onclick='display_file("
            + "\"" + file + "\"" + ")'>"
            + filename + "</a></td>"
            + "<td>" + time + "</td>"
            + "<td><input type='checkbox' class='checkbox' value='" 
            + app + " " + file + "'></td>"
            + "</tr>");
            index++;
        }
    }
    if(!show_input)
    {
        var items = document.getElementsByClassName("checkbox");
        for(let i = 0; i < items.length; i++)
            items[i].style.display = "none";
    }
}

//从服务器获取已经上传的文件的列表
function connect_display_file_list(show_input)
{
    $.ajax(
        {
            url: "http://114.212.189.166:8001/file_list",
            type: "post",
            dataType: "json",
            data: JSON.stringify({"cookie": window.localStorage["cookie"]}),
            contentType:'application/json; charset=utf-8',
            success: function(message)
            {
                state = message["state"];
                if(state == 200)
                    display_file_list(message["data"], show_input);
                else
                    $("p#response").text("文件读取失败");
            },
            error: function()
            {
                $("p#response").text("服务器连接失败");
            }
        }
    )
}

//从模型合并界面跳转到文件展示界面，并展示一个文件的内容
function display_file(file)
{
    window.location.assign("display.html?display_file="+ file);
}
/*
@Time    : 2021/6/1 20:04 下午
@Author  : Tang Jiaxin
文件删除功能
*/

//向服务器发送文件删除请求
function connect_remove_file()
{
    var items = document.getElementsByClassName("checkbox");
    var files = {"files": []};
    for(let i = 0; i < items.length; i++)
    {
        if(!items[i].checked)
            continue;
        var t = items[i].value.split(" ");
        var file = t[1];
        files["files"].push(file);
    }
    if(files["files"].length == 0)
    {
        alert("请选择待删除的文件");
        return;
    }
    $.ajax(
        {
            url: "http://114.212.189.166:8001/file_remove",
            type: "post",
            dataType: "json",
            data: JSON.stringify(files),
            contentType:'application/json; charset=utf-8',
            success: function(message)
            {
                var state = message["state"];
                if(state == 200)
                    connect_display_file_list(true);
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

//删除文件
function remove_file()
{
    var items = document.getElementsByClassName("checkbox");
    for(let i = 0; i < items.length; i++)
        items[i].style.display = "inline";
    var button2 = document.getElementById("button2");
    button2.style.visibility = "visible";
    var button4 = document.getElementById("button4");
    button4.style.visibility = "visible";
    var button1 = document.getElementById("button1");
    button1.style.visibility = "hidden";
    var button3 = document.getElementById("button3");
    button3.style.visibility = "hidden";
}

//取消删除文件
function cancel_remove()
{
    var items = document.getElementsByClassName("checkbox");
    for(let i = 0; i < items.length; i++)
        items[i].style.display = "none";
    var button2 = document.getElementById("button2");
    button2.style.visibility = "hidden";
    var button4 = document.getElementById("button4");
    button4.style.visibility = "hidden";
    var button1 = document.getElementById("button1");
    button1.style.visibility = "visible";
    var button3 = document.getElementById("button3");
    button3.style.visibility = "visible";
}
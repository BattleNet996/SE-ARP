/*
@Time    : 2021/7/12 20:13 下午
@Author  : Tang Jiaxin
登录注册功能，向服务器提交登录注册等请求
*/
function connect_register()
{
    var register_info = document.getElementById("register_form");
    var user_name = register_info["user_name"].value;
    var password = register_info["password1"].value;
    var password2 = register_info["password2"].value;
    if(!user_name)
    {
        alert("请输入用户名！");
        return;
    }
    if(!password || !password2)
    {
        alert("请输入密码！");
        return;
    }
    if(password != password2)
    {
        alert("两次输入的密码不一致！");
        return;
    }
    var user_name_reg = /^\w{1,20}$/;
    if(!user_name_reg.test(user_name))
    {
        alert("输入的用户名不合理！");
        return;
    }
    var password_reg = /^\w{6,20}$/;
    if(!password_reg.test(password))
    {
        alert("输入的密码长度太短或太长！");
        return;
    }
    var data = {"user_name": user_name, "password": password};
    $.ajax(
        {
            url: "http://114.212.189.166:8001/register",
            type: "post",
            dataType: "json",
            data: JSON.stringify(data),
            contentType:'application/json; charset=utf-8',
            success: function(message)
            {
                var state = message["state"];                
                if(state == 200)
                {
                    alert("注册成功！");
                    var uid = message["uid"];
                    window.localStorage["cookie"] = uid.toString();
                    window.localStorage["user_name"] = user_name;
                    window.location.assign("select.html");
                }
                else
                    alert("注册失败：" + message["msg"]);
            },
            error: function()
            {
                alert("服务器连接失败");
            }
        }
    )
}

function create_check_code()
{
    var alphabet = [];
    for(let c = 0; c <= 9; c++)
        alphabet.push(String.fromCharCode(48 + c));
    for(let c = 0; c <= 25; c++)
    {
        alphabet.push(String.fromCharCode(65 + c));
        alphabet.push(String.fromCharCode(97 + c));
    }
    function getRndInteger(min, max) {
        return Math.floor(Math.random() * (max - min)) + min;
    }
    var str = "";
    for(let i = 0; i < 4; i++)    
        str += alphabet[getRndInteger(0, 62)];    
    window.sessionStorage["check_code"] = str;
    return str;
}

function connect_check_code()
{
    var request = new XMLHttpRequest();
    request.open("post", "http://114.212.189.166:8001/check_code", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    request.responseType = "blob";
    request.onload = function()
    {
        if(this.status == 200)
        {
            var data = this.response;
            var img = document.createElement("img");
            img.onload = function(e) 
            {
                window.URL.revokeObjectURL(img.src); 
            };
            img.src = window.URL.createObjectURL(data);
            $("#check_code_img").html(img);
        }
    }
    var check_code_data = create_check_code();
    request.send(JSON.stringify({"str": check_code_data}));
}

function connect_login()
{
    var login_info = document.getElementById("login_form");
    var user_name = login_info["user_name"].value;
    var password = login_info["password"].value;
    var check_code = login_info["check_code"].value;
    if(!user_name)
    {
        alert("请输入用户名！");
        return;
    }
    if(!password)
    {
        alert("请输入密码！");
        return;
    }
    if(!check_code)
    {
        alert("请输入验证码！");
        return;
    }
    if(check_code != window.sessionStorage["check_code"])
    {
        alert("验证码错误！");
        return;
    }
    var data = {"user_name": user_name, "password": password};
    $.ajax(
        {
            url: "http://114.212.189.166:8001/login",
            type: "post",
            dataType: "json",
            data: JSON.stringify(data),
            contentType:'application/json; charset=utf-8',
            success: function(message)
            {
                var state = message["state"];
                var uid = message["uid"];
                var mail_addr = message["mail_addr"];
                if(state == 200)
                {
                    window.localStorage["cookie"] = uid.toString();
                    window.localStorage["user_name"] = user_name;
                    if(mail_addr)
                        window.localStorage["mail_addr"] = mail_addr;
                    window.location.assign("select.html");
                }
                else
                    alert("登录失败：" + message["msg"]);
            },
            error: function()
            {
                alert("服务器连接失败");
            }
        }
    )
}

function connect_mail_login()
{
    var login_info = document.getElementById("mail_login_form");
    var user_mail = login_info["user_mail"].value;
    if(!user_mail)
    {
        alert("请输入用户名或邮箱！");
        return;
    }    
    var check_code = create_check_code();
    var data = {"check_code": check_code};
    var index = user_mail.indexOf("@");
    if(index == -1)
        data["user_name"] = user_mail;
    else
        data["mail_addr"] = user_mail;
    $.ajax(
        {
            url: "http://114.212.189.166:8001/mail_login",
            type: "post",
            dataType: "json",
            data: JSON.stringify(data),
            contentType:'application/json; charset=utf-8',
            success: function(message)
            {
                var state = message["state"];
                var uid = message["uid"];
                var mail_addr = message["mail_addr"];
                var user_name = message["user_name"];
                if(state == 200)
                {
                    alert("邮件发送成功，请填写收到的验证码");
                    window.sessionStorage["check_code"] = check_code;
                    window.sessionStorage["cookie"] = uid.toString();
                    window.sessionStorage["mail_addr"] = mail_addr;
                    window.sessionStorage["user_name"] = user_name;
                }
                else
                    alert("邮件发送失败：" + message["msg"]);
            },
            error: function()
            {
                alert("服务器连接失败");
            }
        }
    )
}

function mail_login()
{
    var login_info = document.getElementById("mail_login_form");
    var check_code = login_info["check_code"].value;
    if(!check_code)
    {
        alert("请输入验证码！");
        return;
    }
    if(check_code != window.sessionStorage["check_code"])
    {
        alert("验证码错误！");
        return;
    }
    window.localStorage["cookie"] = window.sessionStorage["cookie"];
    window.localStorage["mail_addr"] = window.sessionStorage["mail_addr"];
    window.localStorage["user_name"] = window.sessionStorage["user_name"];
    window.location.assign("select.html");
}

function connect_change_password()
{
    var password_change_info = document.getElementById("password_change_form");
    var old_password = password_change_info["old_password"].value;
    var new_password = password_change_info["new_password1"].value;
    var new_password2 = password_change_info["new_password2"].value;
    if(!old_password)
    {
        alert("请输入旧密码！");
        return;
    }
    if(!new_password)
    {
        alert("请输入新密码！");
        return;
    }
    if(!new_password2)
    {
        alert("请再次输入新密码！");
        return;
    }
    if(new_password != new_password2)
    {
        alert("两次输入的新密码不一致！");
        return;
    }
    if(old_password == new_password)
    {
        alert("新密码不能与旧密码相同！");
        return;
    }
    var password_reg = /^\w{6,20}$/;
    if(!password_reg.test(new_password))
    {
        alert("新密码长度太短或太长！");
        return;
    }
    $.ajax(
        {
            url: "http://114.212.189.166:8001/change_password",
            type: "post",
            dataType: "json",
            data: JSON.stringify({'old_password': old_password,
            'new_password': new_password, 
            'cookie': window.localStorage["cookie"]}),
            contentType:'application/json; charset=utf-8',
            success: function(message)
            {
                var state = message["state"];
                if(state == 200)
                    alert("密码修改成功");
                else
                    alert("密码修改失败：" + message["msg"]);
            },
            error: function()
            {
                alert("服务器连接失败");
            }
        }
    )
}

function connect_mail_bind()
{
    var mail_bind_info = document.getElementById("mail_bind_form");
    var mail_addr = mail_bind_info["mail_addr"].value;
    if(!mail_addr)
    {
        alert("请输入邮箱！");
        return;
    }    
    var check_code = create_check_code();
    $.ajax(
        {
            url: "http://114.212.189.166:8001/mail_bind",
            type: "post",
            dataType: "json",
            data: JSON.stringify({"mail_addr": mail_addr, 
            "cookie": window.localStorage["cookie"], "check_code": check_code}),
            contentType:'application/json; charset=utf-8',
            success: function(message)
            {
                var state = message["state"];
                if(state == 200)
                {
                    alert("邮件发送成功，请填写收到的验证码");
                    window.sessionStorage["check_code"] = check_code;
                }
                else
                    alert("邮件发送失败：" + message["msg"]);
            },
            error: function()
            {
                alert("服务器连接失败");
            }
        }
    )
}

function connect_mail_update()
{
    var mail_bind_info = document.getElementById("mail_bind_form");
    var mail_addr = mail_bind_info["mail_addr"].value;
    var check_code = mail_bind_info["check_code"].value;
    if(!check_code)
    {
        alert("请输入验证码！");
        return;
    }
    if(check_code != window.sessionStorage["check_code"])
    {
        alert("验证码错误！");
        return;
    }
    if(!mail_addr)
    {
        alert("请输入邮箱！");
        return;
    }
    $.ajax(
        {
            url: "http://114.212.189.166:8001/mail_bind",
            type: "post",
            dataType: "json",
            data: JSON.stringify({"mail_addr": mail_addr,
            "cookie": window.localStorage["cookie"]}),
            contentType:'application/json; charset=utf-8',
            success: function(message)
            {
                var state = message["state"];
                if(state == 200)
                {
                    alert("邮箱绑定成功");
                    window.localStorage["mail_addr"] = mail_addr;   
                }                                                 
                else
                    alert("邮件发送失败：" + message["msg"]);
            },
            error: function()
            {
                alert("服务器连接失败");
            }
        }
    )
}

function get_user_info()
{
    $("p#user_name").text("用户名：" + localStorage["user_name"]);
    if(window.localStorage.getItem("mail_addr"))
        $("p#mail_addr").text("邮箱：" + localStorage["mail_addr"]);
    else
        $("p#mail_addr").text("邮箱：未绑定");
}

function exit_account()
{
    window.localStorage.removeItem("cookie");
    window.localStorage.removeItem("user_name");
    if(window.localStorage.getItem("mail_addr"))
        window.localStorage.removeItem("mail_addr");
    window.location.assign("entrance.html");
}
$(document).ready(function(){
	$("#sub").click(function(){
		alert("123");
		
		var username=$('#username').val();
		var password=$('#password').val();
		var email=$('#email').val();
		
		if(!username){
			alert("请先输入账号!");
			$("#username").focus();//获取焦点
			return ;
		}
		if(!password){
			alert("请先输入密码!");
			$("#password").focus();//获取焦点
			return ;
		}
		if(!email){
			alert("请先输入邮箱!");
			$("#email").focus();//获取焦点
			return ;
		}
		
		
		var param = {
			"username":username,
			"password":password,
			"email":email
		};
				  
		$.post("http://dk.ruut.cn:8001/AddDkUser",param,function(result){
			if(result==="success"){
				alter("success")
			}else{
				alert(result);
			}
		});
	});
	$("#del").click(function(){
		var username=$('#username').val();
		var password=$('#password').val();
		
		if(!username){
			alert("请先输入账号!");
			$("#username").focus();//获取焦点
			return ;
		}
		if(!password){
			alert("请先输入密码!");
			$("#password").focus();//获取焦点
			return ;
		}
		var param = {
			"username":username,
			"password":password,
		};
				  
		$.post("http://dk.ruut.cn:8001/DelDkUser",param,function(result){
			if(result==="success"){
				alter("success")
			}else{
				alert(result);
			}
		});
	});
	$("#res").click(function(){
		$('#username').val('');
		$("#password").val('');
		$("#email").val('');
	});
});
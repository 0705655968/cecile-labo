catalogID='15101';

function openWin(myURL,myW,myH,myName){
	var scWidthCenter=screen.availWidth/2;
	var scHeightCenter=screen.availHeight/2;
	option="toolbar=0,location=0,directories=0,status=0,menubar=0,scrollbars=0,resizable=0,width="+myW+",height="+myH+",left="+(scWidthCenter-(myW/2))+",top="+(scHeightCenter-(myH/2));
	var newWin=window.open(myURL,myName,option);
	newWin.window.focus();
}

function setParam(){
	var nombre = 0;
	var r_array = new Array();
	var r_array2 = new Array();
	var result = "";
	var sea_length = location.search.length;
	var equal_chara = location.search.indexOf("?")+1;
	if(sea_length>1){
		r_array = location.search.substring(equal_chara,sea_length).split("&");
	}
	for(i in r_array){
		r_array2.push(r_array[i].split("="));
		if(r_array2[i][0] == "directPage"){
			r_array2[i][1] -= nombre;
		}
		result += r_array2[i][0] + "=" + r_array2[i][1];
		if(r_array.length-1>i){
			result += "&";
		}
	}
	return unescape(result);
}

function quit(){
	window.close();
}

var cartWin;
function openCart(URL){
    if(window.navigator.userAgent.indexOf('Safari')===-1 && cartWin && !cartWin.closed){
        cartWin.close();
    }
    cartWin = window.open(URL,'cart');
    cartWin.focus();
}

function openPageCart(pageNum){
	pageNum=Math.max(1, Number(pageNum));

	headStr='http://www.cecile.co.jp/site/cmdtyinfo/digicata/ListSrv.jsp?micd=';
	JumpURL=headStr+catalogID+'&pgno='+pageNum;
	openCart(JumpURL);
}

function keyWordSearch(){
JumpURL='http://search2.cecile.co.jp/cgi-bin/s/search.cgi';
openCart(JumpURL);
}

function openHelp(){
helpWin=window.open('../dc_help/index.html','help','width=432,height=600,scrollbars=yes');
helpWin.focus();
}
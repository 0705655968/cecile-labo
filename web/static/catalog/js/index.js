$(function(){
	'use strict';
	var version = '3.0.5.2067'; // バージョン番号

	var xml_contents; //contents.xml格納用
	var xml_link;     //link.xml格納用
	var catalog_Menu; //カタログメニュー格納用

	//xmlから読み込む値
	var imgPrefix;    //画像ディレクトリまでのパス
	var opSpread;     //右開き・左開き
	var totalPages;   //総ページ数（1から数えた数）
	var bookW;        //1ページの幅
	var bookH;        //1ページの高さ
	var sliceW;       //スライス画像横幅
	var sliceH;       //スライス画像縦幅
	var pageStyle;		//ページスタイル（3:複数ページ用(最初の見開きが1ページ)、4:複数ページ用(最初の見開きが2ページ)、5:単ページ表示）
	var pdfStyle;     //PDFのスタイル（1：見開きのみ 2：見開き、片ページ両方 3：片ページのみ）
	var imgSize;      //使用画像サイズ
	var nombre;       //ページ数を数える場合の開始数
	var minusPage;    //マイナスページを表示するか（0:表示しない、1:表示する）
	var hidePages;    //非表示ページ（配列に変換）
	var turnPageType; //ページめくり方法（0:横スライド、1:3Dアニメ）
	var turnPageTime; //ページめくりの時間
	var shoppingHide; //商品購入ボタン非表示ページ
	var linkColor;    //リンクエリアの色
	var linkColor2;   //リンクエリアの色（マウスオーバー、強調時）
	var tagColorAry;  //付箋の色
	var tagMax;       //付箋の見開きごとの最大数

	//設定用変数
	var dblClickTime=300; //ダブルクリック判定間隔（ms）
	var zoomRatio=2;      //ズーム１回分の拡大率
	var borderW=5;        //ページ境界の線の幅
	var canvasZoom=2;     //canvasの拡大率
	var hideZero=true;    //pageStyle=4 のとき、0ページ目の表示（true:表示しない、false:表示する）

	//汎用変数
	var showPageNum;      //１度に表示するページ数（1/2）
	var pageZoom;         //ページ初期表示のズーム値
	var initZoom=1;       //初期ズーム値（最小値）※1で固定
	var maxZoom=4;        //最大ズーム値
	var curZoom;          //現在のズーム値
	var initImgSize;      //初期表示画像サイズ
	var curPage;          //現在のページ
	var prevPage;         //前のページのページ番号
	var nextPage;         //次のページのページ番号
	var windowW;          //ウインドウ横幅
	var windowH;          //ウインドウ高さ
	var viewW;            //表示エリア横幅
	var viewH;            //表示エリア高さ
	var isLeftEnd;        //左端ページ
	var isRightEnd;       //右端ページ
	var startPage=0;      //表示開始ページ
	var sliderMove=false; //スライダー動作中
	var history=[];       //「戻る」ボタン用
	var isZoomIn=true;    //クリックでズームイン（PCの場合）
	var wheelType;        //マウスホイール操作（0:拡大・縮小　1:紙面スクロール　2:ページ送り）
	var moveType;         //ページ移動時の表示サイズ（0:全体　1:拡大したまま）
	var catalogName='';   //データ保存用カタログ名
	var windowHideTimer;  //小ウィンドウ非表示用タイマー
	var scrollbarW;       //スクロールバー横幅
	var nombreData={};    //ページ表記データ保持
	var searchData;       //検索用jsonデータ保持
	var favoriteList;     //お気に入りページ
	var firstLoad=true;   //初回読み込み判定
	var sendGA;           //GA送信用関数
	var AreaNaviHeight    //エリアナビの高さ

	var ua = navigator.userAgent;
	var isIOS = (ua.indexOf('iPhone')!==-1 || ua.indexOf('iPad')!==-1 || ua.indexOf('iPod')!==-1);
	var isAndroid = (ua.indexOf('Android')!==-1);
	var isPC = (!isIOS && !isAndroid);
	var isIE = (ua.indexOf('MSIE')!==-1 || ua.indexOf('Trident')!==-1);
	var isMacSafari = (ua.indexOf('Macintosh')!==-1 && ua.indexOf('Safari')!==-1 && ua.indexOf('Chrome')===-1);

	var startEvent = 'touchstart mousedown';
	var moveEvent  = 'touchmove mousemove';
	var endEvent   = 'touchend mouseup touchcancel';

	if (isAndroid || isIOS){
		$('#HelpDialog .pc').hide();
	} else {
		$('#HelpDialog .sp').hide();
	}

	catalogName = location.pathname.split('/').slice(1,-1).join('_');

	if (isIOS){
		$('#Wrapper').on('touchmove', function(e){
			e.preventDefault();
		});
		$('.scrollArea, #BtnList .spScroll').on('touchmove', function(e){
			e.stopPropagation();
		});
	}

	if (isIOS || isAndroid){
		$('#SettingDialog .wheel').hide();
	}
	var localStorage;
	try{
		if(window.localStorage){
			localStorage = window.localStorage;
		} else {
			console.warn('window.localStorage が使えません');
		}
	} catch(e) {
		console.warn('window.localStorage が使えません');
	}

	/*-------------------------------------------------------------------------
	  汎用関数
	-------------------------------------------------------------------------*/
	function isMaxWidth(w){
		if (window.matchMedia){
			var q = window.matchMedia('(max-width: '+w+'px)');
			return q.matches;
		} else {
			return (window.innerWidth<=w);
		}
	}

	function isRightPage(page){
		if (pageStyle===5){
			return false;
		} else if (opSpread==='left'){
			return page%2===(pageStyle===4?1:0);
		} else {
			return page%2===(pageStyle===4?0:1);
		}
	}

	function getPageGroup(page){
		if (pageStyle===3){
			return page+(page+2)%2;
		} else if (pageStyle===4){
			return page+1-page%2;
		} else {
			return page;
		}
	}

	function getPageX(e){
		if (window.event && event.touches){
			return event.touches[0].pageX;
		} else {
			return e.pageX;
		}
	}

	function getPageY(e){
		if (window.event && event.touches){
			return event.touches[0].pageY;
		} else {
			return e.pageY;
		}
	}

	function round(n, p){
		return Math.round(n*Math.pow(10,p))/Math.pow(10,p);
	}

	function addZero(n, keta){
		n += '';
		while (n.length<keta){ n = '0'+n; }
		return n;
	}

	function makeColorStyle(color, alpha){
		return 'rgba('+parseInt(color.slice(2,4),16)+','+parseInt(color.slice(4,6),16)+','+parseInt(color.slice(6,8),16)+','+parseInt(alpha)/100+')';
	}

  function getUrlParam(name, url){
      if (!url) url = window.location.href;
      name = name.replace(/[\[\]]/g, "\\$&");
      var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
          results = regex.exec(url);
      if (!results) return null;
      if (!results[2]) return '';
      return decodeURIComponent(results[2].replace(/\+/g, " "));
  }

	/*-------------------------------------------------------------------------
	  xml読み込み
	-------------------------------------------------------------------------*/

	$('#Loading').show();
	$.ajax({
		type : 'GET',
		url : '/static/catalog/contents/'+getUrlParam('code')+'.xml',
		dataType : 'xml'
	}).done(function(data){
		xml_contents = data;
		var promise = [];
		if($('link', xml_contents).text()==='1'){
			var p1 = $.ajax({
				type : 'GET',
				url : 'index/link.xml',
				dataType : 'xml'
			}).done(function(data){
				xml_link = data;
			});
			promise.push(p1);
		}
		//pageCSV
		if ($('pageAssign', xml_contents).text()==='1' && $('pageAssign', xml_contents).attr('nombreFile')){
			var p2 = $.ajax({
				type : 'GET',
				url : $('pageAssign', xml_contents).attr('nombreFile'),
				dataType : 'text'
			}).done(function(data){
				nombreData = data.split(/[\r\n]+/).reduce(function(p,c){
					var temp=c.split(/,/);
			        p[temp[0]] = temp[1];
			        return p;
				},{});
			});
			promise.push(p2);
		}
		if($('catalogMenu', xml_contents).text()==='1' && $('catalogMenu', xml_contents).attr('adress')){
			var p3 = $.ajax({
				type : 'GET',
				url : $('catalogMenu', xml_contents).attr('adress'),
				dataType : 'xml'
			}).done(function(data){
				catalog_Menu = data;
			});
			promise.push(p3);
		}
		$.when.apply($, promise).always(function(){
			init();
		});
	}).fail(function(e,t){
		alert(t);
	});


	function init(){
		//定数設定
		imgPrefix = $('imgPrefix', xml_contents).text();
		opSpread = $('opSpread', xml_contents).text();
		totalPages = parseInt($('totalPages', xml_contents).text(),10);
		bookW = parseInt($('bookW', xml_contents).text());
		bookH = parseInt($('bookH', xml_contents).text());
		sliceW = parseInt($('sliceW', xml_contents).text());
		sliceH = parseInt($('sliceH', xml_contents).text());
		pageStyle = parseInt($('pageStyle', xml_contents).text());
		pdfStyle = parseInt($('pdf', xml_contents).attr('style'));
		imgSize = $('scaleSize', xml_contents).text().split(',');
		nombre = parseInt($('pageAssign', xml_contents).attr('nombre'));
		minusPage = parseInt($('pageAssign', xml_contents).attr('minusPage'));
		hidePages = $('hidePage', xml_contents).text().split(',');
		for (var i=0; i<hidePages.length; i++){ hidePages[i] = parseInt(hidePages[i]); }

		// 先頭ヘルプページ非表示処理
		if (hideZero && pageStyle===4 && !isPC ){ startPage = 1; }

		//表示するページがない場合
		if (totalPages<=hidePages.length){ return; }

		//ページ数設定
		if (Object.keys(nombreData).length > 0){
			$('#PageTotal').text(nombreData['total']);
		} else {
			$('#PageTotal').text(totalPages-1+nombre);
		}
		//要素の表示・非表示
		$('#PrintBtn').toggleClass('hide', $('printOut', xml_contents).text()!=='1');
		$('#PdfBtn').toggleClass('hide', $('pdf', xml_contents).text()!=='1');
		$('#SettingBtn').toggleClass('hide', $('configWin', xml_contents).text()!=='1');
		$('#HelpBtn').toggleClass('hide', $('help', xml_contents).text()!=='1' && $('help', xml_contents).text()!=='2');
		$('#CloseBtn').toggleClass('hide', $('quit', xml_contents).text()!=='1');

		$('#MenuKeyword').toggleClass('hide', $('otherMenu', xml_contents).text()!=='1');
		$('#MenuVisualMenu').toggleClass('hide', $('visualIndex', xml_contents).text()!=='1');
		if($('catalogMenu', xml_contents).text()!=='1'){
			$('#MenuCatalog ,#SpCatalogBtn').addClass('hide');
		}else{
			addCSSRule(
				'#MenuList #MenuCatalog ,#SpCatalogBtn',
				'color:'+'#'+$('catalogMenu', xml_contents).attr('textColor').replace('0x','')+';'+
				'background-color:'+'#'+$('catalogMenu', xml_contents).attr('color').replace('0x','')+';'
			);
			addCSSRule(
				'body.openMenu #MenuList #MenuCatalog:not(.current):not(.close):not(:hover)',
				'color:'+'#'+$('catalogMenu', xml_contents).attr('color').replace('0x','')+';'+
				'background-color:'+'#'+$('catalogMenu', xml_contents).attr('textColor').replace('0x','')+';'
			);
		}

		$('#PageBtnLeft, #PageBtnRight').toggleClass('hide', $('sideMenu', xml_contents).text()==='0');
		$('#AreaNavi').toggleClass('hide', $('areaNavi', xml_contents).text()==='0');
		if(isPC || $('pageSlidebar', xml_contents).text()!=='1'){
			$('body').addClass('hideSlidebar');
		}
		$('#HomeBtn').toggleClass('hide', $('homeBtn', xml_contents).text()!=='1');
		$('#ShareBtn').toggleClass('hide', $('shareBtn', xml_contents).text()!=='1');
		$('#ZoomInBtn, #ZoomOutBtn').toggleClass('hide', $('scaleBtn', xml_contents).text()!=='1');
		$('#TagBtn, #MenuTagList').toggleClass('hide', $('fusen', xml_contents).text()!=='1');
		$('#PageJumpArea').toggleClass('hide', $('pageAssign', xml_contents).text()==='0');
		$('#BackBtn, #SpBackBtn').toggleClass('hide', $('history', xml_contents).text()!=='1');
//		$('#UrlCopyBtn, #SpUrlCopy').toggleClass('hide', $('urlCopy', xml_contents).text()!=='1');
		$('#PenBtn').toggleClass('hide', $('penTool', xml_contents).text()!=='1');

		if ($('#MenuList li:visible').length>=5){
			$('body').addClass('maxMenu');
		}

		$('#Footer .block:visible').each(function(){
			if ($(this).width()===0){ $(this).hide(); }
		});

		//色設定
		function addCSSRule(selector, css){
			var sheets = document.styleSheets;
			var sheet = sheets[sheets.length-1];
			if (sheet.insertRule){
				sheet.insertRule(selector+'{'+css+'}', sheet.cssRules.length);
			} else if (sheet.addRule){
				sheet.addRule(selector, css, -1);
			}
		}
		var mainColor = '#'+$('mainColor', xml_contents).text().replace('0x','');
		var mainTextColor = '#'+$('mainTextColor', xml_contents).text().replace('0x','');
		var mainHoverColor = makeColorStyle($('mainColor', xml_contents).text(),'10');
		addCSSRule(
			'.cmnBtn,'+
			'#MenuList li,'+
			'#IndexList li.folder:before,'+
			'#PageSlider:before,'+
			'#AutoInterval li.current,'+
			'#SpMenuBtn,'+
			'.menuContent .closeBtn,'+
			'#PageBtnLeft,#PageBtnRight,'+
			'#AreaNavi,'+
			'#PageBtn li,'+
			'#AutoDirection li,'+
			'.dialog .btn',
			'background-color:'+mainColor+';'+
			'color:'+mainTextColor);
		if (isPC){
			addCSSRule(
				'#IndexList li:not(.midashi):not(.folder):hover,'+
				'#IndexList .folderTit:hover,'+
				'#SearchList li:hover,'+
				'#TagList li:hover,'+
				'.dialog .pageSelect li div:hover,'+
				'.visualList .img:hover:after',
				'background-color:'+mainHoverColor);
		}
		addCSSRule(
			'.checkbox input:checked + span:after,'+
			'#AreaNavi .toggleBtn:after,'+
			'#AreaNavi.close .toggleBtn:after,'+
			'#AreaNavi .toggleBtn,'+
			'#AreaNavi .area,'+
			'#PenTool .select li.selected:after',
			'border-color:'+mainColor);
		AreaNaviHeight = (bookH/bookW)*95;
		addCSSRule(
			'#AreaNavi .img img',
			'height:'+AreaNaviHeight+'px');
		addCSSRule(
			'body.openMenu #MenuList li:not(.current):not(.close):not(:hover),'+
			'.dialog .pageSelect strong',
			'color:'+mainColor);
		addCSSRule(
			'.dialog .pageSelect li div:before,'+
			'.dialog .pageSelect li div:after',
			'background-color:'+makeColorStyle($('mainColor', xml_contents).text(),'30'));

		var subColor = '#'+$('subColor', xml_contents).text().replace('0x','');
		var subTextColor = '#'+$('subTextColor', xml_contents).text().replace('0x','');
		addCSSRule(
			'#BtnList li,'+
			'#Footer .btnList.tool li,'+
			'.cmnBtn.cancel',
			'background-color:'+subColor+';'+
			'color:'+subTextColor);
		if($('history', xml_contents).text()==='1'){
			$('#BackBtn, #SpBackBtn').css('background-color', '#'+$('history', xml_contents).attr('color').replace('0x',''));
		}
		if($('urlCopy', xml_contents).text()==='1'){
			$('#UrlCopyBtn, #SpUrlCopy').css('background-color', '#'+$('urlCopy', xml_contents).attr('color').replace('0x',''));
		}
		if($('quit', xml_contents).text()==='1'){
			$('#CloseBtn').css('background-color', '#'+$('quit', xml_contents).attr('color').replace('0x',''));
			if($('quit', xml_contents).attr('textColor')){
				$('#CloseBtn').css('color', '#'+$('quit', xml_contents).attr('textColor').replace('0x',''));
			}else{
				$('#CloseBtn').css('color', '#FFFFFF');
			}
		}
		if(!isPC){
			addCSSRule(
				'#SliderArea',
				'padding-bottom: 60px'
			);
		}
		//リンク色設定
		var lc1 = $('link', xml_contents).attr('color1');
		var lc2 = $('link', xml_contents).attr('color2');
		var la1 = $('link', xml_contents).attr('alpha1').split(',');
		var la2 = $('link', xml_contents).attr('alpha2').split(',');
		linkColor = makeColorStyle(lc1,la1[0]);
		linkColor2 = makeColorStyle(lc1,la1[1]);
		var linkBorderColor = makeColorStyle(lc2,la2[0]);
		var linkBorderColor2 = makeColorStyle(lc2,la2[1]);
		addCSSRule(
			'.linkArea',
			'background-color:'+linkColor+';'+
			'border-color:'+linkBorderColor);
		addCSSRule(
			'.linkArea:hover',
			'background-color:'+linkColor2+' !important;'+
			'border-color:'+linkBorderColor2);

		//付箋
		tagColorAry = $('fusen', xml_contents).attr('color').split(',').map(function(s){ return s.replace('0x','').substr(0,6); });
		for (i=0; i<tagColorAry.length; i++){
			$('#TagColor .color'+(i+1)).css('background-color', '#'+tagColorAry[i]);
		}
		addCSSRule('.tagLayer .tag textarea', 'color:#'+$('fusen', xml_contents).attr('textColor').replace('0x',''));
		tagMax = parseInt($('fusen', xml_contents).attr('maximum'));
		if (isNaN(tagMax)){ tagMax = 5; }

		//背景
		if ($('background', xml_contents).text()==='1'){
			$('#SliderArea').css('background-image', 'url(index/bg.jpg)');
			if ($('background', xml_contents).attr('style')==='1'){
				$('#SliderArea').css('background-size', 'cover');
			}
		}

		//メニュー表示
		if ($('menuStyle', xml_contents).text()==='1' && !isMaxWidth(767)){
			var menuActive = $('menuStyle', xml_contents).attr('active');
			var activeIndex = 0;
			var menuArray = ['text','visual','otherMenu','fusen','favorite','catalog'];
			if($.inArray( menuActive, menuArray) >=0){ activeIndex = $.inArray( menuActive, menuArray)};

			$('#MenuList li').eq(activeIndex).addClass('current');
			$('.menuContent').eq(activeIndex).show();
			$('body').addClass('openMenu');
		}

		//キーワード検索用 JSON読み込み
		if ($('otherMenu', xml_contents).text()==='1'){
			$.ajax({
				type : 'GET',
				url : 'search.json',
				dataType : 'json'
			}).done(function(data){
				searchData = data;
			});
		}

		//ページめくりアニメーション
		turnPageType = $('flipAnimation', xml_contents).text()==='0'?0:1;
		turnPageTime = 8/(parseInt($('flipAnimation', xml_contents).attr('speed')) || 30);
		addCSSRule(
			'#SliderArea li.turn.L .pageL,'+
			'#SliderArea li.turn.nextL.move .pageR,'+
			'#SliderArea li.turn.R .pageR,'+
			'#SliderArea li.turn.nextR.move .pageL',
			'-webkit-animation-duration:'+turnPageTime/2+'s;'+
			'animation-duration:'+turnPageTime/2+'s');

		//ページの影
		$('body').toggleClass('hideBookShadow', $('bookShadow', xml_contents).text()==='0');
		$('body').toggleClass('showPageLine', $('pageShadow', xml_contents).text()==='2');

		//ビジュアルメニュー 単ページ
		$('.visualList').toggleClass('single', pageStyle===5);

		//ロゴ表示
		if ($('logo', xml_contents).text()==='1' && $('homeBtn', xml_contents).text()!=='1'){
			if($('logo', xml_contents).attr('adress') !== ""){
				$('#Logo').html('<a href="'+$('logo', xml_contents).attr('adress')+'" target="_blank"><img src="/static/catalog/img/logo.jpg" alt=""></a>');
			}else{
				$('#Logo').html('<img src="index/logo.jpg" alt="">');
			}
			$('body').addClass('hasLogo');
		}

		//右開き 調整
		if (opSpread==='right'){
			$('#PageBtn .leftEnd').text('最後へ');
			$('#PageBtn .left').text('次のページへ');
			$('#PageBtn .right').text('前のページへ');
			$('#PageBtn .rightEnd').text('先頭へ');
			$('#AutoDirection li').eq(0).text('逆送り').removeClass('current');
			$('#AutoDirection li').eq(1).text('順送り').addClass('current');
			autoReverse = true;
			$('.visualList').addClass('opRight');
		}

		//カタログ請求
		if ($('catalogOrder', xml_contents).text()==='1'){
			$('#CatalogBtn').on('click', function(){
				window.open($('catalogOrder', xml_contents).attr('adress'), '_blank');
			});
		} else {
			$('#CatalogBtn').hide();
		}

		//PDF
		if (pdfStyle===1){
			$('#PdfDialog').find('.left, .right').hide();
		} else if (pdfStyle===3){
			$('#PdfDialog').find('.both').hide();
		}

		//自動再生
		if ($('autoPlay', xml_contents).text()==='1'){
			var autoPlayTime = $('autoPlay', xml_contents).attr('time').split(',');
			for (i=0; i<Math.min(4,autoPlayTime.length); i++){
				$('#AutoInterval ul').append('<li><span>'+autoPlayTime[i]+'</span>秒</li>');
			}
			var autoPlayInit = Math.min(1,$('#AutoInterval li').length-1);
			$('#AutoInterval li').eq(autoPlayInit).addClass('current');
			autoInterval = autoPlayTime[autoPlayInit]*1000+500;
		} else {
			$('#AutoBtn,#SpAutoBtn').hide();
		}

		//お気に入りボタン
		if ($('favorite', xml_contents).text()==='1'){
			$('#FavoriteBtn, #SpFavoriteBtn, #SpFavorite').css({
				backgroundColor: '#'+$('favorite', xml_contents).attr('color').replace('0x',''),
				color: '#'+$('favorite', xml_contents).attr('textColor').replace('0x','')
			});
		} else {
			$('#FavoriteBtn, #SpFavoriteBtn, #SpFavorite, #MenuFavorite').hide();
		}

		//商品購入ボタン
		if ($('shoppingPage', xml_contents).text()==='1'){
			$('#PurchaseBtn, #SpPurchaseBtn').css({
				backgroundColor: '#'+$('shoppingPage', xml_contents).attr('color').replace('0x',''),
				color: '#'+$('shoppingPage', xml_contents).attr('textColor').replace('0x','')
			});
			if ($('shoppingPage', xml_contents).attr('inactive')){
				shoppingHide = $('shoppingPage', xml_contents).attr('inactive').split(',').map(function(x){ return parseInt(x); });
			} else {
				shoppingHide = [];
			}
		} else {
			$('#PurchaseBtn, #SpPurchaseBtn').addClass('hide');
		}

		//マウスオーバー画像
		if ($('link', xml_contents).attr('explainImg')){
			$('#Tooltip').html('<img src="'+$('link', xml_contents).attr('explainImg')+'" alt="">');
			setTooltip('.pageArea .linkLayer', '.linkArea');
		}

		// Google Analytics 設定
		if ($('googleAnalytics', xml_contents).text()==='1'){
			var gatitle = $('title').text();
			if($('catalogTitle', xml_contents).text() !== ''){
				gatitle = $('catalogTitle', xml_contents).text();
			}
			var gapath = location.pathname;
			if(location.search === ''){
				gapath = gapath + '?directPage=';
			}else{
				gapath = gapath + '?' + location.search.slice(1).split('&').filter(function(i) {
					return (i.indexOf('directPage=') !== 0);
				}).concat('directPage=').join('&');
			}
			sendGA = function(p,n){
				// p := directPage=p
				// n := P.2-3
				if(typeof(ga) === 'function'){
					ga('set','page',  gapath + p);
					ga('set','title', gatitle + ' ' + n);
					ga('send','pageview');
				}
			};
		}

		//スクロールバー幅取得
		$('html').css('overflow-y', 'scroll');
		scrollbarW = window.innerWidth - $(window).width();
		$('html').css('overflow-y', 'auto');

		//パラメータ判定
		var url = location.href;
		if (url.match(/directPage=(-?\d+)/)){
			curPage = parseInt(RegExp.$1)-nombre;
		} else if (location.hash.match(/^#(-?\d+)/)){
			curPage = parseInt(RegExp.$1)-nombre;
		} else {
			curPage = 0;
		}

		$('#Wrapper').css('opacity', '1');
		setSize();
		makeIndex();
		makeVisualMenu();
		makeCatalogMenu();
		makeFavoriteList();
	}


	/*-------------------------------------------------------------------------
	  リサイズ時処理
	-------------------------------------------------------------------------*/
	var resizeTimer;
	$(window).resize(function(){
		clearTimeout(resizeTimer);
		resizeTimer = setTimeout(function(){
			closePenTool();
			setSize();
		}, 100);
	});

	function setSize(isForce){
		//縦長・横長判定（表示枚数変更）
		if (!isForce){
			if (!isPC && windowW===window.innerWidth){
				return;
			}
			if (pageStyle!==5 && $(window).width()>$(window).height()){
				showPageNum = 2;
			} else {
				showPageNum = 1;
			}
		}
		if (isMaxWidth(767)){
			$('body').removeClass('openMenu');
			$('#MenuList li').removeClass('current');
			$('#MenuContentArea').hide();
		}else{
			$('#MenuContentArea').show();
			if($('#MenuList li').hasClass('current') !== true){
				$('#MenuContentArea').children('div').hide();
			}
		}
		$('body').toggleClass('turn3D', turnPageType===1 && showPageNum===2);
		$('body').toggleClass('hidePageShadow', showPageNum===1 ||  $('pageShadow', xml_contents).text()==='0');

		//ページ高さ・幅設定
		windowH = window.innerHeight;
		windowW = window.innerWidth;
		viewH = $('#SliderArea').height();
		viewW = $('#SliderArea').width();
		borderW = isMaxWidth(767)?30:145;

		//ページにフィットするよう調整
		pageZoom = Math.min(viewH/bookH, viewW/(bookW*showPageNum));
		maxZoom  = imgSize[imgSize.length - 1] / pageZoom;

		if (turnPageType===1 && showPageNum===2){
			$('#SliderArea ul').css('width', 'auto').css('left', '0');
			$('#SliderArea li').css('left', (viewW+borderW)+'px').css('border-right-width', '0');
		} else {
			$('#SliderArea ul').css('width', (viewW+borderW)*3+'px').css('left', -1*(viewW+borderW)+'px');
			$('#SliderArea li').css('left', '0').css('border-right-width', borderW+'px');
		}
		$('#SliderArea li').css('width', viewW+'px');
		$('#SliderArea .pageAreaInner').css({
			width: Math.round(bookW*showPageNum*pageZoom)+'px',
			height: Math.round(bookH*pageZoom)+'px'
		});
		$('#SliderArea canvas')
			.attr('width', Math.round(bookW*showPageNum*canvasZoom))
			.attr('height', Math.round(bookH*canvasZoom));
		jq_areaNavi.css({
			left: '290px',
			top: (windowH-260)+'px'
		});
		$('#BtnList .spScroll').css('max-height', windowH-45-82+'px');

		//ページスライダー幅
		var footerWidth = 0;
		$('#Footer .block:visible').each(function(){
			footerWidth += $(this).outerWidth(true);
		});
		$('#PageSliderArea').css('max-width', footerWidth+'px');

		if (viewW>bookW*showPageNum*4){
			initImgSize = 3;
		} else if (viewW>bookW*showPageNum*2){
			initImgSize = 2;
		} else {
			initImgSize = 1;
		}

		zoomReset();

		//ページ読み込み
		jumpPage(curPage);
	}

	//ズーム初期化
	function zoomReset(){
		if (isPC && !isMacSafari){
			$('#SliderArea .pageArea').css({
				width: Math.round(bookW*showPageNum*pageZoom)+'px',
				height: Math.round(bookH*pageZoom)+'px'
			});
			$('#SliderArea .pageAreaInner').css('transform', 'scale('+initZoom+')');
			jq_areaNavi.hide();
		} else {
			$('#SliderArea .pageAreaInner').css('zoom', initZoom);
		}
		curZoom = initZoom;

		$('.linkArea' ).css('border-width',  1/initZoom+'px');
		$('.linkLayer').css('top',          -1/initZoom+'px');
		$('.linkLayer').css('left',         -1/initZoom+'px');

		var pageW = bookW*showPageNum*pageZoom;
		var pageH = bookH*pageZoom;
		$('.pageArea')
			.css('left', (viewW-pageW)/2+'px')
			.css('top', (viewH-pageH)/2+'px');

		if (isPC){
			isZoomIn = true;
			$('#SliderArea').removeClass('max');
			if (isIE){ $('#SliderArea').css('cursor', 'url(img/cursor_zoomin.cur), auto'); }
		}
	}


	/*-------------------------------------------------------------------------
	  ページジャンプ
	-------------------------------------------------------------------------*/
	function jumpPage(index, isSearch){
		index = parseInt(index, 10);
		if (isNaN(index)){ return; }
		if (!isSearch){ isKeywordSearch = false; }

		var changeNum = showPageNum;
		curPage = index;
		isLeftEnd = false;
		isRightEnd = false;
		if (showPageNum===2 && (pageStyle===3 && curPage%2===0 || pageStyle===4 && curPage%2===1)){ curPage--; }

		$('#SliderArea .pageArea').eq(1).find('.thumbnail, .mainImg, .linkLayer, .tagLayer').html('');

		setTimeout(function(){
			zoomReset();
			for(;;){
				var result = loadPage(1, curPage);
				if (result==='success'){ break; }
				else if (result==='end'){ changeNum = -1*showPageNum; }
				curPage += changeNum;
			}
			loadNextPage();
			loadPrevPage();
			pageChange();
		}, 100);
	}

	function emLink(){
		$('.pageArea').eq(1).find('.linkArea').css('background-color', linkColor2);
		setTimeout(function(){
			$('.pageArea').eq(1).find('.linkArea').css('background-color', linkColor);
		},500);
	}

	//ページ移動時処理
	function pageChange(){
		//ページ移動ボタンの表示・非表示
		$('#PageBtnLeft, #TagAppend .leftBtn').toggle(!isLeftEnd);
		$('#PageBtnRight, #TagAppend .rightBtn').toggle(!isRightEnd);

		makePageNum(curPage);
		if (Object.keys(nombreData).length > 0){
			if (showPageNum===1 || curPage>=totalPages-1){
				$('#PageInput').val(nombreData[curPage]);
			} else {
				$('#PageInput').val(nombreData[curPage+1]);
			}
		} else {
			var page = curPage+nombre+((showPageNum===1 || curPage>=totalPages-1)?0:1);
			$('#PageInput').val(page<=0?'':page);
		}
		var range = ($('#PageSliderArea').width()-$('#PageSlider').width())/((showPageNum===1? totalPages-startPage:Math.ceil((totalPages+((pageStyle===3)?1:0))/2))*2-2);
		$('#PageSlider').css(opSpread, range*2*(showPageNum===1? curPage-startPage:Math.floor((curPage-startPage+1)/2))+'px');

		if (history.length===0 || history[history.length-1]!==curPage){
			history.push(curPage);
			if (history.length>1){
				$('#BackBtn, #SpBackBtn').removeClass('disabled');
			}
			if (history.length>parseInt($('history', xml_contents).attr('historyMax'))){
				history.shift();
			}
		}

		if (!$('#PurchaseBtn').hasClass('hide')){
			$('#PurchaseBtn, #SpPurchaseBtn').removeClass('disabled');
			for (var i=0; i<shoppingHide.length; i++){
				if (curPage===shoppingHide[i] || showPageNum===2 && getPageGroup(curPage)===getPageGroup(shoppingHide[i])){
					$('#PurchaseBtn, #SpPurchaseBtn').addClass('disabled');
					break;
				}
			}
		}

		jq_areaNavi.find('.img').html($('.pageArea').eq(1).find('.thumbnail').html());
		jq_areaNavi.toggleClass('single', showPageNum===1);

		//検索キーワードハイライト
		if (isKeywordSearch){
			if (curPage>=0){ showSearchHighlight(curPage, (opSpread==='right' && showPageNum===2)); }
			if (showPageNum===2 && curPage+1<totalPages){ showSearchHighlight(curPage+1, opSpread==='left'); }
		} else {
			$('.searchWord').remove();
		}

		//リンク強調
		setTimeout(emLink,100);

		if (firstLoad){
			showHighlight();
			firstLoad = false;
		} else {
			$('.pageArea .highlight').html('');
		}

		//めくり時不具合対策
		$('#SliderArea ul').removeClass('move');
		$('#SliderArea li').removeClass('turn L nextL R nextR move');

		//GA送信
		if (typeof(sendGA) === 'function'){
			var pagenum = Math.max(curPage+nombre, startPage+nombre);
			var pagetext = 'P.' + pagenum;
			if(showPageNum === 2 && curPage >= startPage && curPage < totalPages - 1){
				pagetext = pagetext + '-' + (pagenum+1);
			}
			sendGA(pagenum, pagetext);
		}
	}

	//ページ数表示
	var jq_pageNum = $('#PageNum');
	function makePageNum(page){
		var left = (page>=startPage)? Math.max(page+nombre, startPage+nombre):'';
		var right = (showPageNum===2 && page<totalPages-1)? page+1+nombre:'';
		
		if (Object.keys(nombreData).length > 0){
			if(left!==''){ left = nombreData[page]; }
			if(right!==''){ right = nombreData[page+1]; }
			
			if ((!isFinite(left) || left==='') && (!isFinite(right) || right==='')){
				jq_pageNum.text(left + (left!=='' && right!=='' ? '-':'')+ right);
			} else if ((!isFinite(left) || left==='') && isFinite(right)){
				jq_pageNum.text(left + (left!=='' && right!=='' ? '-':'')+'P.'+ right);
			} else {
				jq_pageNum.text('P.'+left + (left!=='' && right!=='' ? '-':'') + right);
			}
			
		} else {

			if (left<=0 && minusPage===0){ left = ''; }
			else if (left<0){ left = '('+left+')'; }

			if (right!=='' && right<=0 && minusPage===0){ right = ''; }
			else if (right!=='' && right<0){ right = '('+right+')'; }

			jq_pageNum.text('P.'+left + (left!=='' && right!=='' ? '-':'') + right);

			if (jq_pageNum.text()==='P.'){ jq_pageNum.addClass('hide'); }
			else { jq_pageNum.removeClass('hide'); }
		}
	}

	//検索キーワードハイライト
	function showSearchHighlight(page, isRight){
		$.ajax({
			type : 'GET',
			url : 'index/search/'+addZero(page,4)+'.xml',
			dataType : 'xml'
		}).done(function(data){
			var matchIndex = [];
			var pageW = parseFloat($('page', data).attr('w'));
			var pageH = parseFloat($('page', data).attr('h'));
			var i,j;
			for (i=0; i<searchWords.length; i++){
				j = 0;
				var tempAry = [];
				$('text', data).each(function(k,ele){
					if (j>0 && $(ele).attr('s').match(/[!#$%&\(\)\+,\-\.=@\[\]^_{}~'\*\/:;<>?\\`|｡｢｣､･、。，．・：；？！―‐／＼～∥｜…‥‘’“”（）〔〕［］｛｝〈〉《》「」『』【】─│┌┐┘└├┬┤┴┼━┃┏┓┛┗┣┳┫┻╋┠┯┨┷┿┝┰┥┸╂㌍〝〟＇＂]/)){
						tempAry.push(k);
						return;
					} else if (j>0 && $(ele).attr('s')!==searchWords[i][j]){
						j = 0;
						tempAry = [];
					}
					if ($(ele).attr('s')===searchWords[i][j]){
						tempAry.push(k);
						j++;
						if (searchWords[i].length===j){
							j = 0;
							matchIndex.push(tempAry);
							tempAry = [];
						}
					}
				});
			}
			var $word;
			for (i=0; i<matchIndex.length; i++){
				for (j=0; j<matchIndex[i].length; j++){
					var $t = $('text', data).eq(matchIndex[i][j]);
					var textX = parseFloat($t.attr('x'));
					var textY = parseFloat($t.attr('y'));
					var textW = parseFloat($t.attr('w'));
					var textH = parseFloat($t.attr('h'));
					if (j===0 || $word.data('y')!==textY){
						$word = $('<div class="searchWord"></div>');
						$word.data({
							x: textX,
							y: textY,
							w: textW,
							h: textH
						}).css({
							left: (textX*bookW/pageW+(isRight?bookW:0))*pageZoom+'px',
							top: textY*bookH/pageH*pageZoom+'px',
							width: textW*bookW/pageW*pageZoom+'px',
							height: textH*bookH/pageH*pageZoom+'px'
						});
						$('.pageArea').eq(1).find('.linkLayer').prepend($word);
					} else {
						if ($word.data('h')<textH){
							$word.data('h', textH).css('height', textH*bookH/pageH*pageZoom+'px');
						}
						$word.css('width', (textX-$word.data('x')+textW)*bookW/pageW*pageZoom+'px');
					}
				}
			}
			isKeywordSearch = false;
		});
	}


	/*-------------------------------------------------------------------------
	  ページ移動スライダ
	-------------------------------------------------------------------------*/
	$('#PageSlider').on(startEvent, function(e){
		e.preventDefault();
		e.stopPropagation();

		//1ページの場合
		if (isLeftEnd && isRightEnd){ return; }
		if (window.event && event.touches &&  event.touches.length>1){ return; }

		sliderMove = true;

		var slideMax = $('#PageSliderArea').width()-$('#PageSlider').width();
		var jq_slider = $('#PageSlider');
		var range = slideMax/((showPageNum===1? totalPages-startPage:Math.ceil((totalPages+(pageStyle===3?1:0))/2))*2-2);
		var newPage = curPage;

		var touchX;
		if (window.event && event.touches){ touchX = event.touches[0].pageX; }
		else { touchX = e.pageX; }

		var moveX = null;
		var initX = parseInt(jq_slider.css(opSpread));

		$('#PageNum').addClass('show');

		$(document).on(moveEvent, function(e){
			e.preventDefault();

			if (window.event && event.touches){ moveX = event.touches[0].pageX; }
			else { moveX = e.pageX; }

			var newX = Math.max(0, Math.min(slideMax, initX+(moveX-touchX)*(opSpread==='left'?1:-1)));
			jq_slider.css(opSpread, newX+'px');
			
			if (pageStyle===3){
				newPage = startPage+(1-showPageNum)+Math.round(newX/(range*2))*showPageNum;
			} else {
				newPage = Math.round(newX/(range*2))*showPageNum;
			}
			makePageNum(newPage);

		}).on(endEvent, function(){
			$(document).off(moveEvent);
			$(document).off(endEvent);
			if (newPage!==curPage){ jumpPage(newPage); }
			else { pageChange(); }
			$('#PageNum').removeClass('show');
			sliderMove = false;
		});
	});

	$('#PageSliderArea').on(startEvent, function(e){
		if (window.event && event.touches &&  event.touches.length>1){ return; }
		var range = ($('#PageSliderArea').width()-$('#PageSlider').width())/((showPageNum===1? totalPages-startPage:Math.ceil(totalPages/2))*2-2);
		var touchX = (window.event && event.touches)? event.touches[0].pageX : e.pageX;
		var newX = touchX-$('#PageSliderArea').offset().left;
		if(opSpread==='right'){ newX = $('#PageSliderArea').width() - newX;}
		newX = newX - $('#PageSlider').width()/2;
		$('#PageSlider').css(opSpread, newX+'px');
		jumpPage(Math.round(newX/(range*2))*showPageNum);
	});


	/*-------------------------------------------------------------------------
	  ページ読み込み
	-------------------------------------------------------------------------*/
	function loadPrevPage(){
		var index = (opSpread==='left')? 0:2;
		prevPage = curPage-showPageNum;
		for (;;){
			var result = loadPage(index, prevPage);
			if (result==='success'){ break; }
			if (result==='start'){
				if (opSpread==='left'){ isLeftEnd = true; }
				else { isRightEnd = true; }
				break;
			} else{
				prevPage -= showPageNum;
			}
		}
	}

	function loadNextPage(){
		var index = (opSpread==='left')? 2:0;
		nextPage = curPage+showPageNum;
		for(;;){
			var result = loadPage(index, nextPage);
			if (result==='success'){ break; }
			else if (result==='end'){
				if (opSpread==='left'){ isRightEnd = true; }
				else { isLeftEnd = true; }
				break;
			} else {
				nextPage += showPageNum;
			}
		}
	}

	//見開きページを読み込み
	function loadPage(boxNum, pageNum){
		scrollTo(0,1);
		if (showPageNum===2){
			if (opSpread==='left'){ return loadImage($('#SliderArea .pageArea').eq(boxNum), pageNum, pageNum+1); }
			else { return loadImage($('#SliderArea .pageArea').eq(boxNum), pageNum+1, pageNum); }
		} else {
			return loadImage($('#SliderArea .pageArea').eq(boxNum), pageNum);
		}
	}

	//画像読み込み
	function loadImage(jq_page, pageLeft, pageRight){
		var htmlStr='';
		var imgSrcL, imgSrcR;
		var thumSrc;

		clearCanvas(jq_page.find('canvas').get(0).getContext('2d'));
		jq_page.find('.thumbnail, .mainImg, .linkLayer, .tagLayer').html('');
		jq_page.addClass('empty').data('imgSrcL', null).data('imgSrcR', null);

		//冊子のラスト
		if (pageLeft>=totalPages && pageRight===void(0) || pageLeft>=totalPages && pageRight!==void(0) && pageRight>=totalPages){
			return 'end';
		}

		//すべてhideページの場合
		if ($.inArray(pageLeft, hidePages)!==-1 && ($.inArray(pageRight, hidePages)!==-1 || pageRight===void(0))){
			return 'hide';
		}

		//画像パス生成・サムネイルhtml生成
		if (pageLeft>=startPage && pageLeft<totalPages && $.inArray(pageLeft, hidePages)===-1){
			imgSrcL = imgPrefix+'/'+addZero(pageLeft,4)+'/';

			htmlStr += '<div class="pageL"><img src="'+imgSrcL+'tmb.jpg" width="'+Math.round(bookW*showPageNum*pageZoom)/showPageNum+'" height="'+Math.round(bookH*pageZoom)+'"></div>';
			thumSrc = imgSrcL+'tmb.jpg';
		}
		if (pageRight!==void(0) && pageRight>=startPage && pageRight<totalPages && $.inArray(pageRight, hidePages)===-1){
			imgSrcR = imgPrefix+'/'+addZero(pageRight,4)+'/';

			htmlStr += '<div class="pageR"><img src="'+imgSrcR+'tmb.jpg" width="'+Math.round(bookW*showPageNum*pageZoom)/showPageNum+'" height="'+Math.round(bookH*pageZoom)+'"></div>';
			thumSrc = imgSrcR+'tmb.jpg';
		}

		//冊子の先頭
		if (!imgSrcL && !imgSrcR){
			return 'start';
		}
		jq_page.removeClass('empty');

		//片面判定
		jq_page.toggleClass('onlyR', showPageNum===2 && (pageStyle===3 && opSpread==='left' && pageLeft===-1 || opSpread==='right' && pageLeft===totalPages));
		jq_page.toggleClass('onlyL', showPageNum===2 && (pageStyle===3 && opSpread==='right' && pageRight===-1 || opSpread==='left' && pageRight===totalPages));

		jq_page.toggleClass('single', showPageNum===1);

		//サムネイルを先に表示
		var thumImg = new Image();
		var setting = false;
		$(thumImg).on('load', function(){
			if (!setting){
				setting = true;
				$('#Loading').hide();
				jq_page.data('imgSrcL', imgSrcL);
				jq_page.data('imgSrcR', imgSrcR);
				jq_page.find('.mainImg.size1').html(makeImgHtml(imgSize[initImgSize], imgSrcL, imgSrcR));
				//リンク表示
				if (imgSrcL){ setLink(jq_page.find('.linkLayer'), pageLeft); }
				if (imgSrcR){ setLink(jq_page.find('.linkLayer'), pageRight, true); }
				//付箋・ペン表示
				setPageTag(jq_page, opSpread==='left'||showPageNum===1?pageLeft:pageRight);
				drowPen(jq_page.find('canvas').get(0).getContext('2d'), pageLeft);
			}
		});
		thumImg.src = thumSrc;
		jq_page.find('.thumbnail').html(htmlStr);

		return 'success';
	}

	function makeImgHtml(n, imgSrcL, imgSrcR){
		//html生成
		n = parseInt(n);
		if (isNaN(n)){ n = 2; }
		var htmlStrL = '';
		var htmlStrR = '';
		var edgePixW = bookW*n%sliceW===0? sliceW:bookW*n%sliceW;
		var edgePixH = bookH*n%sliceH===0? sliceH:bookH*n%sliceH;
		var sliceNumW = Math.ceil(bookW*n/sliceW);
		var sliceNumH = Math.ceil(bookH*n/sliceH);
		var i,j,w,h;
		for (i=0; i<sliceNumH; i++){
			if (imgSrcL){
				for (j=i*sliceNumW; j<(i+1)*sliceNumW; j++){
					w = ((j+1)%sliceNumW===0)? edgePixW:sliceW;
					h = (i===sliceNumH-1)? edgePixH:sliceH;
					htmlStrL += '<img src="'+imgSrcL+n+'00_'+j+'.jpg" width="'+w*pageZoom/n+'" height="'+h*pageZoom/n+'">';
				}
			}
			if (imgSrcR){
				for (j=i*sliceNumW; j<(i+1)*sliceNumW; j++){
					w = ((j+1)%sliceNumW===0)? edgePixW:sliceW;
					h = (i===sliceNumH-1)? edgePixH:sliceH;
					htmlStrR += '<img src="'+imgSrcR+n+'00_'+j+'.jpg" width="'+w*pageZoom/n+'" height="'+h*pageZoom/n+'">';
				}
			}
			if (i<sliceNumH-1){
				if (htmlStrL){ htmlStrL += '<br>'; }
				if (htmlStrR){ htmlStrR += '<br>'; }
			}
		}
		return '<div class="pageL">'+htmlStrL+'</div>'+(showPageNum===2?'<div class="pageR">'+htmlStrR+'</div>':'');
	}


	/*-------------------------------------------------------------------------
	  リンク設定
	-------------------------------------------------------------------------*/
	function setLink(jq_page, page, isRight){
		if (!xml_link){ return; }

		var offset = isRight? bookW*pageZoom : 0;

		var links = $('link[page="'+page+'"]', xml_link).last().find('item');
		putLink(links, offset, jq_page);
	}

	function putLink(links, offset, jq_page){
		for (var i=0; i<links.length; i++){
			var l = $(links[i]);
			var newDiv = $('<div class="linkArea"></div>');
			newDiv
				.css('top', parseInt(l.attr('y'))*pageZoom+'px')
				.css('left', (offset+parseInt(l.attr('x'))*pageZoom)+'px')
				.css('width', parseInt(l.attr('w'))*pageZoom+'px')
				.css('height', parseInt(l.attr('h'))*pageZoom+'px');
			if (l.attr('adress')){
				newDiv.attr('data-adress', l.attr('adress'));
			} else {
				newDiv.attr('data-orderNo', l.attr('orderNo'));
			}
			jq_page.append(newDiv);
		}
	}


	/*-------------------------------------------------------------------------
	  エリアナビ
	-------------------------------------------------------------------------*/
	var jq_areaNavi = $('#AreaNavi');

	function showAreaNavi(){
		var areaW = windowW - ($('body').hasClass('openMenu')?$('#MenuArea').width():0);
		var areaH = windowH - $('#BtmArea').height();
		var imgW = bookW*showPageNum*pageZoom*curZoom;
		var imgH = bookH*pageZoom*curZoom;
		var offsetL = $('#SliderArea li').eq(1).offset().left - ($('body').hasClass('openMenu')?$('#MenuArea').width():0);
		var offsetT = $('#SliderArea li').eq(1).offset().top;
		var x = parseInt($('#SliderArea .pageArea').eq(1).css('left'));
		var y = parseInt($('#SliderArea .pageArea').eq(1).css('top'));
		setAreaNavi(-1*(x+offsetL)*95*showPageNum/imgW, -1*(y+offsetT)*AreaNaviHeight/imgH, areaW*95*showPageNum/imgW, areaH*AreaNaviHeight/imgH);
		jq_areaNavi.show();
	}

	function setAreaNavi(l, t, w, h){
		jq_areaNavi.find('.bgT').css({
			bottom: (AreaNaviHeight-t)+'px'
		});
		jq_areaNavi.find('.bgL').css({
			top: t+'px',
			right: (95*showPageNum-l)+'px',
			bottom: (AreaNaviHeight-t-h)+'px'
		});
		jq_areaNavi.find('.bgR').css({
			top: t+'px',
			left: (l+w)+'px',
			bottom: (AreaNaviHeight-t-h)+'px'
		});
		jq_areaNavi.find('.bgB').css({
			top: (t+h)+'px'
		});
		jq_areaNavi.find('.area').css({
			top: t+'px',
			left: l+'px',
			width: w+'px',
			height: h+'px'
		});
	}

	//表示位置移動
	jq_areaNavi.on(startEvent, function(e){
		e.preventDefault();
		var initX = parseInt(jq_areaNavi.css('left'));
		var initY = parseInt(jq_areaNavi.css('top'));
		var touchX = getPageX(e);
		var touchY = getPageY(e);
		$(document).on(moveEvent, function(e){
			e.preventDefault();
			var moveX = getPageX(e);
			var moveY = getPageY(e);
			jq_areaNavi.css({
				left: Math.max(0, Math.min(windowW-jq_areaNavi.outerWidth(), initX+moveX-touchX))+'px',
				top: Math.max(0, Math.min(windowH-jq_areaNavi.outerHeight(), initY+moveY-touchY))+'px'
			});
		}).on(endEvent, function(){
			$(document).off(moveEvent).off(endEvent);
		});
	});

	//エリア移動
	jq_areaNavi.find('.area').on(startEvent, function(e){
		e.stopPropagation();
		e.preventDefault();
		var offsetL = $('#SliderArea li').eq(1).offset().left - ($('body').hasClass('openMenu')?$('#MenuArea').width():0);
		var offsetT = $('#SliderArea li').eq(1).offset().top;
		var initX = parseInt($(this).css('left'));
		var initY = parseInt($(this).css('top'));
		var width = parseInt($(this).css('width'));
		var height = parseInt($(this).css('height'));
		var touchX = getPageX(e);
		var touchY = getPageY(e);
		var jq_pageArea = $('#SliderArea .pageArea').eq(1);
		$(document).on(moveEvent, function(e){
			e.preventDefault();
			var moveX = getPageX(e);
			var moveY = getPageY(e);
			var newX = Math.max(-20, Math.min(95*showPageNum-width+20, initX+moveX-touchX));
			var newY = Math.max(-20, Math.min(AreaNaviHeight-height+20, initY+moveY-touchY));
			setAreaNavi(newX, newY, width, height);
			jq_pageArea.css({
				left: (-1*newX*bookW*pageZoom*curZoom/95-offsetL)+'px',
				top: (-1*newY*bookH*pageZoom*curZoom/AreaNaviHeight-offsetT)+'px'
			});
		}).on(endEvent, function(){
			$(document).off(moveEvent).off(endEvent);
		});
	});

	//開閉
	jq_areaNavi.find('.toggleBtn').on('click', function(){
		jq_areaNavi.toggleClass('close');
	});


	/*-------------------------------------------------------------------------
	  タッチイベント
	-------------------------------------------------------------------------*/
	var scrollX, scrollY;
	var pinchCancel=false; //ピンチ処理キャンセル
	var clickTimer=null;   //ダブルクリック判定用タイマー保持
	var touchNum=0;        //タッチした指の数
	var isSwipe=false;     //スワイプ中
	var isPinch=false;     //ピンチ中
	var pinchVal;          //ピンチ時の指の間隔

	$('#SliderArea').on(startEvent, function(e){
		if (e.button===1 || e.button===2){ return; }
		e.preventDefault();
		var touchX, touchY;  //タッチ位置
		var tapLink;         //リンク

		pinchCancel = false;
		if (isSwipe || sliderMove){ return; }

		if ($('body').hasClass('autoMode')){
			$('body').removeClass('autoMode');
			clearTimeout(autoTimer);
			setTimeout(function(){
				setSize(true);
			},500);
			return;
		}

		if ($(e.target).hasClass('linkArea')){
			tapLink = e.target;
		} else {
			tapLink = null;
		}

		if (window.event && event.touches) {
			var t=event.touches;
			if (!isSwipe && t.length>=2 && touchNum>0){
				pinchVal = Math.sqrt(Math.pow(t[1].pageX-t[0].pageX, 2) + Math.pow(t[1].pageY-t[0].pageY, 2));
				isPinch = true;
				touchNum++;
			} else {
				touchX = t[0].pageX;
				touchY = t[0].pageY;
				isPinch = false;
				touchNum = 1;
			}
		} else {
			touchX = e.pageX;
			touchY = e.pageY;
			isPinch = false;
		}

		var moveX = null;
		var moveY = null;
		var moveFlg = false;

		scrollX = parseInt($('#SliderArea .pageArea').eq(1).css('left'));
		scrollY = parseInt($('#SliderArea .pageArea').eq(1).css('top'));

		var areaW = windowW - ($('body').hasClass('openMenu')?$('#MenuArea').width():0);
		var areaH = windowH - $('#BtmArea').height();
		var offsetL = $('#SliderArea li').eq(1).offset().left - ($('body').hasClass('openMenu')?$('#MenuArea').width():0);
		var offsetT = $('#SliderArea li').eq(1).offset().top;
		var moveEnable = false;
		setTimeout(function(){
			moveEnable = true;
		},100);

		$(document).on(moveEvent, function(e){
			e.preventDefault();
			if (!moveEnable){ return; }
			if (window.event && event.touches) {
				var t=event.touches;
				if (isPinch && !isSwipe && t.length>=2){
					var newPinchVal;
					var pinchX = (t[0].pageX + t[1].pageX)/2;
					var pinchY = (t[0].pageY + t[1].pageY)/2;
					newPinchVal = Math.sqrt(Math.pow(t[1].pageX-t[0].pageX, 2) + Math.pow(t[1].pageY-t[0].pageY, 2));
					zoomIn(curZoom*(newPinchVal/pinchVal), pinchX, pinchY);
					pinchVal = newPinchVal;
				} else {
					moveX = t[0].pageX;
					moveY = t[0].pageY;
				}
			} else {
				moveX = e.pageX;
				moveY = e.pageY;
			}

			if (touchX !== moveX || touchY !== moveY){
				moveFlg = true;
			} else {
				return;
			}
			
			if (isPinch){
				return;
			} else if (curZoom===initZoom){
				//全体表示の場合：スワイプ
				if (turnPageType===0 || showPageNum===1){
					$('#SliderArea ul').css('left', -1*(viewW+borderW)+moveX-touchX+'px');
				}
				if (touchX !== moveX || touchY !== moveY){ isSwipe = true; }
			} else {
				//拡大表示の場合：ドラッグ
				var imgW = bookW*showPageNum*pageZoom*curZoom;
				var imgH = bookH*pageZoom*curZoom;
				var newX = Math.max(-1*imgW+viewW/2, Math.min(viewW/2, scrollX+moveX-touchX));
				var newY = Math.max(-1*imgH+viewH/2, Math.min(viewH/2, scrollY+moveY-touchY));

				$('#SliderArea .pageArea').eq(1).css({
					left: newX+'px',
					top: newY+'px'
				});
				setAreaNavi(-1*(newX+offsetL)*95*showPageNum/imgW, -1*(newY+offsetT)*AreaNaviHeight/imgH, areaW*95*showPageNum/imgW, areaH*AreaNaviHeight/imgH);
			}
		}).on(endEvent, function(){
			var swipeWidth = 50;
			var is3D = (turnPageType===1 && showPageNum===2);
			$(document).off(moveEvent).off(endEvent);

			touchNum = Math.max(0, touchNum-1);
			if (isPinch){ return; }

			//リンクをタップ
			if (tapLink && !moveFlg && $(tapLink).attr('data-adress')){
				jq_tooltip.hide();
				if ($(tapLink).attr('data-adress').match(/page:(.*)/)){
					var page = parseInt(RegExp.$1,10);
					$('#Loading').show();
					jumpPage(page);
					$('#Loading').hide();
				} else if ($(tapLink).attr('data-adress').match(/javascript:(.+)/)){
					var url = RegExp.$1;
					eval(url);
				} else {
					location.href = $(tapLink).attr('data-adress');
				}
				return;
			}

			if (!moveFlg){
				if (isPC || clickTimer){
					//ダブルタップ（PCシングルタップ）
					clearTimeout(clickTimer);
					clickTimer=null;
					if (isPC || curZoom<maxZoom){
						zoomIn(curZoom*(isZoomIn?zoomRatio:1/zoomRatio), touchX, touchY);
					} else {
						zoomReset();
					}
				} else {
					//シングルタップ
					clickTimer = setTimeout(function(){
						clickTimer=null;
						$('#PageSliderArea').toggle(0, function () {
							if ($(this).is(':visible')) {
								var range = ($('#PageSliderArea').width()-$('#PageSlider').width())/((showPageNum===1? totalPages-startPage:Math.ceil((totalPages+((pageStyle===3)?1:0))/2))*2-2);
								$('#PageSlider').css(opSpread, range*2*(showPageNum===1? curPage-startPage:Math.floor((curPage-startPage+1)/2))+'px');
								$('#PageBtnLeft, #PageBtnRight').toggleClass('hide', $('sideMenu', xml_contents).text()==='0');
							} else {
								$('#PageBtnLeft, #PageBtnRight').addClass('hide');
							}
						});
					}, dblClickTime);
				}
			} else 	if (isSwipe && moveX-touchX > swipeWidth && !isLeftEnd){
				//スワイプ（右）
				if (!is3D){ $('#SliderArea ul').addClass('move').css('left', 0); }
				setTimeout(function(){
					$('#SliderArea li').eq(0).before($('#SliderArea li').eq(2));
					if (is3D){
						turnPageL();
					} else {
						$('#SliderArea ul').removeClass('move').css('left', -1*(viewW+borderW)+'px');
					}
					isRightEnd = false;
					if (opSpread==='left'){
						nextPage = curPage;
						curPage = prevPage;
						loadPrevPage();
					} else {
						prevPage = curPage;
						curPage = nextPage;
						loadNextPage();
					}
					setTimeout(pageChange,turnPageTime*1000);
					isSwipe = false;
				}, is3D?0:500);
			} else if (isSwipe && touchX-moveX > swipeWidth && !isRightEnd){
				//スワイプ（左）
				if (!is3D){ $('#SliderArea ul').addClass('move').css('left', -2*(viewW+borderW)+'px'); }
				setTimeout(function(){
					$('#SliderArea li').eq(2).after($('#SliderArea li').eq(0));
					if (is3D){
						turnPageR();
					} else {
						$('#SliderArea ul').removeClass('move').css('left', -1*(viewW+borderW)+'px');
					}
					isLeftEnd = false;
					if (opSpread==='left'){
						prevPage = curPage;
						curPage = nextPage;
						loadNextPage();
					} else {
						nextPage = curPage;
						curPage = prevPage;
						loadPrevPage();
					}
					setTimeout(pageChange,turnPageTime*1000);
					isSwipe = false;
				}, is3D?0:500);
			} else if (isSwipe) {
				//スワイプキャンセル
				if (!is3D){ $('#SliderArea ul').addClass('move').css('left', -1*(viewW+borderW)+'px'); }
				setTimeout(function(){
					$('#SliderArea ul').removeClass('move');
					isSwipe = false;
				}, 500);
			} else {
			}
		});
	});


	/*-------------------------------------------------------------------------
	  拡大
	-------------------------------------------------------------------------*/
	function zoomIn(newZoom, x, y, type){
		newZoom = Math.min(newZoom, maxZoom);
		var outer = $('#SliderArea li').eq(1);
		var page = outer.find('.pageArea');
		var inner = outer.find('.pageAreaInner');

		if (!type && (pinchCancel || curZoom!==initZoom && newZoom<=initZoom)){
			$(document).off(moveEvent);
			$(document).off(endEvent);
			zoomReset();
			pinchCancel = true;
			return;
		} else if (newZoom<=initZoom){
			zoomReset();
			return;
		}

		if (isPC && !isMacSafari){
			page.css({
				width: Math.round(bookW*showPageNum*pageZoom*newZoom)+'px',
				height: Math.round(bookH*pageZoom*newZoom)+'px'
			});
			inner.css('transform', 'scale('+newZoom+')');
		} else {
			inner.css('zoom', newZoom);
		}

		inner.find('.linkArea' ).css('border-width',  1/newZoom+'px');
		inner.find('.linkLayer').css('top',          -1/newZoom+'px');
		inner.find('.linkLayer').css('left',         -1/newZoom+'px');

		if (type==='wheel' || type==='btn'){
			scrollX = parseInt($('#SliderArea .pageArea').eq(1).css('left'));
			scrollY = parseInt($('#SliderArea .pageArea').eq(1).css('top'));
		}
		if (type!=='move'){
			scrollX -= (x-outer.offset().left-scrollX)*(newZoom/curZoom-1);
			scrollY -= (y-outer.offset().top-scrollY)*(newZoom/curZoom-1);
		}

		page.css('left', scrollX+'px').css('top', scrollY+'px');

		curZoom = newZoom;

		var jq_page = $('.pageArea').eq(1);
		if (curZoom>=2 && imgSize[initImgSize+1] && jq_page.find('.mainImg.size2').html()===''){
			jq_page.find('.mainImg.size2').html(makeImgHtml(imgSize[initImgSize+1], jq_page.data('imgSrcL'), jq_page.data('imgSrcR')));
		}
		if (curZoom>=4 && imgSize[initImgSize+2] && jq_page.find('.mainImg.size3').html()===''){
			jq_page.find('.mainImg.size3').html(makeImgHtml(imgSize[initImgSize+2], jq_page.data('imgSrcL'), jq_page.data('imgSrcR')));
		}

		if (isPC){
			if (curZoom>initZoom){
				showAreaNavi();
			}
			if (curZoom===maxZoom){
				isZoomIn = false;
				$('#SliderArea').addClass('max');
				if (isIE){ $('#SliderArea').css('cursor', 'url(img/cursor_zoomout.cur), auto'); }
			} else if (curZoom===initZoom){
				isZoomIn = true;
				$('#SliderArea').removeClass('max');
				if (isIE){ $('#SliderArea').css('cursor', 'url(img/cursor_zoomin.cur), auto'); }
			}
		}
	}


	/*-------------------------------------------------------------------------
	  ハイライト表示
	-------------------------------------------------------------------------*/
	function showHighlight(){
		var params = location.search.replace('?','').split('&');
		if (!params || $('showPageItem', xml_contents).text()!=='1'){ return; }
		var color1 = $('showPageItem', xml_contents).attr('color1');
		var color2 = $('showPageItem', xml_contents).attr('color2');
		var alpha1 = $('showPageItem', xml_contents).attr('alpha1');
		var alpha2 = $('showPageItem', xml_contents).attr('alpha2');
		var isCircle = $('showPageItem', xml_contents).attr('style')==='1';
		var lineW = $('showPageItem', xml_contents).attr('size');
		lineW = (color2&&lineW)? lineW*pageZoom : 0;
		var icon = $('showPageItem', xml_contents).attr('icon')==='1';
		var areaColor = makeColorStyle(color1, alpha1);
		var borderColor = color2? makeColorStyle(color2, alpha2) : '';
		var p = {};
		for (var i=0; i<params.length; i++){
			p[params[i].split('=')[0]] = params[i].split('=')[1];
		}
		var num = ['','2','3','4','5'];
		for (i=0; i<num.length; i++){
			makeHighlight(p['x'+num[i]], p['y'+num[i]], p['w'+num[i]], p['h'+num[i]]);
		}

		function makeHighlight(x, y, w, h){
			if (!x || !y || !w || !h){ return; }
			var $canvas = $('<div class="area"><canvas width="'+Math.ceil(w*pageZoom)+'" height="'+Math.ceil(h*pageZoom)+'"></canvas></div>');
			if (icon){ $canvas.addClass('hasIcon'); }
			if (isCircle){ $canvas.addClass('circle'); }
			$canvas.css({
				left: x*pageZoom+'px',
				top: y*pageZoom+'px'
			});
			$('.pageArea').eq(1).find('.highlight').append($canvas);
			var c = $canvas.find('canvas').get(0).getContext('2d');
			w = w*pageZoom;
			h = h*pageZoom;
			c.beginPath();
			c.save();
			if (isCircle){
				c.translate(w/2,h/2);
				c.scale(1,Math.abs((h-lineW)/(w-lineW)));
				c.arc(0, 0, w/2-lineW/2, 0, 2*Math.PI);
			} else {
				c.rect(lineW/2,lineW/2,w-lineW,h-lineW);
			}
			c.restore();
			if (lineW){
				c.strokeStyle = borderColor;
				c.lineWidth = lineW;
				c.stroke();
			}
			c.fillStyle = areaColor;
			c.fill();
		}
	}


	/*-------------------------------------------------------------------------
	  ヘッダー
	-------------------------------------------------------------------------*/

	//シェアボタン
	$('#ShareBtn').on('click', function(){
		shareLinkChange();
		$('#ShareDialog').fadeIn(300);
	});
	// シェアボタンリンク再作成
	function shareLinkChange(){
		var url = location.href;
		url = url.replace('sp.html', 'index.html');
		
		if (url.indexOf('directPage')!=-1){
			url = url.replace(/directPage=-?\d*/, 'directPage='+(Math.max(0, curPage)+nombre));
		} else if (url.indexOf('?')!=-1){
			url += '&directPage='+(Math.max(0, curPage)+nombre);
		} else {
			url += '?directPage='+(Math.max(0, curPage)+nombre);
		}
		url = url.replace(/:/g, '%3a')
				.replace(/\//g, '%2f')
				.replace(/\./g, '%2e')
				.replace(/\?/g, '%3f')
				.replace(/=/g, '%3d')
				.replace(/&/g, '%26');
		$('#ShareFacebook a').attr('href', 'http://www.facebook.com/sharer.php?u='+url);
		$('#ShareTwitter a').attr('href', 'https://twitter.com/share?url='+url);
		$('#ShareMail a').attr('href', 'mailto:?body='+url);
	}

	//印刷
	$('#PrintBtn').on('click', function(){
		if (showPageNum===1){
			$('#PrintDialog .btnArea.print').show();
			$('#PrintDialog .pageSelect').hide();
		} else {
			$('#PrintDialog .btnArea.print').hide();
			$('#PrintDialog .pageSelect').show();
			$('#PrintDialog .pageSelect li').eq(1).toggleClass('disabled', !$('.pageArea').eq(1).data('imgSrcL'));
			$('#PrintDialog .pageSelect li').eq(2).toggleClass('disabled', !$('.pageArea').eq(1).data('imgSrcR'));
		}
		$('#PrintDialog').fadeIn(300);
	});

	$('#PrintDialog .pageSelect li').on('click', function(){
		if ($(this).hasClass('disabled')){ return; }
		var imgSrcL = $('.pageArea').eq(1).data('imgSrcL');
		var imgSrcR = $('.pageArea').eq(1).data('imgSrcR');
		execPrint(imgSrcL, imgSrcR, ['both', 'left', 'right'][$(this).index()]);
	});

	$('#PrintDialog .btnArea.print .btn').on('click', function(){
		execPrint($('.pageArea').eq(1).data('imgSrcL'), null, 'left');
	});

	function execPrint(imgSrcL, imgSrcR, type){
		var _pageZoom = pageZoom;
		$('#PrintArea').addClass('single').find('.page01, .page02').hide();
		pageZoom = 700/bookW;
		if (type==='both'){
			if ($('printOut', xml_contents).attr('style')==='1'){
				makePrintPage($('#PrintArea .page01'), curPage, imgSrcL, null, 1);
				makePrintPage($('#PrintArea .page02'), curPage+1, null, imgSrcR, 1);
			} else {
				$('#PrintArea').removeClass('single');
				pageZoom = 1000/(bookW*2);
				makePrintPage($('#PrintArea .page01'), curPage, imgSrcL, imgSrcR, 2);
			}
		} else {
			if (type==='right'){
				makePrintPage($('#PrintArea .page01'), curPage+1, null, imgSrcR, 1);
			} else {
				makePrintPage($('#PrintArea .page01'), curPage, imgSrcL, null, 1);
			}
		}
		pageZoom = _pageZoom;
		$('#Loading').show();
		loadCheck();
		function loadCheck(){
			if ($('#PrintArea img').toArray().every(function(cur){ return cur.complete; })){
				$('#Loading').hide();
				window.print();
			} else {
				setTimeout(loadCheck, 500);
			}
		}
	}

	function makePrintPage($area, page, imgSrcL, imgSrcR, showPage){
		var _showPageNum = showPageNum;
		showPageNum = showPage;
		$area.show().css({
			width: bookW*showPageNum*pageZoom+2+'px',
			height: bookH*pageZoom+2+'px'
		});
		$area.find('canvas')
			.attr('width', bookW*showPageNum*canvasZoom)
			.attr('height', bookH*canvasZoom);
		if ($('#PrintDialog input').prop('checked')){
			drowPen($area.find('canvas').get(0).getContext('2d'), page);
			setPageTag($area, page, true);
			$('.pageArea').eq(1).find('.tag').not('.close').each(function(){
				$area.find('.tag[data-index="'+$(this).attr('data-index')+'"]').removeClass('close');
			});
		} else {
			clearCanvas($area.find('canvas').get(0).getContext('2d'));
			$area.find('.tagLayer').html('');
		}
		showPageNum = _showPageNum;
		$area.find('.mainImg').html(makeImgHtml($('printOut', xml_contents).attr('scale'), imgSrcL, imgSrcR));
	}

	//PDF
	$('#PdfBtn').on('click', function(){
		if (showPageNum===1){
			openPdf(curPage+nombre);
		} else {
			$('#PdfDialog .pageSelect li').eq(0).toggleClass('disabled', !$('.pageArea').eq(1).data('imgSrcL') || !$('.pageArea').eq(1).data('imgSrcR'));
			$('#PdfDialog .pageSelect li').eq(1).toggleClass('disabled', !$('.pageArea').eq(1).data('imgSrcL'));
			$('#PdfDialog .pageSelect li').eq(2).toggleClass('disabled', !$('.pageArea').eq(1).data('imgSrcR'));
			$('#PdfDialog').fadeIn(300);
		}
	});

	$('#PdfDialog .pageSelect li').on('click', function(){
		if ($(this).hasClass('disabled')){ return; }
		if ($(this).hasClass('both')){
			openPdf(curPage+nombre, true);
		} else if ($(this).hasClass(opSpread)){
			openPdf(curPage+nombre);
		} else {
			openPdf(curPage+nombre+1);
		}
	});

	function openPdf(page, isBoth){
		if ($('pdf', xml_contents).attr('js')==='1'){
			if (isBoth){
				open_pdf_both(page);
			} else {
				open_pdf(page);
			}
		} else if (pdfStyle==='4' && $('pdf', xml_contents).attr('adress')){
			window.open('_blank', $('pdf', xml_contents).attr('adress'));
		} else {
			window.open('index/pdf'+(isBoth?'_both':'')+'/'+page+'.pdf', '_blank');
		}
	}

	//設定
	$('#SettingBtn').on('click', function(){
		$('#SettingDialog').fadeIn(300);
	});

	$('#SettingDialog .radioList').eq(0).find('input').on('change', function(){
		wheelType = $(this).closest('li').index();
		if (localStorage){
			localStorage.setItem(catalogName+'_wheelType', wheelType);
		}
	});

	$('#SettingDialog .radioList').eq(1).find('input').on('change', function(){
		moveType = $(this).closest('li').index();
		if (localStorage){
			localStorage.setItem(catalogName+'_moveType', moveType);
		}
	});

	if (localStorage && localStorage.getItem(catalogName+'_wheelType')){
		wheelType = parseInt(localStorage.getItem(catalogName+'_wheelType'));
	} else {
		wheelType = 0;
	}
	$('#SettingDialog .radioList:eq(0) li').eq(wheelType).find('input').prop('checked', true);

	if (localStorage && localStorage.getItem(catalogName+'_moveType')){
		moveType = parseInt(localStorage.getItem(catalogName+'_moveType'));
	} else {
		moveType = 0;
	}
	$('#SettingDialog .radioList:eq(1) li').eq(moveType).find('input').prop('checked', true);

	//マウスホイール
	$('#SliderArea').mousewheel(function(e, delta){
		if (wheelType===0){
			if (delta<0){
				zoomIn(curZoom/zoomRatio, e.pageX, e.pageY, 'wheel');
			} else {
				zoomIn(curZoom*zoomRatio, e.pageX, e.pageY, 'wheel');
			}
		} else if (wheelType===1){
			if (curZoom>initZoom){
				scrollY = Math.max(-1*bookH*pageZoom*curZoom+viewH/2, Math.min(viewH/2, scrollY+(delta<0?-80:80)));
				$('#SliderArea .pageArea').eq(1).css('top', scrollY+'px');
			}
		} else if (wheelType===2){
			if (delta<0){
				moveRight();
			} else {
				moveLeft();
			}
		}
	});

	//ヘルプ
	$('#HelpBtn').on('click', function(){
		if ($('help', xml_contents).text()==='2'){
			if($('help', xml_contents).attr('adress').match('javascript')){
				eval($('help', xml_contents).attr('adress'));
			}else{
				window.open($('help', xml_contents).attr('adress'), '_blank');
			}
		} else {
			$('#HelpDialog').fadeIn(300);
		}
	});

	//閉じる
	$('#CloseBtn').on('click', function(){
		window.close();
	});

	//スマホ・メニュー開閉
	$('#SpMenuBtn').on('click', function(e){
		e.stopPropagation();
		closePenTool();
		$(this).toggleClass('close');
		$('#BtnList .spScroll').toggleClass('show');
	});
	$('body').on('click', function(){
		$('#SpMenuBtn').removeClass('close');
		$('#BtnList .spScroll').removeClass('show');
	});


	/*-------------------------------------------------------------------------
	  メニュー
	-------------------------------------------------------------------------*/
	$('#MenuList li').on('click', function(){
		if ($(this).attr('id')=='CatalogBtn') return false;
		if (isMaxWidth(767)){
			closePenTool();
			$('.menuContent').hide().eq($(this).index()).show();
			$('#MenuContentArea').fadeIn(200);
		} else {
			if ($(this).hasClass('current') || $(this).hasClass('close')){
				$('body').removeClass('openMenu');
				$('#MenuList li').removeClass('current');
				setSize(true);
			} else {
				if (!$('body').hasClass('openMenu')){
					$('body').addClass('openMenu');
					setSize(true);
				}
				$(this).addClass('current').siblings().removeClass('current');
				$('.menuContent').hide().eq($(this).index()).show();
			}
		}
	});
	
	$('#MenuTagList').on('click', function(){
		makeTagList();
	});
	
	$('#SpFavorite').on('click', function(){
		closePenTool();
		$('.menuContent').hide().eq(4).show();
		$('#MenuContentArea').fadeIn(200);
	});

	$('#SpCatalogBtn').on('click', function(){
		closePenTool();
		$('.menuContent').hide().eq(5).show();
		$('#MenuContentArea').fadeIn(200);
	});
	$('.menuContent .closeBtn').on('click', menuClose);

	function menuClose(){
		$('#MenuList li').removeClass('current');
		$('#MenuContentArea').fadeOut(200);
	}


	/*-------------------------------------------------------------------------
	  もくじ
	-------------------------------------------------------------------------*/
	//もくじ生成
	function makeIndex(){
		var pageList = $('contents', xml_contents).children();
		if (pageList.length===0){
			$('#MenuIndex').css('display','none');
			return;
		}

		function makeIndexSub(ary){
			for (var i=0; i<ary.length; i++){
				if ($(ary[i]).attr('title')){
					var childPageList = $(ary[i]).children();
					htmlStr += '<li class="folder">'+
						'<div class="folderTit">'+$(ary[i]).attr('title')+'</div>'+
						'<ul>';
					makeIndexSub(childPageList);
					htmlStr += '</ul>';
				} else {
					htmlStr += listStr($(ary[i]).attr('no'), $(ary[i]).text());
				}
			}
		}

		var htmlStr='';
		makeIndexSub(pageList);
		$('#IndexList ul').html(htmlStr);
		$('#IndexList').css('font-size', $('contents', xml_contents).attr('font')+'px');

		function listStr(no, txt){
			var cla = (no==='')? ' class="midashi"':'';
			var page = (no!=='')? ' data-page="'+no+'"':'';
			txt = txt.replace(/<\/?font[\s\w\d=#"]*>/g, '');
			return '<li'+cla+page+'>'+txt+'</li>';
		}

		$('#IndexList li').on('click', function(e){
			e.stopPropagation();
			if ($(this).hasClass('folder')){
				$(this).toggleClass('open');
			}
			if ($(this).attr('data-page')!==void(0)){
				jumpPage($(this).attr('data-page'));
				if (isMaxWidth(767)){ menuClose(); }
			}
		});
	}


	/*-------------------------------------------------------------------------
	  キーワード検索
	-------------------------------------------------------------------------*/
	var searchWords = [];
	$('#SearchForm').on('submit', function(){
		$(this).find('input').blur();
		if ($(this).find('input').val()===''){
			showSearchError('キーワードを入力してください');
			searchWords = [];
			return;
		}
		var resultIndex = [];
		var input = $(this).find('input').val();
		input = input.replace(/[0-9]/g, function(c){
			return String.fromCharCode(c.charCodeAt(0) + '０'.charCodeAt(0) - '0'.charCodeAt(0));
		});
		input = input.replace(/[a-z]/g, function(c){
			return String.fromCharCode(c.charCodeAt(0) + 'Ａ'.charCodeAt(0) - 'a'.charCodeAt(0));
		});
		input = input.replace(/[A-Z]/g, function(c){
			return String.fromCharCode(c.charCodeAt(0) + 'Ａ'.charCodeAt(0) - 'A'.charCodeAt(0));
		});
		input = input.replace(/[ａ-ｚ]/g, function(c){
			return String.fromCharCode(c.charCodeAt(0) + 'Ａ'.charCodeAt(0) - 'ａ'.charCodeAt(0));
		});
		input = input.replace(/¢/g, '￠');
		input = input.replace(/£/g, '￡');
		input = input.replace(/\xa5/g, '￥');
		input = input.replace(/¦/g, '￤');
		input = input.replace(/¬/g, '￢');
		input = input.replace(/¯/g, '￣');
		input = input.replace(/ｰ/g, 'ー');
		var kanaMap = {
			'ｶﾞ': 'ガ', 'ｷﾞ': 'ギ', 'ｸﾞ': 'グ', 'ｹﾞ': 'ゲ', 'ｺﾞ': 'ゴ',
			'ｻﾞ': 'ザ', 'ｼﾞ': 'ジ', 'ｽﾞ': 'ズ', 'ｾﾞ': 'ゼ', 'ｿﾞ': 'ゾ',
			'ﾀﾞ': 'ダ', 'ﾁﾞ': 'ヂ', 'ﾂﾞ': 'ヅ', 'ﾃﾞ': 'デ', 'ﾄﾞ': 'ド',
			'ﾊﾞ': 'バ', 'ﾋﾞ': 'ビ', 'ﾌﾞ': 'ブ', 'ﾍﾞ': 'ベ', 'ﾎﾞ': 'ボ',
			'ﾊﾟ': 'パ', 'ﾋﾟ': 'ピ', 'ﾌﾟ': 'プ', 'ﾍﾟ': 'ペ', 'ﾎﾟ': 'ポ',
			'ｳﾞ': 'ヴ', 'ﾜﾞ': 'ヷ', 'ｦﾞ': 'ヺ',
			'ｱ': 'ア', 'ｲ': 'イ', 'ｳ': 'ウ', 'ｴ': 'エ', 'ｵ': 'オ',
			'ｶ': 'カ', 'ｷ': 'キ', 'ｸ': 'ク', 'ｹ': 'ケ', 'ｺ': 'コ',
			'ｻ': 'サ', 'ｼ': 'シ', 'ｽ': 'ス', 'ｾ': 'セ', 'ｿ': 'ソ',
			'ﾀ': 'タ', 'ﾁ': 'チ', 'ﾂ': 'ツ', 'ﾃ': 'テ', 'ﾄ': 'ト',
			'ﾅ': 'ナ', 'ﾆ': 'ニ', 'ﾇ': 'ヌ', 'ﾈ': 'ネ', 'ﾉ': 'ノ',
			'ﾊ': 'ハ', 'ﾋ': 'ヒ', 'ﾌ': 'フ', 'ﾍ': 'ヘ', 'ﾎ': 'ホ',
			'ﾏ': 'マ', 'ﾐ': 'ミ', 'ﾑ': 'ム', 'ﾒ': 'メ', 'ﾓ': 'モ',
			'ﾔ': 'ヤ', 'ﾕ': 'ユ', 'ﾖ': 'ヨ',
			'ﾗ': 'ラ', 'ﾘ': 'リ', 'ﾙ': 'ル', 'ﾚ': 'レ', 'ﾛ': 'ロ',
			'ﾜ': 'ワ', 'ｦ': 'ヲ', 'ﾝ': 'ン',
			'ｧ': 'ァ', 'ｨ': 'ィ', 'ｩ': 'ゥ', 'ｪ': 'ェ', 'ｫ': 'ォ',
			'ｯ': 'ッ', 'ｬ': 'ャ', 'ｭ': 'ュ', 'ｮ': 'ョ'
		};
		input = input.replace(new RegExp('(' + Object.keys(kanaMap).join('|') + ')', 'g'), function(c){
			return kanaMap[c];
		});
		input = input.replace(/[!#$%&\(\)\+,\-\.=@\[\]^_{}~'\*\/:;<>?\\`|｡｢｣､･、。，．・：；？！―‐／＼～∥｜…‥‘’“”（）〔〕［］｛｝〈〉《》「」『』【】─│┌┐┘└├┬┤┴┼━┃┏┓┛┗┣┳┫┻╋┠┯┨┷┿┝┰┥┸╂㌍〝〟＇＂]/g, '');
		searchWords = input.replace(/　/g,' ').split(' ');
		searchWords = searchWords.filter(function(d){ return d!=='' && d.search(/[んゃゅょっぁぃぅぇぉンャュョッァィゥェォー]/)!==0; });
		if (searchWords.length===0){
			showSearchError('該当のページは見つかりませんでした。');
			return;
		}
		var searchWordsReg = searchWords.map(function(s){ return new RegExp(s); });
		var checkWord = function(ele){
			return ele.test(searchData[i].text);
		};
		for (var i=0; i<searchData.length; i++){
			if (($.inArray(i,hidePages)===-1) && searchWordsReg.every(checkWord)){
				resultIndex.push(i);
			}
		}
		if (resultIndex.length===0){
			showSearchError('該当のページは見つかりませんでした。');
			return;
		}
		var htmlStr = '';
		for (i=0; i<resultIndex.length; i++){
			var d = searchData[resultIndex[i]];
			htmlStr += '<li data-page="'+d.page+'">'+d.title+'</li>';
		}

		$('#SearchList ul').show().html(htmlStr);
		$('#SearchMessage').hide();
		//iOS スクロール不具合対策
		$('#SearchArea').hide();
		setTimeout(function(){
			$('#SearchArea').show();
		},10);
		//--
		return false;
	});

	function showSearchError(msg){
		$('#SearchMessage').html(msg).show();
		$('#SearchList ul').hide();
	}

	//ページ移動
	var isKeywordSearch = false;
	$('#SearchList').on('click', 'li', function(){
		isKeywordSearch = true;
		jumpPage($(this).attr('data-page'), true);
		if (isMaxWidth(767)){ menuClose(); }
	});


	/*-------------------------------------------------------------------------
	  付箋リスト
	-------------------------------------------------------------------------*/
	function makeTagList(){
		var htmlStr='';
		for (var i=tagData.length-1; i>=0; i--){
			var d = tagData[i];
			
			var page = d.page-(pageStyle!==5&&(opSpread==='right'&&d.x>bookW||opSpread==='left'&&d.x<bookW)?1:0);
			var tagText = d.txt.replace(/</g,'&lt;').replace(/>/g,'&gt;');
			htmlStr +=
				'<li class="color'+d.color+'" data-index="'+i+'" data-page="'+page+'">'+
				'<p class="text">'+tagText+'</p>';
			if (Object.keys(nombreData).length > 0){
				if (page < startPage ){
					if (isFinite(nombreData[page+1])){
						htmlStr += '<div class="page">P.'+(nombreData[page+1])+'</div>';
					} else {
						htmlStr += '<div class="page">'+(nombreData[page+1])+'</div>';
					}
				} else if (page < totalPages){
					if (isFinite(nombreData[page])){
						htmlStr += '<div class="page">P.'+(nombreData[page])+'</div>';
					} else {
						htmlStr += '<div class="page">'+(nombreData[page])+'</div>';
					}
				} else {
					if (isFinite(nombreData[page-1])){
						htmlStr += '<div class="page">P.'+(nombreData[page-1])+'</div>';
					} else {
						htmlStr += '<div class="page">'+(nombreData[page-1])+'</div>';
					}
				}
			} else {
				htmlStr += '<div class="page">P.'+(page+nombre)+'</div>';
			}
			htmlStr += '</li>';
		}
		$('#TagList > ul').html(htmlStr);
	}

	//すべて削除
	$('#TagList .deleteAll').on('click', function(){
		if (tagData.length===0){ return; }
		$('#TagDeleteAll').show();
		if (!isMaxWidth(767)){
			$('#TagDeleteAll .window').css({
				left: $(this).offset().left-20+'px',
				top: $(this).offset().top-5+'px'
			});
		}
	});

	if (isPC){
		$('#TagDeleteAll .window').on({
			mouseenter: function(){
				clearTimeout(windowHideTimer);
			},
			mouseleave: function(){
				windowHideTimer = setTimeout(function(){
					$('#TagDeleteAll').hide();
				}, 500);
			}
		});
	}

	$('#TagDeleteAll .cmnBtn').on('click', function(){
		$('#TagDeleteAll').hide();
	});

	$('#TagDeleteAll .enter').on('click', function(){
		tagData = [];
		$('.pageArea .tagLayer .tag').remove();
		makeTagList();
		saveTagData();
	});

	//詳細を見る
	$('#TagList').on('click', 'li', function(){
		var page = parseInt($(this).attr('data-page'));
		if (page!==curPage && (showPageNum===1 || getPageGroup(page)!==getPageGroup(curPage))){
			jumpPage(page);
		}
		if (isMaxWidth(767)){ menuClose(); }
	});


	/*-------------------------------------------------------------------------
	  ビジュアルメニュー
	-------------------------------------------------------------------------*/
	var showVisualMenuNum = 0;
	var jq_visualMenu = $('#VisualMenu');
	var jq_visualMenuList;

	function makeVisualMenu(){
		var htmlStr = '';
		for (var i=(pageStyle===3?-1:0); i<totalPages; i+=(pageStyle===5?1:2)){
			if ($.inArray(i,hidePages)!==-1 && (pageStyle===5 || $.inArray(i+1,hidePages)!==-1)){ continue; }
			var imgSrc01 = imgPrefix+'/'+addZero(i,4)+'/tmb.jpg';
			var imgSrc02 = imgPrefix+'/'+addZero(i+1,4)+'/tmb.jpg';
			var page = [];
			if (Object.keys(nombreData).length>0 && i>=0){
				page.push(nombreData[i]);
			} else if(i+nombre>0){
				page.push(i+nombre);
			}
			if (pageStyle!==5 && i+1>=0 && i+1<totalPages){
				if (Object.keys(nombreData).length > 0){
					page.push(nombreData[i+1]);
				} else {
					page.push(i+1+nombre); 
				}
			}
			htmlStr +=
				'<li>'+
				'<div class="img" data-page="'+i+'">'+
				($.inArray(i,hidePages)===-1 && i>=0?'<img class="img01" data-src="'+imgSrc01+'" alt="">':'')+
				(pageStyle!==5 && $.inArray(i+1,hidePages)===-1 && i+1<totalPages?'<img class="img02" data-src="'+imgSrc02+'" alt="">':'')+
				'</div>';
			if (Object.keys(nombreData).length > 0){
				if (!isFinite(page[0]) && !isFinite(page[1])){
					htmlStr += '<div class="page">'+(page.length>0?page.join('-'):'')+'</div>';
				} else if(!isFinite(page[0]) && isFinite(page[1])){
					htmlStr += '<div class="page">'+(page.length>0?page.join('-p.'):'')+'</div>';
				} else {
					htmlStr += '<div class="page">'+(page.length>0?'p.'+page.join('-'):'')+'</div>';
				}
			} else {
				htmlStr += '<div class="page">'+(page.length>0?'p.'+page.join('-'):'')+'</div>';
			}
			htmlStr += '</li>';
		}
		$('#VisualMenu ul').html(htmlStr);
		$('#VisualMenu .img').css('padding-top', (pageStyle!==5?bookH/bookW/2:bookH/bookW*0.6)*100+'%');
		jq_visualMenuList = $('#VisualMenu li');
		scrollVisualMenu();
	}

	jq_visualMenu.on('scroll', scrollVisualMenu);

	function scrollVisualMenu(){
		while(showVisualMenuNum<jq_visualMenuList.length){
			var jq_item = jq_visualMenuList.eq(showVisualMenuNum);
			if (showVisualMenuNum<10 || jq_visualMenu.is(':visible') && jq_item.offset().top<windowH){
				jq_item.find('img').each(function(){
					$(this).attr('src', $(this).attr('data-src'));
				});
				showVisualMenuNum++;
			} else {
				break;
			}
		}
	}

	$('#VisualMenu').on('click', '.img', function(){
		jumpPage($(this).attr('data-page'));
		if (isMaxWidth(767)){ menuClose(); }
	});

	/*-------------------------------------------------------------------------
	  カタログメニュー
	-------------------------------------------------------------------------*/
	var showCatalogMenuNum = 0;
	var jq_catalogMenu = $('#CatalogMenu');
	var jq_catalogMenuList;

	function makeCatalogMenu(){
		if (!catalog_Menu){ return; }
		var imgWidth = $(catalog_Menu).children().attr("imgWidth");
		var imgHeight = $(catalog_Menu).children().attr("imgHeight");
		$(catalog_Menu).find('item').each(function(){
			var htmlStr = '<li>';
			htmlStr += '<a href="'+ $(this).attr('adress') +'"><div class="img" data-page="'+ $(this).attr('adress') +'">';
			htmlStr += '<img class="img01" data-src="'+$(this).attr('src') +'" alt="">';
			htmlStr += '</div></a>';
			htmlStr += '<div class="catalogname">'+ $(this).attr('title') +'</div>';
			htmlStr += '</li>';
			$('#CatalogMenu ul').append(htmlStr);
		});
		$('#CatalogMenu .img').css('height', imgHeight+'px');
		$('#CatalogMenu .img').css('width',imgWidth+'px');
		$('#CatalogMenu ul').addClass('single');
		jq_catalogMenuList = $('#CatalogMenu li');
		scrollCatalogMenu();
	}

	jq_catalogMenu.on('scroll', scrollCatalogMenu);

	function scrollCatalogMenu(){
		while(showCatalogMenuNum<jq_catalogMenuList.length){
			var jq_item = jq_catalogMenuList.eq(showCatalogMenuNum);
			if (showCatalogMenuNum<10 || jq_catalogMenu.is(':visible') && jq_item.offset().top<windowH){
				jq_item.find('img').each(function(){
					$(this).attr('src', $(this).attr('data-src'));
				});
				showCatalogMenuNum++;
			} else {
				break;
			}
		}
	}

	/*-------------------------------------------------------------------------
	  お気に入りページ
	-------------------------------------------------------------------------*/

	function makeFavoriteList(){
		var htmlStr = '';
		for (var i=favoriteList.length-1; i>=0; i--){
			var imgNum = 1;
			var page = [];
			htmlStr +=
				'<li>'+
				'<div class="img" data-page="'+favoriteList[i]+'">';
			for (var j=0; j<totalPages; j++){
				if (getPageGroup(j)===favoriteList[i]){
					var imgSrc = imgPrefix+'/'+addZero(j,4)+'/tmb.jpg';
					if ($.inArray(i,hidePages)===-1 && j===0 && pageStyle===3){
						htmlStr += '<img class="img0'+(imgNum+1)+'" src="'+imgSrc+'" alt="">';
					} else {
						htmlStr += '<img class="img0'+imgNum+'" src="'+imgSrc+'" alt="">';
					}
					imgNum++;
					if (Object.keys(nombreData).length>0 && j>=0){
						page.push(nombreData[j]);
					} else if (j+nombre>0){
						page.push(j+nombre);
					}
				}
			}
			htmlStr +='</div>';
			if (Object.keys(nombreData).length > 0){
				if (!isFinite(page[0]) && !isFinite(page[1])){
					htmlStr += '<div class="page">'+(page.length>0?page.join('-'):'')+'</div>';
				} else if(!isFinite(page[0]) && isFinite(page[1])){
					htmlStr += '<div class="page">'+(page.length>0?page.join('-p-'):'')+'</div>';
				} else {
					htmlStr += '<div class="page">'+(page.length>0?'p.'+page.join('-'):'')+'</div>';
				}
			} else {
				htmlStr += '<div class="page">'+(page.length>0?'p.'+page.join('-'):'')+'</div>';
			}
			htmlStr += '<div class="deleteBtn cmnBtn">削除</div></li>';
		}
		$('#FavoriteList ul').html(htmlStr);
		$('#FavoriteList .img').css('padding-top', bookH/bookW/2*100+'%');
	}

	$('#FavoriteList').on('click', '.img', function(){
		jumpPage($(this).attr('data-page'));
		if (isMaxWidth(767)){ menuClose(); }
	});

	//削除
	$('#FavoriteList').on('click', '.deleteBtn', function(){
		favoriteList.splice(favoriteList.length-1-$(this).closest('li').index(), 1);
		saveFavoriteData();
		makeFavoriteList();
	});

	//すべて削除
	$('#FavoriteList .deleteAll').on('click', function(){
		if (favoriteList.length===0){ return; }
		$('#FavoriteDeleteAll').show();
		if (!isMaxWidth(767)){
			$('#FavoriteDeleteAll .window').css({
				left: $(this).offset().left-20+'px',
				top: $(this).offset().top-5+'px'
			});
		}
	});

	if (isPC){
		$('#FavoriteDeleteAll .window').on({
			mouseenter: function(){
				clearTimeout(windowHideTimer);
			},
			mouseleave: function(){
				windowHideTimer = setTimeout(function(){
					$('#FavoriteDeleteAll').hide();
				}, 500);
			}
		});
	}

	$('#FavoriteDeleteAll .cmnBtn').on('click', function(){
		$('#FavoriteDeleteAll').hide();
	});

	$('#FavoriteDeleteAll .enter').on('click', function(){
		favoriteList = [];
		saveFavoriteData();
		$('#FavoriteList ul').html('');
	});


	/*-------------------------------------------------------------------------
	  ページ移動ボタン
	-------------------------------------------------------------------------*/

	function moveLeft(){
		if (isLeftEnd || $('#SliderArea ul').hasClass('move') || $('#SliderArea li.turn').length>0){ return; }
		var zoom = curZoom;
		var moveTime = 0;
		var is3D = (turnPageType===1 && showPageNum===2);
		scrollX = parseInt($('#SliderArea .pageArea').eq(1).css('left'));
		scrollY = parseInt($('#SliderArea .pageArea').eq(1).css('top'));
		if (moveType===0 || curZoom===initZoom){
			if (!is3D){
				$('#SliderArea ul').addClass('move');
				moveTime = 500;
			}
		}
		zoomReset();
		if (!is3D){ $('#SliderArea ul').css('left', 0); }
		setTimeout(function(){
			$('#SliderArea li').eq(0).before($('#SliderArea li').eq(2));
			if (!is3D){
				$('#SliderArea ul').removeClass('move').css('left', -1*(viewW+borderW)+'px');
			} else if (moveType===0 || zoom===initZoom){
				turnPageL();
			}
			if (moveType===1){ zoomIn(zoom, 0, 0, 'move'); }
			isRightEnd = false;
			if (opSpread==='left'){
				nextPage = curPage;
				curPage = prevPage;
				loadPrevPage();
			} else {
				prevPage = curPage;
				curPage = nextPage;
				loadNextPage();
			}
			setTimeout(pageChange,turnPageTime*1000);
		}, moveTime);
	}

	function turnPageL(){
		$('#SliderArea li').eq(2).addClass('turn L');
		$('#SliderArea li').eq(1).addClass('turn nextL');
		$('#SliderArea li').eq(2).find('.mainImg .pageL').on('animationend', function(){
			$('#SliderArea li').eq(1).addClass('move');
		});
		$('#SliderArea li').eq(1).find('.mainImg .pageR').on('animationend', function(){
			$('#SliderArea li').removeClass('turn L nextL move');
			$('#SliderArea').find('.pageL, .pageR').off('animationend');
		});
	}

	function moveRight(){
		if (isRightEnd || $('#SliderArea ul').hasClass('move') || $('#SliderArea li.turn').length>0){ return; }
		var zoom = curZoom;
		var moveTime = 0;
		var is3D = (turnPageType===1 && showPageNum===2);
		scrollX = parseInt($('#SliderArea .pageArea').eq(1).css('left'));
		scrollY = parseInt($('#SliderArea .pageArea').eq(1).css('top'));
		if (moveType===0 || curZoom===initZoom){
			if (!is3D){
				$('#SliderArea ul').addClass('move');
				moveTime = 500;
			}
		}
		zoomReset();
		if (!is3D){ $('#SliderArea ul').css('left', -2*(viewW+borderW)+'px'); }
		setTimeout(function(){
			$('#SliderArea li').eq(2).after($('#SliderArea li').eq(0));
			if (!is3D){
				$('#SliderArea ul').removeClass('move').css('left', -1*(viewW+borderW)+'px');
			} else if(moveType===0 || zoom===initZoom) {
				turnPageR();
			}
			if (moveType===1){ zoomIn(zoom, 0, 0, 'move'); }
			isLeftEnd = false;
			if (opSpread==='left'){
				prevPage = curPage;
				curPage = nextPage;
				loadNextPage();
			} else {
				nextPage = curPage;
				curPage = prevPage;
				loadPrevPage();
			}
			setTimeout(pageChange,turnPageTime*1000);
		}, moveTime);
	}

	function turnPageR(){
		$('#SliderArea li').eq(0).addClass('turn R');
		$('#SliderArea li').eq(1).addClass('turn nextR');
		$('#SliderArea li').eq(0).find('.mainImg .pageR').on('animationend', function(){
			$('#SliderArea li').eq(1).addClass('move');
		});
		$('#SliderArea li').eq(1).find('.mainImg .pageL').on('animationend', function(){
			$('#SliderArea li').removeClass('turn R nextR move');
			$('#SliderArea').find('.pageL, .pageR').off('animationend');
		});
	}

	$('#PageBtnLeft, #PageBtn .left').on('click', moveLeft);
	$('#PageBtnRight, #PageBtn .right').on('click', moveRight);

	$('#PageBtn .leftEnd').on('click', function(){
		jumpPage(opSpread==='left'?0:totalPages-1);
	});

	$('#PageBtn .rightEnd').on('click', function(){
		jumpPage(opSpread==='left'?totalPages-1:0);
	});


	/*-------------------------------------------------------------------------
	  フッターエリア
	-------------------------------------------------------------------------*/
	//ホームボタン
	$('#HomeBtn,#CatalogBtn').on('click', function(){
		location.href = 'catalog';
	});

	//ズーム
	$('#ZoomInBtn').on('click', function(){
		zoomIn(curZoom*zoomRatio, windowW/2, windowH/2, 'btn');
	});
	$('#ZoomOutBtn').on('click', function(){
		zoomIn(curZoom/zoomRatio, windowW/2, windowH/2, 'btn');
	});

	//自動再生
	var autoTimer;
	var autoInterval;
	var autoReverse = false;
	$('#AutoBtn, #SpAutoBtn').on('click', function(){
		$('body').addClass('autoMode');
		$('#SpMenuBtn').removeClass('close');
		$('#BtnList .spScroll').removeClass('show');
		zoomReset();
		setSize(true);
		showMessage('画面をクリックすると<br class="sp">自動再生を終了します');
		setTimeout(function(){
			autoTimer = setTimeout(autoMove, autoInterval);
		},1500);
	});

	function autoMove(){
		if(!$('body').hasClass('autoMode')){ return; }
		if (autoReverse){
			if (isLeftEnd){
				jumpPage(totalPages-1);
			} else {
				moveLeft();
			}
		} else {
			if (isRightEnd){
				jumpPage(0);
			} else {
				moveRight();
			}
		}
		autoTimer = setTimeout(autoMove, autoInterval);
	}

	$('#AutoInterval').on('click', 'li', function(){
		autoInterval = parseInt($(this).find('span').text())*1000+500;
		$(this).addClass('current').siblings().removeClass('current');
		clearTimeout(autoTimer);
		autoTimer = setTimeout(autoMove, autoInterval);
	});

	$('#AutoDirection li').on('click', function(){
		autoReverse = $(this).index()===0;
		$(this).removeClass('current').siblings().addClass('current');
	});

	//ページジャンプ
	$('#PageJump').on('submit', function(){
		var page = parseInt($('#PageInput').val(),10)-nombre;
		if (Object.keys(nombreData).length > 0){
			for (var nbCnt = 0; nbCnt < Object.keys(nombreData).length; nbCnt++){
				if (nombreData[nbCnt] === $('#PageInput').val()){
					jumpPage(nbCnt);
					break;
				}
			}
		} else if (!isNaN(page)){
			jumpPage(page);
		}
		return false;
	});

	//戻る
	$('#BackBtn, #SpBackBtn').on('click', function(){
		if ($(this).hasClass('disabeld')){ return; }
		$('#SpMenuBtn').removeClass('close');
		$('#BtnList .spScroll').removeClass('show');
		history.pop();
		jumpPage(history.pop());
		if (history.length<2){
			$('#BackBtn, #SpBackBtn').addClass('disabled');
		}
	});

	//お気に入り
	if (localStorage && localStorage.getItem(catalogName+'_favorite')){
		favoriteList = JSON.parse(localStorage.getItem(catalogName+'_favorite'));
	} else {
		favoriteList = [];
	}

	function saveFavoriteData(){
		if (localStorage){
			localStorage.setItem(catalogName+'_favorite', JSON.stringify(favoriteList));
		}
	}

	$('#FavoriteBtn, #SpFavoriteBtn').on('click', function(){
		if ($.inArray(getPageGroup(curPage), favoriteList)===-1){
			favoriteList.push(getPageGroup(curPage));
			saveFavoriteData();
			makeFavoriteList();
			showMessage('お気に入りに追加しました');
		}
	});

	//商品購入
	$('#PurchaseBtn, #SpPurchaseBtn').on('click', function(){
		if ($(this).hasClass('disabled')){ return; }
		if($('shoppingPage', xml_contents).attr('adress').match('openPageCart')){
			eval($('shoppingPage', xml_contents).attr('adress')+(curPage+nombre)+'\')');
		}else{
			window.open($('shoppingPage', xml_contents).attr('adress'));
		}
	});

	// 共有
	$('#PageShareBtn').on('click', function(){
		var url = 'https://cecile-dev.prm.bz/share/fst/digicata/'+getUrlParam('code')+'/?directPage=' + (curPage+nombre);
		location.href=url;
	});

	//このページのURLをコピー
	$('#UrlCopyBtn button, #SpUrlCopy button').on('click', function(){
		var url = location.origin + location.pathname.replace(/[^\/]*$/, 'index.html') + '?directPage=' + (curPage+nombre);
		if (isIOS && ua.search(/OS [5-9]/)!==-1){
			$('#PageUrlDialog textarea').val(url);
			$('#PageUrlDialog').fadeIn(300);
		} else {
			if (isMaxWidth(767)){ $('#UrlCopyBtn').show(); }
			$('#UrlCopyBtn .text').show();
			if (isIOS){
				$('#UrlCopyBtn .text').html('<p>'+url+'</p>');
				var range = document.createRange();
				range.selectNodeContents($('#UrlCopyBtn p').get(0));
				window.getSelection().addRange(range);
				document.execCommand('copy');
			} else {
				$('#UrlCopyBtn .text').html('<textarea>'+url+'</textarea>');
				$('#UrlCopyBtn textarea').get(0).select();
				document.execCommand('copy');
				$('#UrlCopyBtn textarea').blur();
			}
			if (isMaxWidth(767)){
				$('#UrlCopyBtn, #UrlCopyBtn .text').hide();
				showMessage('クリップボードにコピーされました');
			} else {
				$('#UrlCopyBtn .text').html('クリップボードにコピーされました');
				$('#UrlCopyBtn .text').addClass('show');
				setTimeout(function(){
					$('#UrlCopyBtn .text').fadeOut(300, function(){
						$('#UrlCopyBtn .text').removeClass('show');
					});
				}, 1500);
			}
		}
	});


	/*-------------------------------------------------------------------------
	  付箋
	-------------------------------------------------------------------------*/
	var tagData;

	if (localStorage && localStorage.getItem(catalogName+'_sticky')){
		tagData = JSON.parse(localStorage.getItem(catalogName+'_sticky'));
	} else {
		tagData = [];
	}

	function saveTagData(){
		if (localStorage){
			localStorage.setItem(catalogName+'_sticky', JSON.stringify(tagData));
		}
	}

	function setPageTag(jq_page, page){
		var data = tagData;
		jq_page.find('.tagLayer').html('');
		for (var i=0; i<data.length; i++){
			if (data[i].page===getPageGroup(page)){
				addTag(i, showPageNum===1 && isRightPage(page));
			}
		}

		function addTag(i, isR){
			var tagObj = data[i];
			if (showPageNum===1){
				if (!isR && tagObj.x>=bookW){ return; }
				if (isR && tagObj.x<bookW){ return; }
			}
			var htmlStr =
				'<div class="tag '+'" data-index="'+i+'">'+
				'<div class="header"><p>'+tagObj.date+'</p></div>'+
				'<div class="toggleBtn"></div>'+
				'<div class="deleteBtn"></div>'+
				'<div class="text">'+
				'<textarea placeholder="ここにテキストを入力">'+tagObj.txt+'</textarea>'+
				'</div>'+
				'<div class="resizeBtn"></div>'+
				'</div>';
			var jq_tag = $(htmlStr);
			jq_tag.css({
				left: Math.round((tagObj.x-(isR?bookW:0))*pageZoom)+'px',
				top: Math.round(tagObj.y*pageZoom)+'px',
				backgroundColor: '#'+tagColorAry[tagObj.color],
				width: tagObj.w*pageZoom+'px',
				height: tagObj.h*pageZoom+'px'
			});
			jq_page.find('.tagLayer').append(jq_tag);
		}
	}

	//付箋追加
	$('#TagBtn').on('click', function(){
		if ($('.pageArea').eq(1).find('.tag').length>=tagMax){ return; }
		if ($('#TagColor').is(':visible')){
			$('#TagColor').hide();
		} else {
			$('#TagColor').show();
			if (!isMaxWidth(767)){
				$('#TagColor .window').css({
					left: Math.max(0,$(this).offset().left*(!isPC||isMacSafari?curZoom:1)-90)+'px',
					top: $(this).offset().top*(!isPC||isMacSafari?curZoom:1)-70+'px'
				});
			}
		}
	});

	$('#TagColor li').on('click', function(){
		addNewTag($(this).index());
		$('#TagColor').hide();
	});

	function addNewTag(color){
		var d = new Date();
		var day = ['SUN','MON','TUE','WED','THU','FRI','SAT'];
		var tag = {
			page: getPageGroup(curPage),
			color: color,
			x: (bookW*showPageNum-200)/2+(isRightPage(curPage)?bookW:0),
			y: (bookH-100)/2,
			w: 200,
			h: 100,
			date: d.getFullYear()+'.'+addZero(d.getMonth()+1,2)+'.'+addZero(d.getDate(),2)+'('+day[d.getDay()]+') '+addZero(d.getHours(),2)+':'+addZero(d.getMinutes(),2),
			txt: ''
		};
		tagData.push(tag);
		zoomReset();
		setPageTag($('.pageArea').eq(1), curPage);
		saveTagData();
		makeTagList();
	}

	//開閉
	$('#SliderArea .tagLayer').on('click', '.tag .toggleBtn', function(e){
		e.stopPropagation();
		$(this).closest('.tag').toggleClass('close');
	});

	//マウスオーバー
	$('#SliderArea .tagLayer').on('mouseover', '.tag', function(e){
		$(this).css('z-index', '10').siblings().css('z-index', '0');
	});

	//削除
	$('#SliderArea .tagLayer').on('click', '.tag .deleteBtn', function(e){
		e.stopPropagation();
		if ($(this).closest('.tag').hasClass('close')){ return; }
		tagData.splice($(this).closest('.tag').attr('data-index'), 1);
		$(this).closest('.tag').remove();
		saveTagData();
		makeTagList();
	});

	//テキスト変更
	$('#SliderArea .tagLayer').on('change', 'textarea', function(){
		var val = $(this).val();
		var index = $(this).closest('.tag').attr('data-index');
		tagData[index].txt = val;
		saveTagData();
		makeTagList();
	});

	//位置変更
	$('#SliderArea .tagLayer').on(startEvent, '.tag', function(e){
		e.stopPropagation();
		var jq_tag = $(this);
		var newX=null;
		var newY=null;
		var initX = parseInt(jq_tag.css('left'));
		var initY = parseInt(jq_tag.css('top'));
		var startX = getPageX(e);
		var startY = getPageY(e);
		var moveEnable = false;
		setTimeout(function(){
			moveEnable = true;
		}, 100);
		$(document).on(moveEvent, function(e){
			e.preventDefault();
			if (!moveEnable){ return; }
			newX = Math.max(0, Math.min(bookW*showPageNum*pageZoom-jq_tag.outerWidth(), initX+(getPageX(e)-startX)/curZoom));
			newY = Math.max(0, Math.min(bookH*pageZoom-jq_tag.outerHeight(), initY+(getPageY(e)-startY)/curZoom));
			jq_tag.css({
				left: newX+'px',
				top: newY+'px'
			});
		}).on(endEvent, function(){
			$(document).off(moveEvent).off(endEvent);
			if (newY!==null){
				tagData[jq_tag.attr('data-index')].x = Math.round(newX/pageZoom)+(showPageNum===1&&isRightPage(curPage)?bookW:0);
				tagData[jq_tag.attr('data-index')].y = Math.round(newY/pageZoom);
				saveTagData();
				makeTagList();
			}
		});
	});
	$('#SliderArea .tagLayer').on(startEvent, '.tag .editBtn', function(e){
		e.stopPropagation();
	});

	//リサイズ
	$('#SliderArea .tagLayer').on(startEvent, '.tag .resizeBtn', function(e){
		e.preventDefault();
		e.stopPropagation();

		var jq_tag = $(this).closest('.tag');
		var touchX = getPageX(e);
		var touchY = getPageY(e);
		var moveX = null;
		var moveY = null;
		var initW = parseInt(jq_tag.width())/pageZoom;
		var initH = parseInt(jq_tag.height())/pageZoom;

		$(document).on(moveEvent, function(e){
			e.preventDefault();
			moveX = getPageX(e);
			moveY = getPageY(e);
			var newW = Math.max(180, initW+(moveX-touchX)/pageZoom/curZoom);
			var newH = Math.max(30, initH+(moveY-touchY)/pageZoom/curZoom);
			jq_tag.css({
				width: newW*pageZoom+'px',
				height: newH*pageZoom+'px'
			});
			tagData[jq_tag.attr('data-index')].w = newW;
			tagData[jq_tag.attr('data-index')].h = newH;
		}).on(endEvent, function(){
			$(document).off(moveEvent).off(endEvent);
			saveTagData();
		});
	});


	/*-------------------------------------------------------------------------
	  ペン
	-------------------------------------------------------------------------*/
	var penData;
	var penColorAry = ['d30036', '342aff', 'e4ed00', '1a6c00', '000'];
	var penColor = 0;
	var penWidthAry = [2,8,14];
	var penWidth = 0;
	var jq_penTool = $('#PenTool');

	if (localStorage && localStorage.getItem(catalogName+'_pen')){
		penData = JSON.parse(localStorage.getItem(catalogName+'_pen'));
		penData.forEach(function(cur){
			cur.linecolor = parseInt(cur.linecolor, 10);
			cur.linesize  = parseInt(cur.linesize,  10);
			if(!Array.isArray(cur.x)){
				cur.x = cur.x.split(',').map(parseFloat);
				cur.y = cur.y.split(',').map(parseFloat);
			}
		});
	} else {
		penData = [];
	}

	function savePenData(){
		if (localStorage){
			var tempPenData = JSON.parse(JSON.stringify(penData));
			tempPenData.forEach(function(cur){
				cur.x = cur.x.join(',');
				cur.y = cur.y.join(',');
			});
			localStorage.setItem(catalogName+'_pen', JSON.stringify(tempPenData));
		}
	}

	function drowPen(c, page, jq_tag){
		var i,j,x,y;
		var pg = getPageGroup(page);
		var offset = (showPageNum===1 && isRightPage(page))? 0:bookW;
		var data = penData;
		c.lineCap = 'round';
		c.lineJoin = 'round';
		c.globalAlpha = 0.8;
		clearCanvas(c);
		for (i=0; i<data.length; i++){
			if (data[i].page!==pg){ continue; }
			c.lineWidth = penWidthAry[data[i].linesize]*canvasZoom;
			c.strokeStyle = '#'+penColorAry[data[i].linecolor];
			x = data[i].x;
			y = data[i].y;
			if (x.length<2){ continue; }
			c.beginPath();
			canvasMoveTo(c, x[0]+offset, y[0]+bookH/2);
			for (j=1; j<x.length; j++){
				canvasLineTo(c, x[j]+offset, y[j]+bookH/2);
			}
			c.stroke();
		}
		if (jq_tag){
			var isR = jq_tag.hasClass('right');
			var fromX;
			if (isR){
				fromX = (bookW*showPageNum-(parseInt(jq_tag.css('right'))+jq_tag.outerWidth())/pageZoom)*canvasZoom;
			} else {
				fromX = (parseInt(jq_tag.css('left'))+jq_tag.outerWidth())/pageZoom*canvasZoom;
			}
			var fromY = (parseInt(jq_tag.css('top'))+15)/pageZoom*canvasZoom;
			c.save();
			c.lineWidth = 5;
			c.strokeStyle = jq_tag.css('border-left-color') || jq_tag.css('border-right-color');
			c.fillStyle = jq_tag.css('border-left-color') || jq_tag.css('border-right-color');
			c.globalAlpha = 1;
			jq_tag.data('link').each(function(){
				var x = parseFloat($(this).css('left'))/pageZoom*canvasZoom;
				var y = parseFloat($(this).css('top'))/pageZoom*canvasZoom;
				var w = $(this).outerWidth()/pageZoom*canvasZoom;
				var h = $(this).outerHeight()/pageZoom*canvasZoom;
				var toX = x+(isR?w:0);
				var toY = y+h/2;
				c.beginPath();
				c.moveTo(fromX, fromY);
				c.lineTo(toX, toY);
				c.rect(x, y, w, h);
				c.stroke();
				c.beginPath();
				c.moveTo(toX,toY);
				var r = Math.sqrt(Math.pow(toX-fromX, 2)+Math.pow(toY-fromY, 2));
				c.lineTo(toX-(toX-fromX)*24/r-(toY-fromY)*12/r, toY-(toY-fromY)*24/r+(toX-fromX)*12/r);
				c.lineTo(toX-(toX-fromX)*24/r+(toY-fromY)*12/r, toY-(toY-fromY)*24/r-(toX-fromX)*12/r);
				c.fill();
			});
			c.restore();
		}
	}

	function clearCanvas(c){
		c.clearRect(0, 0, bookW*showPageNum*canvasZoom, bookH*canvasZoom);
	}

	function canvasMoveTo(c, x, y){
		c.moveTo(x*canvasZoom, y*canvasZoom);
	}

	function canvasLineTo(c, x, y){
		c.lineTo(x*canvasZoom, y*canvasZoom);
	}

	$('#PenBtn').on('click', function(){
		if (jq_penTool.is(':visible')){
			closePenTool();
			return;
		}
		$('body').addClass('penMode');
		jq_penTool
			.show()
			.css({
				left: (isMaxWidth(767)? (windowW-jq_penTool.outerWidth())/2 : $('#Footer').offset().left)+'px',
				bottom: (isMaxWidth(767)? 10:$('#BtmArea').height()+20)+'px'
			});

		$('.pageArea canvas').on(startEvent, function(e){
			e.preventDefault();
			e.stopPropagation();

			var c = $('.pageArea').eq(1).find('canvas').get(0).getContext('2d');
			var offsetT = $('.pageArea').eq(1).offset().top;
			var offsetL = $('.pageArea').eq(1).offset().left;
			var offsetR = (showPageNum===1 && isRightPage(curPage))? 0:bookW;
			var touchX = round((getPageX(e)-offsetL)/pageZoom/curZoom-offsetR, 2);
			var touchY = round((getPageY(e)-offsetT)/pageZoom/curZoom-bookH/2, 2);
			var moveX = null;
			var moveY = null;

			var data = {
				linecolor: penColor,
				linesize: penWidth,
				page: getPageGroup(curPage),
				x: [touchX],
				y: [touchY]
			};
			if (penData.length===0){
				penData.push(data);
			} else {
				for (var i=0; i<penData.length; i++){
					if (penData[i].page>getPageGroup(curPage)){
						penData.splice(i,0,data);
						break;
					}
					if (i===penData.length-1){
						penData.push(data);
						break;
					}
				}
			}

			canvasMoveTo(c, touchX+offsetR, touchY+bookH/2, 0);

			$(document).on(moveEvent, function(e){
				e.preventDefault();
				moveX = round((getPageX(e)-offsetL)/pageZoom/curZoom-offsetR, 2);
				moveY = round((getPageY(e)-offsetT)/pageZoom/curZoom-bookH/2, 2);
				if (Math.pow(data.x[data.x.length-1]-moveX,2)+Math.pow(data.y[data.y.length-1]-moveY,2)<1){ return; }
				data.x.push(moveX);
				data.y.push(moveY);
				drowPen(c, curPage);
			}).on(endEvent, function(){
				$(document).off(moveEvent).off(endEvent);
				if (data.x.length<2){
					penData.pop();
				}
				savePenData();
			});
		});
	});

	jq_penTool.on(startEvent, function(e){
		e.preventDefault();

		var initX = parseInt(jq_penTool.css('left'));
		var initY = parseInt(jq_penTool.css('bottom'));
		var touchX = getPageX(e);
		var touchY = getPageY(e);
		var moveX = null;
		var moveY = null;

		$(document).on(moveEvent, function(e){
			e.preventDefault();
			moveX = getPageX(e);
			moveY = getPageY(e);
			jq_penTool.css({
				left: Math.max(0, Math.min(windowW-jq_penTool.outerWidth(), initX+moveX-touchX))+'px',
				bottom: Math.max(0, Math.min(windowH-jq_penTool.outerHeight(), initY+touchY-moveY))+'px'
			});
		}).on(endEvent, function(){
			$(document).off(moveEvent).off(endEvent);
		});
	});
	jq_penTool.find('.closeBtn, .selectList li, .back, .clear').on(startEvent, function(e){
		e.stopPropagation();
	});

	$('#PenTool .closeBtn').on('click', closePenTool);

	function closePenTool(){
		$('body').removeClass('penMode');
		jq_penTool.hide();
		$('.pageArea canvas').off(startEvent);
	}

	$('#PenTool .select li').on('click', function(){
		$(this).addClass('selected').siblings().removeClass('selected');
		if ($('#PenTool .spSelect:visible').length>0){
			$(this).closest('.block').find('.spSelect li').attr('class', $(this).attr('class'));
			$('#PenTool .select').hide();
		}
	});

	$('#PenToolSelectColor li').on('click', function(){
		penColor = $(this).index();
	});

	$('#PenTool .back').on('click', function(){
		for (var i=0; i<penData.length; i++){
			if (penData[i].page===getPageGroup(curPage) && (i===penData.length-1 || penData[i+1].page!==getPageGroup(curPage))){
				penData.splice(i,1);
				break;
			}
		}
		drowPen($('.pageArea').eq(1).find('canvas').get(0).getContext('2d'), curPage);
		savePenData();
	});

	$('#PenTool .clear').on('click', function(){
		var clearStart=null;
		var clearNum=0;
		for (var i=0; i<penData.length; i++){
			if (penData[i].page===getPageGroup(curPage)){
				clearNum++;
				if (clearStart===null){
					clearStart = i;
				}
			}
		}
		if (clearStart!==null){
			penData.splice(clearStart,clearNum);
			savePenData();
		}
		drowPen($('.pageArea').eq(1).find('canvas').get(0).getContext('2d'), curPage);
	});

	$('#PenToolSelectWidth li').on('click', function(){
		penWidth = $(this).index();
	});

	$('#PenTool .spSelect').on('click', function(){
		$('#PenTool .select').not($(this).next('.select')).hide();
		$(this).next('.select').fadeToggle(100);
	});


	/*-------------------------------------------------------------------------
	  ダイアログ
	-------------------------------------------------------------------------*/
	$('.dialog, .dialog .btn').on('click', function(){
		$('.dialog').fadeOut(300);
	});
	$('.dialog .window').on('click', function(e){
		e.stopPropagation();
	});

	$('.spDialog').on('click', function(){
		$('.spDialog').fadeOut(300);
	});
	$('.spDialog .window').on('click', function(e){
		e.stopPropagation();
	});

	function showMessage(msg){
		$('#MessageDialog .window .text').html(msg);
		$('#MessageDialog').removeClass('hasOK').fadeIn(300);
		setTimeout(function(){
			$('#MessageDialog').fadeOut(300);
		},1500);
	}

	function showDialog(msg){
		$('#MessageDialog .window .text').html(msg);
		$('#MessageDialog').addClass('hasOK').fadeIn(300);
	}


	/*-------------------------------------------------------------------------
	  ツールチップ
	-------------------------------------------------------------------------*/
	var jq_tooltip = $('#Tooltip');

	function tooltipPos(e, area){
		jq_tooltip.css({
			left: e.pageX-$(area).offset().left-10+'px',
			top: e.pageY-$(area).offset().top-jq_tooltip.height()-5+'px'
		});
	}

	function setTooltip(target1, target2){
		if (!isPC){ return; }
		$(target1)
			.on('mouseenter', target2, function(e){
				$(this).append(jq_tooltip);
				jq_tooltip.show();
				tooltipPos(e, this);
			})
			.on('mousemove', target2, function(e){
				tooltipPos(e, this);
			})
			.on('mouseleave', target2, function(){
				jq_tooltip.hide();
			});
	}

	/*-------------------------------------------------------------------------
	  PC用ページスライダーの表示・表示
	-------------------------------------------------------------------------*/
	$("div #BtmArea").hover(function () {
		if($('pageSlidebar', xml_contents).text()==='1'){
			$('body').removeClass("hideSlidebar");
			var range = ($('#PageSliderArea').width()-$('#PageSlider').width())/((showPageNum===1? totalPages-startPage:Math.ceil((totalPages+((pageStyle===3)?1:0))/2))*2-2);
			$('#PageSlider').css(opSpread, range*2*(showPageNum===1? curPage-startPage:Math.floor((curPage-startPage+1)/2))+'px');
		}
	}, function() {
		$('body').addClass('hideSlidebar');
	});
});

/*-------------------------------------------------------------------------
  スマホ用 openCart
-------------------------------------------------------------------------*/
var cartWin;
function openCart(url){
	var ua = navigator.userAgent;
	if(ua.indexOf('iPhone')>=0 ||
		ua.indexOf('iPad')>=0 ||
		ua.match(/Android .* Chrome\/.* Mobile/)){
		cartWin = window.open(url);
	} else if(!cartWin ||
		  cartWin.closed ||
		  ua.indexOf('Android')>=0){
		cartWin = window.open(url, 'cart');
	} else if(ua.indexOf('Edge')>=0||
		  (ua.indexOf('Chrome')===-1 &&
		  ua.indexOf('Safari')===-1)){
		cartWin.close();
		cartWin = window.open(url);
	} else {
		cartWin.location.href = url;
	}
	cartWin.focus();
}

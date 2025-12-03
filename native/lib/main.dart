import 'dart:async';
import 'dart:io';
import 'dart:convert';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:flutter_native_splash/flutter_native_splash.dart';
import 'package:webview_cookie_manager_plus/webview_cookie_manager_plus.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:share_plus/share_plus.dart';
import 'package:flutter/services.dart' show SystemChrome, rootBundle;
import 'package:firebase_core/firebase_core.dart';
import 'package:material_symbols_icons/material_symbols_icons.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:fcm_config/fcm_config.dart';
import 'package:intl/intl.dart';
import 'package:firebase_analytics/firebase_analytics.dart';

// ニュースID
var news_id = '';
// プッシュトークン
var token_id = '';
// セシール暗号化客番
var ssi_id = '';
// アプリ内で生成した識別コード
var app_user_id = '';

// WebViewコントローラー(セシールラボ)
late WebViewController _webViewLabController;
// WebViewコントローラー(セシールサイト)
late WebViewController _webViewController;
// クッキー初利用
late final WebviewCookieManager _cookieManager = WebviewCookieManager();
// Firebase Messaging
final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
// Firebase Analytics
final FirebaseAnalytics _analytics = FirebaseAnalytics.instance;

// トップレベルに定義
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  var title = message.notification!.title;
  var body = message.notification!.body;
  try {
    news_id = message.data['lp'].toString();
    final logDirectory = await getApplicationDocumentsDirectory();
    await File('${logDirectory.path}/push.log').writeAsString(news_id);
  } catch(err){}
}
/*
Future<void> _firebaseMessagingBackgroundHandler(
    RemoteMessage _notification) async {
  await Firebase.initializeApp();
  //  print('バックグラウンドでメッセージを受け取りました');
  String title = _notification.data['title'];
  String body = _notification.data['body'];
  try {
    news_id = _notification.data['lp'].toString();
    final Directory logDirectory = await getApplicationDocumentsDirectory();
    await File('${logDirectory.path}/push.log').writeAsString(news_id);
  } catch(err){}
  // Androidでは使っていないけど、iOS限定で使っているとまずいので、とりあえず残している
  FCMConfig.instance.local.displayNotification(title: title ?? '', body: body ?? '');
}
*/

// Androidでは使っていなけど、iOS用のおまじないとして残しておく
final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
FlutterLocalNotificationsPlugin();

// Androidでは使っていなけど、iOS用のおまじないとして残しておく
const AndroidNotificationChannel channel = AndroidNotificationChannel(
  'high_importance_channel', // id
  'High Importance Notifications', // title
  description: 'This channel is used for important notifications.', // description
  importance: Importance.high,
);

// Cookieを設定する関数
Future<void> setCustRegistFlagToOne(String domain) async {
  // 1. Cookieオブジェクトを作成（このパッケージ固有の 'Cookie' クラスを使用）
  final newCookie = Cookie('custregist-flg', '1')
    ..domain = domain // 必須：Cookieを適用するドメイン (例: 'example.com')
    ..expires = DateTime.now().add(const Duration(days: 365)) // 有効期限を設定
    ..httpOnly = false; // 必要に応じて設定

  // 2. setCookiesメソッドにリストとして渡して設定/上書き
  try {
    await _cookieManager.setCookies([newCookie]);
    debugPrint('Cookie "custregist-flg" was successfully set to "1" for domain $domain.');
  } catch (e) {
    debugPrint('Failed to set cookie: $e');
  }
}

//void main() {
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  //バックグラウンド用
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  // 画面の向きを固定.
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
  ]);
  /** 音声入力の権限を許可する処理だけど、うまく動かないから、一旦コメントアウト
  if (await Permission.speech.isPermanentlyDenied) {
    openAppSettings();
  }*/
  runApp(CecileApp());
}

class CecileApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: WebViewScreen(),
    );
  }
}

class WebViewScreen extends StatefulWidget {
  _WebViewScreenState createState() => _WebViewScreenState();
}

class _WebViewScreenState extends State<WebViewScreen> with WidgetsBindingObserver {
  // デバッグ出力用フラグ
  final bool _debug = true;
  // アプリ設定画面のアプリバージョンに表示される値
  final String _appVer = '1.0.0';
  // セシールサイトへのリンク時に、どこからのアクセスかを識別するためのパラーメータ
  final app_param = 'utm_source=cecile_labo&utm_medium=app_labo&utm_campaign=app_251101';
  // アシスタント画面のURL
  final String actualBaseUrl = 'https://cecile.yamateras.jp/';
  // ブラウザのユーザーエージェント
  final String uaApp = 'CecileLaboApp/1.0 (Mobile; WebView)';

  int _selectedIndex = 0;
  int _webviewIndex = 0;
  int _history_cnt = 0;
  bool _isLoading = false;
  bool _isPopup = false;
  bool _isActive = false;
  bool _isBar = true;
  bool _showAppBar = false;
  bool _inactive = false;
  String _initapp = '0';
  // アシスタント処理のHTMLソースを管理する変数
  // アプリを閉じるまで、アシスタントの表示を保持する仕様の為
  String assistant_src = '';
  // ホーム処理のHTMLソースを管理する変数
  // アプリを閉じるまで、ホームの表示を保持する仕様の為
  String home_src = '';
  late Timer _timer;

  bool _sendToken = false;
  bool _isSsi = false;
  bool _isSsi_Token = false;

  // 色関連の固定値を管理する変数
  final _selectedItemColor = Color.fromRGBO(209, 63, 125, 1.0);//Colors.white;
  final _unselectedItemColor = Color.fromRGBO(99, 99, 99, 1.0);
  final _selectedBgColor = Colors.white;//Color.fromRGBO(156, 20, 74, 1.0);
  final _unselectedBgColor = Colors.white;

  // 初期URL
  final String initialUrl = 'https://cecile.yamateras.jp/visual';
  // メニューURL
  List<String> _urlList = [
    'https://cecile.yamateras.jp/visual',
    'https://cecile.yamateras.jp/catalog',
    'https://cecile.yamateras.jp/assistant',
    'https://cecile.yamateras.jp/',
    'https://cecile.yamateras.jp/guide',
    'https://cecile.yamateras.jp/receipter',
    'https://cecile.yamateras.jp/receipt?code=',
  ];
  final List<String> cecileLinks = [
    'www.cecile.co.jp', 'cfg.smt.docomo.ne.jp', 'id.smt.docomo.ne.jp', 'payment1.smt.docomo.ne.jp'
  ];

  @override
  void initState() {
    super.initState();
    if (Platform.isIOS) {
      FirebaseMessaging.instance.requestPermission();
    }

    // ブラウザビューの初期化
    initWebViewState();
    // プラットフォームの初期化
    initPlatformState();

    // iOSの場合、セシールサイトでエラー項目が表示されるので、Cookieをセットして回避する
    setCustRegistFlagToOne('cecile.co.jp');

    // 今回表示する、おすすめURLを取得する
    _onRecommendUri();

    // ローカルファイルに保存しているPush通知の情報があれば、
    // その情報を利用して、PopUpダイアログを表示する
    _timer = Timer.periodic(
      Duration(seconds: 3), // 3秒毎に定期実行
      (Timer timer) {
        setState(() async { // 変更を画面に反映するため、setState()している
          try {
            final logDirectory = await getApplicationDocumentsDirectory();
            news_id = await File('${logDirectory.path}/push.log').readAsString();
            if (news_id != '') {
              try {
                _selectedIndex = 0;
                _webViewController.loadRequest(Uri.parse(news_id+'?'+app_param));
                final dir = Directory('${logDirectory.path}/push.log');
                dir.deleteSync(recursive: true);
              }
              catch (err) {}
            }
          }
          catch(err){}
        });
      },
    );

    FirebaseMessaging.onMessageOpenedApp.listen((message) async {
      news_id = message.data['lp'].toString();
      final Directory logDirectory = await getApplicationDocumentsDirectory();
      await File('${logDirectory.path}/push.log').writeAsString(news_id);
    });
    FirebaseMessaging.onMessage.listen((message) async {
      news_id = message.data['lp'].toString();
      final Directory logDirectory = await getApplicationDocumentsDirectory();
      await File('${logDirectory.path}/push.log').writeAsString(news_id);
    });
  }

  Future<void> initWebViewState() async {
    /**
     * セシールラボ用WebView
     */
    _webViewLabController = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setUserAgent(uaApp)
      ..setNavigationDelegate(
          NavigationDelegate(
            onNavigationRequest: (NavigationRequest request) {
              if ((!request.isMainFrame) ||
                  (initialUrl == request.url)) {
                return NavigationDecision.navigate;
              }
              // ブラウザで開くリンクの判別
              final uri = Uri.parse(request.url);
              // グローバルメニュー選択後のページカウント数
              _history_cnt++;
              if (uri.path.contains('text/html')) {
                // HTMLソースを直接WebViewに渡す場合は処理を除外する
                // iOS向けの対策
                return NavigationDecision.navigate;
              }
              else if (uri.path.contains('/app_notification')) {
                // アプリ設定画面へ移動
                _history_cnt = 0;
                openAppSettings();
                return NavigationDecision.prevent;
              }
              else if (uri.path == "/app_allreset") {
                // アプリ内のデータをリセット
                _history_cnt = 0;
                // 削除確認ダイアログを表示
                showDialog(
                  context: context,
                  builder: (_) => AlertDialog(
                    title: Text('削除確認'),
                    content:
                    Text(
                      'アプリ内で保持しているデータを削除してもよろしいですか？',
                      style: TextStyle(fontSize: 14, color: _unselectedItemColor)
                    ),
                    actions: <Widget>[
                      TextButton(
                        child: Text('キャンセル'),
                        onPressed: () => Navigator.of(context).pop(1),
                      ),
                      TextButton(
                        child: Text('削除'),
                        onPressed: () async {
                          Navigator.of(context).pop(1);
                          // WebViewのCookieを削除
                          await _cookieManager.clearCookies();
                          // キャッシュデータの削除
                          await _webViewController.clearCache();
                          await _webViewLabController.clearCache();
                          await _webViewController.clearLocalStorage();
                          await _webViewLabController.clearLocalStorage();
                          assistant_src = "";
                          home_src = "";
                          // 完了メッセージを表示
                          showDialog(
                            context: context,
                            builder: (_) => _buildDialog('削除完了', 'アプリ内で保持しているデータを削除しました。', 'OK')
                          );
                        },
                      ),
                    ],
                  )
                );
                return NavigationDecision.prevent;
              }
              // 暗号化客番
              else if (uri.path == "/app_ssi") {
                // 暗号化客番を共有で通知する
                _onRequestSSI();
                return NavigationDecision.prevent;
              }
              else if (uri.path == "/app_token") {
                // プッシュ通知端末登録
                // プッシュ通知のトークンを取得する
                _history_cnt = 0;
                _onRequestPermissions();
                return NavigationDecision.prevent;
              }
              else if (uri.path == "/app_version") {
                // アプリバージョンの表示
                showDialog(
                  context: context,
                  builder: (_) => _buildDialog('アプリバージョン', _appVer, 'OK')
                );
                return NavigationDecision.prevent;
              }
              else if (uri.path == "/app_cacheclear") {
                // WebViewのキャッシュを削除(Androidのみ)
                // キャッシュクリア確認ダイアログを表示
                _history_cnt = 0;
                showDialog(
                  context: context,
                  builder: (_) => AlertDialog(
                    title: Text('キャッシュ削除確認'),
                    content:
                    Text(
                      'キャッシュデータを削除してもよろしいですか？',
                      style: TextStyle(fontSize: 14,
                        color: _unselectedItemColor)
                    ),
                    actions: <Widget>[
                      TextButton(
                        child: Text('キャンセル'),
                        onPressed: () =>Navigator.of(context).pop(1),
                      ),
                      TextButton(
                        child: Text('削除'),
                        onPressed: () async {
                          Navigator.of(context).pop(1);
                          // キャッシュデータの削除
                          await _webViewController.clearCache();
                          await _webViewLabController.clearCache();
                          assistant_src = "";
                          home_src = "";
                          // 完了メッセージを表示
                          showDialog(
                            context: context,
                            builder: (_) => _buildDialog('クリア完了', 'アプリ内のキャッシュデータの削除が正常に完了しました。', 'OK')
                          );
                        },
                      ),
                    ],
                  )
                );
                return NavigationDecision.prevent;
              }
              else if(request.url.contains('.cecile.co.jp')) {
                /**
                 * セシールサイトなので、ブラウザを切り替える
                 */
                setState(() {
                  //_selectedIndex = 0;
                  _webviewIndex = 1;
                  _history_cnt = 0;
                  _showAppBar = true;
                  _inactive = true;
                  if(request.url.contains('/search-results/?')) _webViewController.loadRequest(Uri.parse(request.url+'&'+app_param));
                  else _webViewController.loadRequest(Uri.parse(request.url+'?'+app_param));
                });
                return NavigationDecision.prevent;
              }
              else if (uri.path == "/app_exit") {
                _isBar = true;
                _isActive = true;
                _onItemTapped(_selectedIndex);
                _isActive = false;
                return NavigationDecision.prevent;
              }
              else if (uri.path == "/settings") {
                // WebView内で遷移
                _isBar = false;
                _isActive = true;
                _webViewLabController.clearCache();
                _onItemTapped(_selectedIndex);
                _webViewLabController.loadRequest(Uri.parse(_urlList[5]));
                _isActive = false;
                return NavigationDecision.prevent;
              }
              else if(request.url.contains('.pdf')
                  || request.url.contains('mailto:')
                  || request.url.contains('intent:')
                  || request.url.contains('javascript')){
                canLaunch(request.url).then((result) {
                  // 外部ブラウザで遷移
                  _history_cnt--;
                  launch(
                    request.url,
                    forceSafariVC: false,
                    forceWebView: false,
                  );
                });
                // 何もしない
                return NavigationDecision.prevent;
              }
              else if(request.url.contains('http://')){
                // http通信はWebViewでエラーとなるので、https通信へ変換する。
                var http_uri = request.url.replaceAll('http://','https://');
                _webViewLabController.loadRequest(Uri.parse(http_uri));
                return NavigationDecision.prevent;
              }
              // Google Analyticsのイベントログ
              _analytics.logEvent(
                name: "page_view",
                parameters: {
                  "page": request.url,
                }
              );
              return NavigationDecision.navigate;
            },
          )
      )
      ..loadRequest(Uri.parse(initialUrl));

    /**
     * セシールサイト用WebView
     */
    _webViewController = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setUserAgent(uaApp)
      ..setNavigationDelegate(
        NavigationDelegate(
          onWebResourceError: (WebResourceError error) {
          },
          onPageStarted: (String url) {
            setState(() {
              _isLoading = true;
            });
          },
          onPageFinished: (String url) async {
            setState(() {
              _isLoading = false;
            });
            _history_cnt++;
            var host = Uri.parse(url).host;

            // セシールのログインを管理しているIDをサーバーに送信
            try{
              bool _isCookie = false;
              if(url.contains('CartSrv.jsp')||url.contains('CompleteSrv.jsp')||url.contains('ConfSrv.jsp')) _isCookie = true;
              else if(url.contains('LoginSrv.jsp')){
                _isCookie = false;
                ssi_id = '';
                _isSsi_Token = false;
                _isSsi = false;
              }
              else if(!_isSsi) _isCookie = true;
              /**
               * クッキーが取得できていて、SSIの値が取得できていなければ、セシールサイトに接続して取得する
               */
              if(_isCookie){
                final gotCookies = await _cookieManager.getCookies('https://www.cecile.co.jp');
                for (var item in gotCookies) {
                  if(item.name=='EncryptedCustNo') {
                    // 暗号化客番
                    ssi_id = item.value;
                    final response = await Dio().get('https://api.interestag.jp/cecilelab/?android__'+app_user_id+'__'+ssi_id);
                    if (token_id!='') {
                      if(!_isSsi_Token){
                        final response2 = await Dio().get('https://api.interestag.jp/cecilelab/?ssi_token__android__'+ssi_id+'__'+token_id);
                        _isSsi_Token = true;
                      }
                    }
                    _isSsi = true;
                    try {
                      if (ssi_id!='') {
                        final logDirectory = await getApplicationDocumentsDirectory();
                        await File('${logDirectory.path}/ssi.data').writeAsString(ssi_id);
                      }
                    } catch (err) {}
                  }
                }
              }
            }
            catch(err){}

            if(url.contains('.pdf')
                || !(url.contains('www.cecile.co.jp')
                    || url.contains('digicata.cecile.co.jp')
                    || url.contains('extif.cecile.co.jp')
                    || url.contains('www.e-scott.jp')
                    || url.contains('.docomo.ne.jp')
                )
                || url.contains('mailto:')
                || url.contains('facebook.com')
                || url.contains('javascript')){
              if (await canLaunch(url)) {
                // 外部ブラウザで遷移
                _history_cnt--;
                await launch(
                  url,
                  forceSafariVC: false,
                  forceWebView: false,
                );
              }
              _webViewController.goBack();
            }
            else if(url.contains('naver.line')){
              var uri = url.replaceAll('intent:', 'line:');
              if (await canLaunch(uri)) {
                // 外部ブラウザで遷移
                _history_cnt--;
                await launch(
                  uri,
                  forceSafariVC: false,
                  forceWebView: false,
                );
              }
              _webViewController.goBack();
            }
            else if(url.contains('http://')){
              // http通信はWebViewでエラーとなるので、https通信へ変換する。
              _webViewController.goBack();
              _history_cnt--;
              var http_uri = url.replaceAll('http://','https://');
              _webViewController.loadRequest(Uri.parse(http_uri));
            }
            else if(url.contains('NetBankSelectSrv')){
              // ネットバンクの別ウィンドウのPOST送信処理の処理調整
              try {
                await _webViewController.runJavaScript("document.querySelectorAll('dl.netbank-list form').forEach(function(element){let link_path='https://cecile-op.prm.bz/nbgwdmy?RD_URL='+element.action;if(element.acceptCharset) link_path+='&charset='+element.acceptCharset;element.querySelectorAll('input').forEach(function(input){link_path+='&'+input.name+'='+encodeURI(input.value);});let parent=element.querySelector('div.button');let button=parent.querySelector('button');button.removeAttribute('type');button.removeAttribute('onclick');button.setAttribute('type','button');element.setAttribute('onsubmit','return false');button.setAttribute('onclick','location.href=`'+link_path+'`');});");
              }catch(err){}
            }
            else{
              // ポップアップフラグが立っていれば、Popup情報を画面表示する
              // _isPopup=true;
              /*
              if(_isPopup){
                try {
                  await _webViewController.runJavaScript("let _style = document.createElement('style');_style.innerText='div.dammy{position:fixed;width:100%;height:100%;top:0px;left:0px;z-index:9;background-color:rgba(0,0,0,0.5);}div.popup{position:fixed;box-sizing:border-box;width:90%;top:50%;left:5%;transform:translateY(-50%);-webkit-transform:translateY(-50%);-ms-transform:translateY(-50%);text-align:center;background-color:#fff;z-index:10;padding:15px 0px;border-radius:10px;}div.popup img{box-sizing:border-box;width:100%;height:auto;padding:0px 15px;}div.popup p{text-align:left;box-sizing:100%;padding:0px 15px;margin:0px;margin-bottom:15px;}div.popup a{text-decoration:none;}div.popup div.closebtn{font-weight:bold;display:inline-block;color:#fff;position:absolute;top:-25px;right:5px;cursor:pointer;}';let _pp=document.createElement('div');_pp.setAttribute('class','popup'),_dm=document.createElement('div');_dm.setAttribute('class','dammy');document.body.style.cssText='overflow-y:hidden';function handleTouchMove(event){event.preventDefault();}document.addEventListener('touchmove',handleTouchMove,{passive:false});let _lnk='"+_popup[0]+"',_ht='<div class=\"closebtn\">✕</div><a href=\"'+_lnk+'\"><p>"+_popup[2]+"</p><img src=\""+_popup[1]+"\"></a>';document.body.appendChild(_pp);document.body.appendChild(_dm);_pp.innerHTML=_ht;document.getElementsByTagName('head')[0].insertAdjacentElement('beforeend',_style);document.querySelector('div.closebtn').addEventListener('click',function(){document.querySelector('div.popup').style.display='none';document.querySelector('div.dammy').style.display='none';document.body.style.cssText='overflow-y:auto';document.removeEventListener('touchmove',handleTouchMove,{passive:false});});");
                }
                catch(err){}
                _isPopup = false;
              }
              */
              try{
                if (app_user_id!='') {
                  // アプリのユーザーIDをサーバーに送信
                  try{
                    final response = await Dio().get(
                      'https://api.interestag.jp/cecilelab/?event_'+app_user_id+'__'+url
                    );
                  }
                  catch(err){}
                }
                if (token_id!='') {
                  // アプリで最初の通信処理時に、トークンIDをサーバーに送信しておく
                  if(!_sendToken) {
                    _sendToken = true;
                    final response = await Dio().get('https://api.interestag.jp/?token_'+app_user_id+'__'+token_id);
                  }
                }
              }
              catch(err){}

              // 閉じるボタンを消す
              try {
                final closebtn = await _webViewController.runJavaScriptReturningResult('document.querySelector(".button-c.-close").innerHTML;');
                if (closebtn != '') await _webViewController.runJavaScript('document.querySelector(".button-c.-close").style.display="none";');
              }
              catch(err){}
              try {
                // アプリバナーを消す
                final appbnr = await _webViewController.runJavaScriptReturningResult('document.querySelector(".smartbanner").innerHTML;');
                if(appbnr!=''){
                  await _webViewController.runJavaScript('document.querySelector(".smartbanner").style.display="none";');
                  await _webViewController.runJavaScript('document.querySelector(".smartbanner-show").style.marginTop="0px";');
                }
              }
              catch(err){}
              try {
                await _webViewController.runJavaScript('var anchors = document.querySelectorAll("a[href\$=pdf]");anchors.forEach(function(a){txt=a.href;a.href = "https://docs.google.com/viewer?url="+txt;});');
              }
              catch(err){}
              try{
                if(url.contains('ReceiptSrv')){
                  final printbtn = await _webViewController.runJavaScriptReturningResult('document.querySelector(".receipt-print a").innerHTML;');
                  if(printbtn!=''){
                    final receiptsrc = await _webViewController.runJavaScriptReturningResult('document.querySelector("body").innerHTML;');
                    final dio = Dio();
                    dio.options.headers = {
                      'Content-Type': 'application/x-www-form-urlencoded'
                    };
                    var formData = FormData.fromMap({
                      'src': receiptsrc
                    });
                    final response = await dio.post(
                      _urlList[5],
                      data: formData,
                    );
                    if(response.data.toString()!=''){
                      _webViewController.goBack();
                      _history_cnt--;
                      await launch(
                        _urlList[6]+response.data.toString(),
                        forceSafariVC: false,
                        forceWebView: false,
                      );
                    }
                  }
                }
              }
              catch(err){}
            }
            // Google Analyticsのイベントログ
            _analytics.logEvent(
              name: "page_view",
              parameters: {
                "page": url,
              }
            );
            debugPrint(url);
          },
        ),
      );
//      ..loadRequest(Uri.parse(initialUrl));
  }

  Future<void> initPlatformState() async {
    _firebaseMessaging.getToken().then((token) async {
      token_id = "$token";
    });
    if (!mounted) return;
    setState(() async{
      final logDirectory = await getApplicationDocumentsDirectory();
      final DateTime now = DateTime.now();
      final DateFormat outputFormat = DateFormat('HmddyyyyMM');
      try {
        var appId = await File('${logDirectory.path}/app.data').readAsString();
        if (appId != '') {
          // アプリIDをセット
          app_user_id = appId;
        }
        else{
          try {
            app_user_id = outputFormat.format(now)+randomString(18);
            await File('${logDirectory.path}/app.data').writeAsString(app_user_id);
          } catch (err) {}
        }
      }
      catch(err){
        try {
          app_user_id = outputFormat.format(now)+randomString(18);
          await File('${logDirectory.path}/app.data').writeAsString(app_user_id);
        } catch (err) {}
      }
      // 暗号化客番
      try {
        var _ssi = await File('${logDirectory.path}/ssi.data').readAsString();
        if (_ssi != ''){
          ssi_id = _ssi;
          _onRecommendUri();
        }
      }
      catch(err){}
    });
  }

  /**
   * アプリ用の簡易ユーザーIDの生成
   * 端末の固有識別IDの取得が出来なくなったので。
   */
  String randomString(int length) {
    const _randomChars = "_#|()ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    const _charsLength = _randomChars.length;
    final rand = new math.Random();
    final codeUnits = new List.generate(
      length,
          (index) {
        final n = rand.nextInt(_charsLength);
        return _randomChars.codeUnitAt(n);
      },
    );
    return new String.fromCharCodes(codeUnits);
  }

  /**
   * BottomNavigation 切り替えで動作
   */
  void _onItemTapped(int index) {
    _history_cnt = -1;
    setState(() {
      // アシスタントモードの場合、HTMLソースを保持する
      if(_selectedIndex == 2) {
        // ページ読み込み完了時にHTMLを取得
        _getHtmlSource(_selectedIndex);
      }
      // 表示するページのURL
      _selectedIndex = index;
      // 表示する画面がアシスタントの場合、ページキャッシュがあれば、
      // キャッシュを表示する
      if(index == 1 && assistant_src != ''){
        // キャッシュを表示する
        final Uri dataUri = Uri.dataFromString(
          assistant_src,
          mimeType: 'text/html',
          encoding: Encoding.getByName('utf-8'),
          parameters: {
            'baseUrl': actualBaseUrl,
          },
        );
        _webViewLabController.loadRequest(dataUri);
      }
      else {
        // セシラボブラウザを表示
        _webviewIndex = 0;
        _showAppBar = false;

        if (_webviewIndex == 0){
          _webViewLabController.loadRequest(Uri.parse(_urlList[index]));
          _inactive = false;
        }
        /*
        else if(index==3){
          // 暗号化客番付でお知らせ配信履歴画面を開く
          String _uri = _urlList[index]+ssi_id;
          _webViewCecileController.loadRequest(Uri.parse(_uri));
        }
        */
        else
          _webViewController.loadRequest(Uri.parse(_urlList[index]));
        // Google Analyticsのイベントログ
        _analytics.logEvent(
          name: "menu_view",
          parameters: {
            "menu": index,
          }
        );
      }
    });
  }

  /**
   * WebViewからHTMLソースを取得する
   */
  Future<void> _getHtmlSource(int type) async {
    try{
      // JavaScriptを実行してHTML全体を取得
      // 'document.documentElement.outerHTML'はページ全体のHTML要素を文字列として返します
      final String html = await _webViewLabController.runJavaScriptReturningResult(
          "document.documentElement.outerHTML"
      ) as String;
      setState(() {
        if(type==0) home_src = html.isNotEmpty ? jsonDecode(html).toString() : "";
        else assistant_src = html.isNotEmpty ? jsonDecode(html).toString() : "";
      });
    }
    catch(e){
      setState((){
        if(type==0) home_src = "";
        else assistant_src = "";
      });
    }
  }

  /**
   * 共有機能を利用して、取得しているトークンを表示する
   */
  Future<void> _onRequestPermissions() async {
    _firebaseMessaging.getToken().then((token) async {
      // 取得したトークンを共有する
      await Share.share("$token");
    });
  }

  /**
   * 共有機能を利用して、取得しているSSIを表示する
   */
  Future<void> _onRequestSSI() async {
    await Share.share(ssi_id);
  }

  /**
   * エラーメッセージ表示ダイアログ
   * OKボタン選択後に、指定した処理を実行する
   */
  Future<void> _onWebPageByErrMsg(String message, int index) async {
    showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title :Text('お知らせ'),
          content: Text(message
              , style: TextStyle(fontSize: 14, color: _unselectedItemColor)),
          actions: <Widget>[
            TextButton(
              child: Text('OK'),
              onPressed: () async {
                Navigator.of(context).pop(1);
                // キャッシュをクリアし、指定ページへ遷移する
                await _webViewLabController.clearCache();
                _webViewLabController.loadRequest(Uri.parse(_urlList[index]));
              },
            ),
          ],
        )
    );
  }

  /**
   * 今のおすすめURLの取得処理
   */
  Future<void> _onRecommendUri() async {
    /*
    List _recommends = [
      <String>[
        'https://www.cecile.co.jp/feature/gift/',
        'https://www.cecile.co.jp/genre/g1/1/UN/bargain/',
      ],
      <String>[
        'https://lw.cecile.co.jp/feature/gift/',
        'https://lw.cecile.co.jp/genre/g1/1/UN/bargain/',
      ]
    ];

    try {
      final dio = Dio();
      final response = await dio.get(
        'https://cecile-app.prm.bz/recommend?ssi='+ssi_id+'&did='+device_id,
      );
      _urlList[0][1] = response.data;
      _urlList[1][1] = response.data;
    } catch (err) {
      _urlList[0][1] = _recommends[_accessPoint][math.Random().nextInt(2)];
      _urlList[1][1] = _recommends[_accessPoint][math.Random().nextInt(2)];
    }
    */
  }

  /**
   * 下部メニューの背景色を動的に変更する
   */
  Color _getBgColor(int index) =>
      _selectedIndex == index ? _selectedBgColor : _unselectedBgColor;

  /**
   * 下部メニューの文字色を動的に変更する
   */
  Color _getItemColor(int index) =>
      _selectedIndex == index && _inactive == false ? _selectedItemColor : _unselectedItemColor;

  /**
   * 下部メニューのアイコンのFILLを動的に変更する
   */
  double _getIconFill(int index) =>
      _selectedIndex == index && _inactive == false ? 1.0 : 0;

  /**
   * 下部メニューのアイコンに背景を設定する
   */
  Widget _buildIcon(IconData iconData, String text, int fontsize, int index) => Container(
    width: double.infinity,
    height: kBottomNavigationBarHeight,
    child: Material(
      color: _getBgColor(index),
      child: InkWell(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Icon(iconData, size: 28.0, fill: _getIconFill(index), color: _getItemColor(index)),
            Text(text, textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 9,height: 1.1, color: _getItemColor(index))),
          ],
        ),
        onTap: () => _onItemTapped(index),
      ),
    ),
  );

  /**
   * 文字列のダイアログを表示
   */
  Widget _buildDialog(String title, String message, String btn) => AlertDialog(
    title :Text(title),
    content: Text(message
        , style: TextStyle(fontSize: 14, color: _unselectedItemColor)),
    actions: <Widget>[
      TextButton(
        child: Text(btn),
        onPressed: () => Navigator.of(context).pop(1),
      ),
    ],
  );

  /**
   * 画像表示付きのダイアログを描画
   */
  Widget _buildImageDialog(String imgpath, String message, String btn, String linkbtn, String linkurl) => AlertDialog(
    titlePadding: EdgeInsets.zero,
    title : Image.network(
      imgpath,
      height: 300,  //写真の高さ指定
      fit: BoxFit.cover,
    ),
    content: Text(message
        , style: TextStyle(fontSize: 14, color: _unselectedItemColor)),
    actions: <Widget>[
      TextButton(
        child: Text(linkbtn),
        onPressed: () {
          _webViewController.loadRequest(Uri.parse(linkurl));
          Navigator.of(context).pop(1);
        },
      ),
      TextButton(
        child: Text(btn),
        onPressed: () => Navigator.of(context).pop(1),
      ),
    ],
  );

  /**
   * ブラウザの戻る処理
   */
  Future<bool> _willPopCallback() async {
    if(_history_cnt>0){
      if(_webviewIndex==1) _webViewController.goBack();
      else _webViewLabController.goBack();
      _history_cnt--;
    }
    return false;
  }

  // 戻るボタンのウィジェット
  Widget backButton(WebViewController controller) {
    return IconButton(
      iconSize: 20.0,
      icon: const Icon(Icons.arrow_back_ios),
      onPressed: () async {
        setState(() {
          _webviewIndex = 0;
          _showAppBar = false;
          _inactive = false;
        });
      },
    );
  }

  // WebViewを一つ前に戻す処理
  Future<void> _goBackInWebView() async {
    // 戻る履歴があるか確認してからgoBack()を呼び出すのが一般的です
    if (await _webViewController.canGoBack()) {
      await _webViewController.goBack();
    }
    else{
      // 戻る履歴がない場合の処理（例：ログ出力、Snackbar表示など）
      setState(() {
        _webviewIndex = 0;
        _showAppBar = false;
        _inactive = false;
      });
    }
  }

  /**
   * 下部メニューバーの描画処理
   */
  Widget build(BuildContext context) {
    final _webViewWidget = [
      WebViewWidget(controller: _webViewLabController),
      WebViewWidget(controller: _webViewController),
    ];
    return WillPopScope(
        onWillPop: _willPopCallback,
        child: Scaffold(
            backgroundColor: Colors.white,
            appBar: _showAppBar ? PreferredSize(
              // appBarにセシラボに戻るバーを表示
              preferredSize: Size.fromHeight(40.0),
              child: AppBar(
                elevation: 0,
                centerTitle: false,
                //title: const Text('セシラボへ戻る', style: TextStyle(fontSize: 14, color: Colors.blueGrey)),
                title: InkWell(
                  // タップイベントを処理
                  onTap: _goBackInWebView,
                  // titleとして表示するウィジェット
                  child: const Padding(
                    padding: EdgeInsets.symmetric(vertical: 8.0, horizontal: 4.0), // タップ領域を確保
                    child: Text('前の画面へ戻る', style: TextStyle(fontSize: 14, color: Colors.black)),
                  ),
                ),
                leading: Padding(
                  padding: EdgeInsets.only(left: 10.0, right: 0), // 左側に 10.0 のパディングを追加
                  child: backButton(_webViewController), // 戻るのアイコンボタン
                ),
                leadingWidth: 35.0,
                // leading: backButton(_webViewController),
              ),
            ): PreferredSize(
              // appBarのサイズを0にし、バーを消す
              preferredSize: Size.fromHeight(0),
              child: AppBar(
                elevation: 0,
                backgroundColor: Colors.transparent,
              ),
            ),
            body: IndexedStack(
              index: _webviewIndex,
              children: _webViewWidget,
            ),
            bottomNavigationBar: Container(
                margin: EdgeInsets.only(top: 0, bottom: 0),
                child: _isBar
                    ? BottomNavigationBar(
                  // selectedFontSizeの値を0にする事でスペースが消える
                  selectedFontSize: 0,
                  items: [
                    BottomNavigationBarItem(
                      icon: _buildIcon(
                          IconData(
                            Symbols.home.codePoint,
                            fontFamily: 'MaterialSymbolsOutlined',
                            fontPackage: 'material_symbols_icons',
                          ), 'ホーム', 12, 0),
                      label: '',
                    ),
                    BottomNavigationBarItem(
                      icon: _buildIcon(
                          IconData(
                            Symbols.book_4.codePoint,
                            fontFamily: 'MaterialSymbolsOutlined',
                            fontPackage: 'material_symbols_icons',
                          ), 'カタログ', 12, 1),
                      label: '',
                    ),
                    BottomNavigationBarItem(
                      icon: _buildIcon(
                          IconData(
                            Symbols.forum.codePoint,
                            fontFamily: 'MaterialSymbolsOutlined',
                            fontPackage: 'material_symbols_icons',
                          ), 'アシスタント', 12, 2),
                      label: '',
                    ),
                    BottomNavigationBarItem(
                      icon: _buildIcon(IconData(
                        Symbols.chart_data.codePoint,
                        fontFamily: 'MaterialSymbolsOutlined',
                        fontPackage: 'material_symbols_icons',
                      ), 'おすすめ', 12, 3),
                      label: '',
                    ),
                    BottomNavigationBarItem(
                      icon: _buildIcon(IconData(
                        Symbols.article_person.codePoint,
                        fontFamily: 'MaterialSymbolsOutlined',
                        fontPackage: 'material_symbols_icons',
                      ), '使い方', 12, 4),
                      label: '',
                    ),
                  ],
                  currentIndex: _selectedIndex,
                  selectedItemColor: _selectedItemColor,
                  type: BottomNavigationBarType.fixed,
                ) : Container(
                  color: Colors.white,
                  width: MediaQuery
                    .of(context)
                    .size
                    .width,
                  height: 0,
                )
            )
        )
    );
  }
}

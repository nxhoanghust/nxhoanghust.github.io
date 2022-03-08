---
layout: post
title:  "Write Up HITB PRO 2021"
date:   2021-11-28 21:15:53 +0700
categories: jekyll update
---
* Do not remove this line (it will not be displayed)
{:toc}

# **I.Mở đầu**
Đợt giữa tuần vừa rồi mình và team có tham gia HITB cùng với những team có thể nói là sừng xỏ nhất thế giới hiện tại và thực sự trải nghiệm tại giải lần này thật sự quý giá đối với mình cx như cả team. Giải lần này thi dưới hình thức ATK & DEF với 11 bài được release trong suốt quá trình chơi. Thật sự bài của giải lần này thực sự rất rất hay, vừa ngắn, dễ hiểu, dễ đọc, dễ debug tuy nhiên cũng rất khó.
Team mình dừng lại ở top 18, top 3 so với những team thi đấu online, đây cũng là một kết quả khá tốt dối với team, ae cũng đã try hard khá ghê để có được kết quả như trên. Shout out to my teammmm.
![bxh](/assets/hitbpro/bxh.png)
- Suốt 30h cuôc thi thì HITB release 11 challs và 5 trong đó thụôc categories web. Team mình có may mắn solve được 3/5 tuy nhiên vì solve chậm cũng như không chuẩn bị kĩ nên số flag chiếm được k nhiều =))) 
- Dưới đây sẽ là wu về mấy bài này.
# **II.FS**
[fs.tar](https://transfer.sh/xIGFR5/fs.tar){:target="_blank"}{:rel="noopener noreferrer"}
- Bài này source nhìn thì có vẻ nhiều nhưng chức năng thật ra cũng khá đơn giản và dễ hiểu. Đầu tiên ta sẽ xem flag của bài ở đâu. Theo API description mà giải cung cấp thì flag sẽ nằm folder data. T sẽ nói qua về chức năng của website này.

## Chức năng:
- Đăng kí và đăng nhập:
	+ Khi mỗi user tạo ra sẽ đồng thời được tạo ra 1 folder tương ứng với tại folder `user/[username]` chứa thông tin đăng nhập trong `.pass_hash` và 1 file `.acl` gồm những folder mà user sẽ có quyền truy cập (sẽ nói trong phần sau).
![User Folder](/assets/hitbpro/fs-folder.png)

- Những chức năng yêu cầu authentication:
1. Upload: Up 1 file lên server, sẽ lưu ở file trong folder `data/[username]`. 

2. Download: download file trên server tuy nhiên user **phải có quyền truy cập**(được lưu trong file `.acl` ở trên, mỗi dòng của file sẽ là quyền tương ứng được truy cập tới folder, file tương ứng). 

3. Share: Chia sẻ 1 folder cho user khác (**bug ở đây**)

- Ở đây mình loại bỏ k đề cập đến những chức năng mình k sử dụng để exploit trong bài. Mình nghĩ rằng tác giả có thể  có thêm 1 bug liên quan đến crypto, tuy nhiên đó ko phải sở trường của mình -,-
## Tìm lỗi:
### Nhận định:
- Sau khi đọc và dùng thử từng chức năng có trên trang web, mình có một số nghi vấn về quản lý truy cập trong bài này (thông qua `.acl`). Việc quản lý hoàn toàn bằng file, sử lý chuỗi sẽ dẫn đến khá nhiều hậu quả khi mình sẽ có thể chèn những kí tự `\n` để  thêm quyền đọc tùy ý.
![Access Control](/assets/hitbpro/fs-acl1.png)

- Phân tích thêm 1 đoạn về cách server nhận request từ người dùng, mình thấy khá lạ khi data truyền client-server là dạng json mà không sử dụng thư viện `json` của python mà thay vào đó là `ujson`.
![Access Control](/assets/hitbpro/ujson.png)

### Phân tích source:
1. **Endpoint `/share`:**
- Share 
- Nhận vào post request với json body, parse thành ShareRequest với 3 param:
![Access Control](/assets/hitbpro/fs-sq.png)
	- u: username muốn share quyền truy cập
	- l: folder, file hoặc đường dẫn muốn share
	- m: message (ko cần quan tâm)

- Kiểm tra truy cập:

![Access Control](/assets/hitbpro/fs-share.png)
![Access Control](/assets/hitbpro/fs-acl.png)
**NOTE**: Hàm commonpath sẽ trả về phần path chung của 2 path truyền vào. Hàm `is_phys_subpath()` sẽ kiểm tra xem cái path mình định share có là folder con của `data/curr_user` hay ko.
- Nếu có thì trả về hàm access url gọi tới endpoint `/access` với token được generate cùng data để vertify

2. **Endpoint `/access`:**
- Nhận token từ param, kiểm tra dat user và thêm quyền truy cập tới file `.acl` của user folder tương ứng. 
![Access Control](/assets/hitbpro/fs-aacl.png)

## Exploit:
### Ý tưởng:
- Do endpoint `/share` cho phép share quyền mà ko giới việc tự assign quyền cho chính user request và unicode encode để nhằm mục đích chèn thêm 1 dòng vào trong `.acl` file. Payload có dạng:
![Access Control](/assets/hitbpro/fs-shareapi.png)
- Hàm kiểm tra owner folder sẽ trả về folder data default của user `hoang`
- Khi qua endpoint `access`, đơn giản là file `user/hoang/.acl` sẽ được append thêm cái location trên và kết quả sẽ thành:

![Access Control](/assets/hitbpro/fs-result.png)

- Khi đến đây, chúng ta đã có thể thực hiện download từ mọi user khi ở dòng 65, điều kiện download sẽ luôn là true khi `allow_path=data/./` và path download sẽ luôn có cùng folder path là `data/`
![Access Control](/assets/hitbpro/fs-vld.png)

### Script:
- Mục tiêu là lấy toàn bộ Flag chứa trong file của những user khác với định dạng `[A-Z0-9]{31}=`. 
[Script](assets/hitbpro/fs.py){:target="_blank"}{:rel="noopener noreferrer"}

# **II.CAAS**
[caas.zip](https://transfer.sh/pxQcu2/caas.zip){:target="_blank"}{:rel="noopener noreferrer"}
- Đây là bài được release trong 6h cuối của cuộc thi, mình tự đánh giá đây là một chall khá ảo ma và hay ho =))).
- Khá là đen là mình không rõ tại sao mình k dựng lại được môi trường docker tuy nhiên mình sẽ viết lại cách mình và team đã tìm ra payload ảo ma này. Đầu tiên phải nói tới tools `forward traffic` được viết bởi Q5Ca, nhờ tools này team mình cx đã đỡ được kha khá cuộc attack khi có thể forward traffic sang team khác =)))). Đó là lý do team mình dù k solve được nhưng defence thì vẫn rất ok. 
- Nhờ việc forward traffic, team mình đã có thể "ăn cắp" payload của team khác và khi nhìn thấy payload của bài này, mình thực sự thấy phục team tìm ra :# 

## Chức năng:
- Server sử dụng gRPC, muốn tương tác chúng ta cũng phải tạo 1 client gRPC tương ứng. 

Phân tích qua file docker-compose, sẽ có 4 serviec được dựng lên:
1. App service: GRPC server
- Tạo user, lấy info user từ Posgresql, mỗi user tạo mới sẽ có 1 `token` (ID) đi kèm và chúng ta có thể lấy thông tin user từ `token` này. Các tính năng phần sau để trigger SSRF phần sau yêu cầu phải có `token` này 

![User RPC](/assets/hitbpro/caas/user.png)
Flag theo description là được bot truyền vào thông qua trường comment. 

![Description](/assets/hitbpro/caas/des.png)

=> Do vậy target của chúng ta là sẽ phải lấy DB. 

![Description](/assets/hitbpro/caas/curl.png)

- Tạo task (curl): Cho phép đẩy 1 bản ghi vào db với dạng `(token,url,state="PENDING")` để những worker (sẽ nói tiếp sau) xử lý. **Tuy nhiên**, URL ở đây đã bị filter bằng đoạn code sau, về cơ bản url sẽ không được phép gọi đến internal ip:
![Description](/assets/hitbpro/caas/filter.png)

2. Worker:
- Query liên tục những bản ghi từ table PENDING `task` để  rồi thực hiện câu lệnh curl với url trong db, lưu lại db kết quả vào bản ghi.

3. MINIO S3:
- Sử  dụng để chứa backup file db của user, được dựng trên network overlay của docker (internal ip).
- Theo phân tích thì có vẻ như đây sẽ là nơi SSRF đến để lấy backup data => extract ra flag.
## SSRF when curl and python not HOMOGENEOUS:
- Chúng ta sẽ đi ngược từ payload mình bắt được của các team khác. `http://s{@1.1.1.1/,3}`, thử dùng curl thêm options `-vvv` để debug ta sẽ rất bất ngờ :3 
![Debug](/assets/hitbpro/caas/debug1.png)

- Vậy có nghĩa nghĩa là với URL này, chúng ta đã có thể send 2 request với 2 URL khác nhau là `http://1.1.1.1` và `http://s3` ( Ảo ma thực sự :#). Đi vào debug thư viện từ source github của thư viện `curl`, mình mới biết rằng thư viện curl default support globbing url, mng có xem thêm ở đây: [https://everything.curl.dev/cmdline/globbing](https://everything.curl.dev/cmdline/globbing){:target="_blank"}{:rel="noopener noreferrer"}

![URL](/assets/payload/URL.png)
- Ảnh trên là cách 1 URL được parse theo tiêu chuẩn và default python sẽ parse như sau:
	- scheme: `http`
	- authority: `s{`
	- address: `1.1.1.1`
	- path: `/,3}`
- Còn với curl, như mình đã đề cập ở trên, URL sẽ request tới 2 url và cùng trả về trên cùng 1 response thông qua `stdout`. Vậy là việc SSRF đã có thể dễ dàng đến `http://s3:5000` để lấy file backup của DB và lấy flag. 

## Cách exploit:
- Do hiện tại mình không thể dựng lại docker nên mình sẽ chỉ nói về  luồng để viết script exploit lấy flag như sau:
	- Create 1 user để lấy token
	- Sử dụng token để tạo 1 task tới url `http://s{@1.1.1.1/,3}:9000/wal` => Lấy list bucket backup file
	- Tạo task tới url `http://s{@1.1.1.1/,3}:9000/wal/[file_name]` => decompress and get flag.

- Tuy nhiên, trong lúc thi, vì bài này lúc bắt được payload đã vào cuối giờ cũng như các team cũng patch gần hết nên team mình chỉ kiếm đc vài flag :3.
# **III.MP**

# **IV. Kết**
- Mình mong blog này sẽ chính là nơi chia sẻ kinh nghiệm, kiến thức và cũng đồng thời là nơi mình có thể lưu trữ, tra cứu trong những trường hợp cần thiết. Nếu có bất kì vấn đề, góp ý nào về đoạn write-up này, mng có thể liên hệ với mình theo thông tin bên dưới. Cảm ơn vì đã đọc!
from datetime import datetime
from functools import wraps
import jwt
from bson import ObjectId
from flask import Flask, redirect, request, render_template, url_for, jsonify, send_from_directory, session, make_response, message_flashed, flash
import pymongo
import datetime
from werkzeug.utils import secure_filename
from flask import Flask
import os
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired


app = Flask(__name__)

myClient = pymongo.MongoClient("mongodb://localhost:27017/")
mydatabasse = myClient["SharingBook"]
ConllectionUser = mydatabasse["USER"]
ConllectionAuthor = mydatabasse["AUTHOR"]
ConllectionBook = mydatabasse["BOOK"]
ConllectionCategory = mydatabasse["CATEGORY"]
ConllectionIdBookSave = mydatabasse["IDBOOKSAVE"]
ConllectionIdBookLike = mydatabasse["IDBOOKLIKE"]
ConllectionBorrowBook  = mydatabasse["BORROWBOOK"]
ConllectionRequest  = mydatabasse["REQUEST"]
ConllectionNotification  = mydatabasse["NOTIFICATION"]


app = Flask(__name__)
APP_ROUTE = os.path.dirname(os.path.abspath(__file__))
app.secret_key = 'QuangHai'
app.config['SECRET_KEY'] = 'HaiDaiCa'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'nguyenquanghai2331998@gmail.com'  # enter your email here
app.config['MAIL_DEFAULT_SENDER'] = 'infooveriq@gmail.com' # enter your email here
app.config['MAIL_PASSWORD'] = 'quanghai12' # enter your password here

#check mail
mail = Mail(app)
s = URLSafeTimedSerializer('Thisisasecret!')



def for_check_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if 'api_session_token' not in session:
            # If it isn't return our access denied message (you can also return a redirect or render_template)
            return jsonify("Access denied")

            # Otherwise just send them where they wanted to go
        return func(*args, **kwargs)

    return wrapped


@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('Login.html')
    else:
        return redirect(url_for('home'))

@app.route('/Login')
def Login():
    return render_template('Login.html')

@app.route('/home')
@for_check_token
def home():
    user_name = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(user_name)})
    image = ConllectionBook.find()
    return render_template('Home.html', user=user, image=image)


# API đăng nhập
@app.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = ConllectionUser.find_one({'username': request.form['username']})
        if user is None:
            flash("Sai tên tài khoản!", "warring")
            return redirect(request.url)
        else:
            if (user['password'] == request.form['password']):
                if (user['email_confirmed']==True):
                    session['logged_in'] = False
                    token = jwt.encode({'user': request.form['username'],
                                        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60)},
                                       app.config['SECRET_KEY'])
                    session['api_session_token'] = token
                    session["USERNAME"] = user["username"]
                    return render_template('Home.html', user=user)
                else:
                    flash("Tài khoản của bạn chưa được xác thực gmail", "success")
                    return redirect(request.url)
            else:
                flash("Sai mật khẩu!", "warring")
                return redirect(request.url)
    return render_template('Login.html')




# API Đăng ký
@app.route('/api/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = ConllectionUser.find_one({'username': request.form['username']})
        email_user = ConllectionUser.find_one({'email_user': request.form['email_user']})
        password = request.form['password']
        if email_user:
            flash("Email đã được sử dụng!", "warring")
            return redirect(request.url)
        if username:
            flash("Tên người dùng đã được sử dụng!", "warring")
            return redirect(request.url)

        if not len(password) >= 5:
            flash("Mật khẩu phải dài hơn 5 kí tự!", "warring")
            return redirect(request.url)
        else:
            taget = os.path.join(APP_ROUTE, 'Image/')  # Folder store image
            if not os.path.isdir(taget):  # TAO THU MUC MOI NEU NO KHONG TON TAI
                    os.mkdir(taget)
            for upload in request.files.getlist('url_user'):
                filename = secure_filename(upload.filename)
                destination = "/".join([taget, filename])
                ConllectionUser.insert({'hoten_user': (request.form['ho_user']+" "+request.form['ten_user']),
                                            'gioitinh_user': request.form['gioitinh_user'],
                                            'email_user': request.form['email_user'],
                                            'diachi_user': request.form['diachi_user'],
                                            'sdt_user': request.form['sdt_user'],
                                            'username': request.form['username'],
                                            'password': request.form['password'],
                                            'thongbao_user': 0,
                                            'url_user': filename,
                                            'email_confirmed': False})
                upload.save(destination)
                session['username'] = request.form['username']
                #check mail

                token = s.dumps(request.form['email_user'], salt='email-confirm')

                msg = Message('[BOOKING SHARE] Vui lòng xác nhận email',
                              sender='nguyenquanghai2331998@gmail.com',
                              recipients=[request.form['email_user']])

                confirm_url = url_for('confirm_email',
                                      token=token,
                                      _external=True)

                msg.html = render_template('active.html',
                                           confirm_url=confirm_url,
                                           username=request.form['username'],
                                           email=request.form['email_user'])

                mail.send(msg)

                flash("Ấn vào link xác nhận được gửi vào gmail của bạn ", "warring")
                return redirect(url_for('index'))
    return render_template('SignUp.html')



@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=86400)
    except SignatureExpired:
        flash("Đã quá thời gian xác nhận email ", "warring")
        return redirect(url_for('index'))
    user_emai = ConllectionUser.find_one({'email_user': str(email)})
    ConllectionUser.update_one({'_id': user_emai['_id']}, {"$set": {'email_confirmed': True}})
    flash("Xác thực gmail thành công", "warring")
    return redirect(url_for('index'))

# API đăng xuất
@app.route('/logout')
@for_check_token
def logout():
    session.clear()
    return redirect(url_for('index'))


# Hiển thị chi tiết thông tin user với ID được truyền tự động
@app.route('/api/user/detailuser', methods=['GET', 'POST'])
@for_check_token
def detailuser():
    username = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(username)})
    return render_template('Detail_User.html', user=user)


# Hiển thị chi tiết thông tin user với ID được truyền thủ công
@app.route('/api/user/detailuser/<string:post_id>', methods=['GET'])
@for_check_token
def DetailUser(post_id):
    if request.method == 'GET':
        user = ConllectionUser.find_one({'_id': ObjectId(post_id)})
        if user:
            return render_template('Detail_User.html', user=user, post_id=post_id)
        return 'Loi 404'



# Edit thoong tin user
@app.route('/api/user/edituser', methods=['GET', 'POST'])
@for_check_token
def updateUser():
    username = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(username)})

    if request.method == 'POST':
        id = user['_id']
        taget = os.path.join(APP_ROUTE, '')  # Folder store image
        if not os.path.isdir(taget):  # TAO THU MUC MOI NEU NO KHONG TON TAI
            os.mkdir(taget)
        for upload in request.files.getlist('anhuser'):
            filename = secure_filename(upload.filename)

            if filename == "":
                check_url = user['url_user']
            else:
                check_url = filename
            destination = "Image/".join([taget, check_url])
            ConllectionUser.update_one({'_id': ObjectId(id)}, {"$set": {'hoten_user': (request.form['ho_user']+" "+request.form['ten_user']),
                                                                        'gioitinh_user': request.form['gioitinh_user'],
                                                                        'email_user': request.form['email_user'],
                                                                        'diachi_user': request.form['diachi_user'],
                                                                        'sdt_user': request.form['sdt_user'],
                                                                        'url_user': check_url}}, upsert=True)
            upload.save(destination)
        return render_template('Edit_User.html', user=user)
    return render_template('Edit_User.html', user=user)


#Đổi Pass
@app.route('/api/user/editpass', methods=['GET', 'POST'])
@for_check_token
def update_password():
    username = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(username)})
    if request.method == 'POST':
        id = user['_id']
        if user['password'] == request.form['password_old']:#nhớ là form có pass old
            if request.form['password_new1'] == request.form['password_new2']:
                ConllectionUser.update_one({'_id': ObjectId(id)}, {"$set": {'password': request.form['password_new1']}}, upsert=True)
                return render_template('Detail_User.html', user=user)
            return '2 mat khau moi khong giong nhau'
        return 'Sai mat khau cu'
    return render_template('Change_Password.html', user=user)



# Thêm ID sách user đã lưu
@app.route('/api/user/addbooksave/<string:id_book>', methods=['GET', 'POST'])
@for_check_token
def addbooksave(id_book):
    user_name = session.get("USERNAME")
    listbooksave = []
    user = ConllectionUser.find_one({'username': str(user_name)})
    exiting = ConllectionBook.find_one({'_id': ObjectId(id_book)})
    user_save = ConllectionIdBookSave.find_one({'id_user': str(user['_id']),
                                                'id_book': str(id_book)})
    cursor = ConllectionIdBookSave.find({'id_user': str(user['_id'])})
    if not user_save:
        ConllectionIdBookSave.insert({'id_user': str(user['_id']),
                                      'id_book': str(id_book)})
        for iten in cursor:
            researchbook = ConllectionBook.find_one({'_id': ObjectId(iten['id_book'])})
            listbooksave.append(researchbook)
        return render_template('List_Book_Save.html', user=user, exiting=exiting, listbooksave=listbooksave)
    else:
        return 'Ma sach nay da luu truoc do'

#



# Hiển thị danh sách sách đã được user mượn
@app.route('/api/book/bookborrow/<int:pn>', methods=['GET'])
@for_check_token
def showbooksave(pn):
    skips = 8 * (pn - 1)
    cursor = []
    user_name = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(user_name)})
    bookborrow = ConllectionBorrowBook.find({'id_user': str(user['_id'])}).skip(skips).limit(8)
    count = ConllectionBorrowBook.find({'id_user': str(user['_id'])}).count()
    for item in bookborrow:
        book = ConllectionBook.find_one({'_id': ObjectId(item['id_book'])})
        cursor.append({'_id': book['_id'],'ten_sach': book['ten_sach'], 'ten_TG': book['ten_TG'], 'url_sach': book['url_sach']})
    return render_template('List_Book_Borrow.html', cursor=cursor, user=user, count=count)



#Thêm ID sách user đã thích
@app.route('/api/user/addbooklike/<string:id_book>', methods=['GET', 'POST'])
@for_check_token
def addbooklike(id_book):
    user_name = session.get("USERNAME")
    listbooklike = []
    user = ConllectionUser.find_one({'username': str(user_name)})
    exiting = ConllectionBook.find_one({'_id': ObjectId(id_book)})
    user_like = ConllectionIdBookLike.find_one({'id_user': str(user['_id']), 'id_book': str(id_book)})
    cursor = ConllectionIdBookLike.find({'id_user': str(user['_id'])})
    if not user_like:
        ConllectionIdBookLike.insert({'id_user': str(user['_id']), 'id_book': str(id_book)})
        upcountlikebook(id_book)
        upcountlikeauthor(exiting['ten_TG'])
        for iten in cursor:
            researchbook = ConllectionBook.find_one({'_id': ObjectId(iten['id_book'])})
            listbooklike.append(researchbook)
        return render_template('List_Book_Like.html', listbooklike=listbooklike, user=user)
    else:
        ConllectionIdBookLike.delete_one(user_like)
        downcountlikebook(id_book)
        downcountlikeauthor(exiting['ten_TG'])
        for iten in cursor:
            researchbook = ConllectionBook.find_one({'_id': ObjectId(iten['id_book'])})
            listbooklike.append(researchbook)
        return render_template('List_Book_Like.html', listbooklike=listbooklike, user=user)



#Check sach da thich chua
@app.route('/api/user/checkbooklike/<string:id_book>', methods=['GET', 'POST'])
@for_check_token
def checkbooklike(id_book):
    user_name = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(user_name)})
    exiting = ConllectionBook.find_one({'_id': ObjectId(id_book)})
    check_like = ConllectionIdBookLike.find_one({'id_user': str(user['_id']), 'id_book': str(id_book)})
    if check_like is None:
        return jsonify(True)
    else:
        return jsonify(False)
# Function up likes of book

def upcountlikebook(get_id):
    books = ConllectionBook.find_one({'_id': ObjectId(get_id)})
    if books:
        like = books['likes_sach']
        ConllectionBook.update_one({'_id': ObjectId(get_id)},
                                   {'$set': {'likes_sach': (like + 1)}})
    return 'Loi he thong'
#

# Function down likes of book

def downcountlikebook(get_id):
    books = ConllectionBook.find_one({'_id': ObjectId(get_id)})
    if books:
        like = books['likes_sach']
        ConllectionBook.update_one({'_id': ObjectId(get_id)},
                                   {'$set': {'likes_sach': (like - 1)}})
# Function up likes of book

def upcountlikeauthor(ten_tg):
    author = ConllectionAuthor.find_one({'ten_TG': str(ten_tg)})
    if author:
        like = author['likes_TG']
        ConllectionAuthor.update_one({'_id': ObjectId(author['_id'])},
                                     {'$set': {'likes_TG': (like + 1)}})

# Function down likes of book

def downcountlikeauthor(ten_tg):
    author = ConllectionAuthor.find_one({'ten_TG': str(ten_tg)})
    if author:
        like = author['likes_TG']
        ConllectionAuthor.update_one({'_id': ObjectId(author['_id'])},
                                     {'$set': {'likes_TG': (like - 1)}})
    return 'Loi he thong'


# Hiển thị danh sách user đã thích
@app.route('/api/book/booklike/<int:pn>')
@for_check_token
def showbooklike(pn):
    skips = 8 * (pn - 1)
    user_name = session.get("USERNAME")
    listbooklike = []
    user = ConllectionUser.find_one({'username': str(user_name)})
    booklikes = ConllectionIdBookLike.find({'id_user': str(user['_id'])}).skip(skips).limit(8)
    for item in booklikes:
        book = ConllectionBook.find_one({'_id': ObjectId(item['id_book'])})
        listbooklike.append({'_id': book['_id'], 'ten_sach': book['ten_sach'], 'ten_TG': book['ten_TG'], 'url_sach': book['url_sach']})
    return render_template('List_Book_Like.html', listbooklike=listbooklike, user=user)


#Thêm thông báo về cho user
def up_notification(id_user):
    user = ConllectionUser.find_one({'_id': ObjectId(id_user)})
    if user:
        thongbao = user['thongbao_user']
        ConllectionUser.update_one({'_id': ObjectId(user['_id'])},
                                   {'$set': {'thongbao_user': (thongbao+1)}})
    else:
        return 'Loi he thong'

#Xóa thông báo cho user
def delete_notification(id_user):
    user = ConllectionUser.find_one({'_id': ObjectId(id_user)})
    if user:
        thongbao = user['thongbao_user']
        ConllectionUser.update_one({'_id': ObjectId(user['_id'])},
                                   {'$set': {'thongbao_user': 0}})
    else:
        return 'Loi he thong'

#Danh sach thong bao trả về trang thông báo
@app.route('/api/user/notification', methods=['GET'])
def danhsachthongbao():
    global requestbook, usermuon
    user_name = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(user_name)})
    delete_notification(user['_id'])
    data = ConllectionRequest.find({'$or': [{'id_user': str(user['_id'])},
                                            {'id_usernsh': str(user['_id'])}]})
    ds = []
    for item in data:
        booker = ConllectionBook.find_one({'_id': ObjectId(item['id_book'])})
        user_nsh = ConllectionUser.find_one({'_id': ObjectId(item['id_usernsh'])})
        usermuon = ConllectionUser.find_one({'_id': ObjectId(item['id_user'])})
        ds.append({'id_borrowbook': item['_id'],
                   'hoten_usermuon': usermuon['hoten_user'],
                   # 'ten_sach': booker['ten_sach'],
                   'trangthai': item['trangthai'],
                   'hoten_nsh': user_nsh['hoten_user'],
                   'id_nsh': str(user_nsh['_id'])})
    return render_template('Notification.html', user=user, ds=ds)

#Danh sach thong bao trả về trang thông báo
@app.route('/api/user/notification', methods=['GET'])
def danhsachthongbaoall():
    global requestbook, usermuon
    user_name = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(user_name)})
    delete_notification(user['_id'])
    data = ConllectionRequest.find({'$or': [{'id_user': str(user['_id'])},
                                            {'id_usernsh': str(user['_id'])}]})
    ds = []
    for item in data:
        book = ConllectionBook.find_one({'_id': ObjectId(item['id_book'])})
        usermuon = ConllectionUser.find_one({'_id': ObjectId(item['id_user'])})
        user_nsh = ConllectionUser.find_one({'_id': ObjectId(book['id_nsh'])})
        ds.append({'id_borrowbook': item['_id'],
                   'hoten_usermuon': usermuon['hoten_user'],
                   'ten_sach': book['ten_sach'],
                   'trangthai': item['trangthai'],
                   'hoten_nsh': user_nsh['hoten_user'],
                   'id_nsh': str(user_nsh['_id'])})
    return render_template('Layout.html', user=user, ds=ds)




# Lấy danh sách quyển sách
@app.route('/api/book/showbook/<int:pn>', methods=['GET'])
@for_check_token
def skiplimitbook(pn):
    skips = 8 * (pn - 1)
    cursor = ConllectionBook.find().skip(skips).limit(8)
    user_name = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(user_name)})
    return render_template('List_Book.html', cursor=cursor, user=user)



# Add sách
@app.route('/api/book/addbook', methods=['GET', 'POST'])
@for_check_token
def Addbook():
    user_name = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(user_name)})
    if request.method == 'POST':
        exiting_book = ConllectionBook.find_one({'ten_sach': request.form['ten_sach'], 'ten_TG': request.form['ten_TG']})
        if exiting_book is None:
            # hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            taget = os.path.join(APP_ROUTE, 'Image/')  # Folder store image
            if not os.path.isdir(taget):  # TAO THU MUC MOI NEU NO KHONG TON TAI
                os.mkdir(taget)
            for upload in request.files.getlist('anhddsach'):
                filename = secure_filename(upload.filename)
                destination = "/".join([taget, filename])
                upload.save(destination)
                ConllectionBook.insert_one({'ten_sach': request.form['ten_sach'],
                                        'ten_TG': request.form['ten_TG'],
                                        'ten_TL': request.form['ten_TL'],
                                        'likes_sach': 0,
                                        'mota_sach': request.form['mota_sach'],
                                        'soluong': int(request.form['soluong']),
                                        'id_nsh': str(user['_id']),
                                        'url_sach': filename})
                flash("Thêm sách thành công !")
                return redirect(request.url)
        else:
            flash(" Thêm sách thất bại! Sách đã tồn tại !")
            return redirect(request.url)
    return render_template('Add_Book.html', user=user)


# EDIT BOOK
@app.route('/api/book/editbook/<string:post_id>', methods=['PUT'])
@for_check_token
def updateSach(post_id):
    if request.method == 'POST':
        exiting = ConllectionBook.find_one({'_id': ObjectId(post_id)})
        if exiting is None:
            return 'Không tồn tại ID sách'
        else:
            taget = os.path.join(APP_ROUTE, 'Image/')  # Folder store image
            if not os.path.isdir(taget):  # TAO THU MUC MOI NEU NO KHONG TON TAI
                os.mkdir(taget)
            for upload in request.files.getlist('anhddsach'):
                filename = secure_filename(upload.filename)
                destination = "/".join([taget, filename])
                ConllectionBook.update_one(
                    {'ma_sach': request.form['masach']}, {
                        '$set': {'ten_sach': request.form['tensach'],
                                 'ten_TG': request.form['tentacgia'],
                                 'ten_TL': request.form['tentheloai'],
                                 'likes_sach': int(request.form['likesach']),
                                 'mota_sach': request.form['mota'],
                                 'url_sach': 'Image/' + filename}})
                upload.save(destination)
                return 'Sua thanh cong'
    return render_template('Update_Book.html')


# Lấy sách bằng id
@app.route('/api/book/detailbook/<string:id>', methods=['GET'])
def getbookbyid(id):
    global user
    exiting = ConllectionBook.find_one({'_id': ObjectId(id)})
    tem = exiting['id_nsh']
    owner = ConllectionUser.find_one({'_id': ObjectId(tem)})
    if exiting:
        username = session.get("USERNAME")
        user = ConllectionUser.find_one({'username': str(username)})

    return render_template('Book_Detail.html', exiting=exiting, user=user, owner=owner)


# Lấy sách bằng Category
@app.route('/api/book/showbook/<string:ten_tl>/<int:pn>', methods=['GET'])
@for_check_token
def skiplimitbook2(ten_tl, pn):
    skips = 4 * (pn - 1)
    cursor = ConllectionBook.find({'ten_TL': str(ten_tl)}).skip(skips).limit(4)
    user_name = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(user_name)})
    return render_template('List_Book.html', cursor=cursor, user=user)


# Lấy sách bằng Author
@app.route('/api/book/showbook/<string:ten_tg>/<int:pn>', methods=['GET'])
@for_check_token
def skiplimitbook3(ten_tg, pn):
    skips = 4 * (pn - 1)
    cursor = ConllectionBook.find({'ten_TG': str(ten_tg)}).skip(skips).limit(4)
    user_name = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(user_name)})
    return render_template('List_Book_By_Autho.html', cursor=cursor, user=user, ten_tg=ten_tg)


# SEARCH BOOK THEO TEN SACH
@app.route('/api/book/searchbook', methods=['POST'])
@for_check_token
def searchnamebook():
    ds = []
    username = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(username)})
    exiting = ConllectionBook.find({'ten_sach': {'$regex': request.form['searchnamebook']}})
    count = exiting.count()
    for item in exiting:

        ds.append({'_id': item['_id'], 'ten_sach': item['ten_sach'], 'ten_TG': item['ten_TG'], 'url_sach': item['url_sach']})
    return render_template('Search_Book.html', count=count, ds=ds, user=user)



# Mượn sách
@app.route('/api/book/borrow/<string:id_sach>', methods=['GET', 'POST'])
@for_check_token
def insertRequestBook(id_sach):
    user_name = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(user_name)})
    exiting = ConllectionBook.find_one({'_id': ObjectId(id_sach)})
    owner = ConllectionUser.find_one({'_id': ObjectId(exiting['id_nsh'])})
    if request.method == 'POST':
        check_request = ConllectionRequest.find_one({'id_book': str(id_sach),
                                                     'id_user': str(user['_id'])})
        if check_request is None :
            ConllectionRequest.insert_one({'id_book': str(id_sach),
                                       'id_user': str(user['_id']),
                                       'id_usernsh': str(exiting['id_nsh']),
                                       'ghichu_request': request.form['ghichu_request'],
                                       'ngaymuon': request.form['ngaymuon'],
                                       'trangthai': 0
                                       })
            up_notification(owner['_id'])
            return render_template('Book_Detail.html', user=user, exiting=exiting, owner=owner)
        if check_request['trangthai'] == 2:
            ConllectionRequest.update_one({'$and':[ {'id_book': str(exiting['_id'])},
                                                    {'id_user': str(user['_id'])}]},
                                                    {'$set': {'trangthai': 0}})
        else:
            return 'Dang gui yeu cau'
            #return render_template('Form_Borrow_Book.html', user=user, exiting=exiting)
    return render_template('Form_Borrow_Book.html', user=user, exiting=exiting, owner=owner)



#Chi tiet phieu muon sach
@app.route('/api/user/detailbookborrow/<string:id_borrow>', methods=['GET',  'POST'])
def confirmbookborrow(id_borrow):
    user_name = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(user_name)})
    requestbook = ConllectionRequest.find_one({'_id': ObjectId(id_borrow)})
    usermuon = ConllectionUser.find_one({'_id': ObjectId(requestbook['id_user'])})
    book = ConllectionBook.find_one({'_id': ObjectId(requestbook['id_book'])})
    id = book['_id']
    if request.method == 'POST':
        check = ConllectionBorrowBook.find_one({'id_user': str(usermuon['_id']), 'id_book': str(book['_id'])})
        if check is None:
            ConllectionBook.update_one({'_id': ObjectId(id)}, {"$set": {'soluong': (book['soluong']-1)}}, upsert=True)
            ConllectionRequest.update_one({'_id': ObjectId(id_borrow)}, {'$set': {'trangthai': 1}})
            ConllectionBorrowBook.insert_one({'id_user': str(usermuon['_id']), 'id_book': str(book['_id'])})
            up_notification(usermuon['_id'])
            data = ConllectionRequest.find({'$or': [{'id_user': str(user['_id'])},
                                                    {'id_usernsh': str(user['_id'])}]})
            ds = []
            for item in data:
                book = ConllectionBook.find_one({'_id': ObjectId(item['id_book'])})
                usermuon = ConllectionUser.find_one({'_id': ObjectId(item['id_user'])})
                user_nsh = ConllectionUser.find_one({'_id': ObjectId(book['id_nsh'])})
                ds.append({'id_borrowbook': item['_id'],
                           'hoten_usermuon': usermuon['hoten_user'],
                           'ten_sach': book['ten_sach'],
                           'trangthai': item['trangthai'],
                           'hoten_nsh': user_nsh['hoten_user'],
                           'id_nsh': str(user_nsh['_id'])})
            return render_template('Notification.html', user=user, ds=ds)
        else:
            return jsonify(False)
    return render_template('Form_Confirm_Borrow_Book.html', usermuon=usermuon, book=book, requestbook=requestbook, user=user)



#Không đồng ý cho mượn sách
@app.route('/api/user/rejectrequest/<string:id_borrow>', methods=['GET',  'POST'])
def rejectrequest(id_borrow):
    user_name = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(user_name)})
    requestbook = ConllectionRequest.find_one({'_id': ObjectId(id_borrow)})
    usermuon = ConllectionUser.find_one({'_id': ObjectId(requestbook['id_user'])})
    book = ConllectionBook.find_one({'_id': ObjectId(requestbook['id_book'])})
    check = ConllectionBorrowBook.find_one({'id_user': str(usermuon['_id']),
                                            'id_book': str(book['_id'])})
    if check is None:
        ConllectionRequest.update_one({'_id': ObjectId(id_borrow)},
                                      {'$set': {'trangthai': 2}})
        up_notification(usermuon['_id'])
        data = ConllectionRequest.find({'$or': [{'id_user': str(user['_id'])},
                                                {'id_usernsh': str(user['_id'])}]})
        ds = []
        for item in data:
            book = ConllectionBook.find_one({'_id': ObjectId(item['id_book'])})
            usermuon = ConllectionUser.find_one({'_id': ObjectId(item['id_user'])})
            user_nsh = ConllectionUser.find_one({'_id': ObjectId(book['id_nsh'])})
            ds.append({'id_borrowbook': item['_id'],
                        'hoten_usermuon': usermuon['hoten_user'],
                        'ten_sach': book['ten_sach'],
                        'trangthai': item['trangthai'],
                        'hoten_nsh': user_nsh['hoten_user'],
                        'id_nsh': str(user_nsh['_id'])})
        return render_template('Notification.html', user=user, ds=ds)

@app.route('/api/user/savenotification/<string:id_book>', methods=['GET',  'POST'])
def guittcancer(id_book):
    user_name = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(user_name)})
    exiting = ConllectionBook.find_one({'_id': ObjectId(id_book)})
    owner = ConllectionUser.find_one({'_id': ObjectId(exiting['id_nsh'])})
    ds = []
    if request.method == 'POST':
        ConllectionNotification.insert({'id_book': str(id_book),
                                        'id_user': str(user['_id']),
                                        'ghichu_request': request.form['lido']
                                        })
        up_notification(owner['_id'])
        data = ConllectionBook.find({'id_nsh': str(user['_id'])})

        for item in data:
            requestbook = ConllectionRequest.find({'id_book': str(item['_id'])})
            for iten in requestbook:
                usermuon = ConllectionUser.find_one({'_id': ObjectId(iten['id_user'])})
                objectborrow = ConllectionRequest.find_one(
                    {'id_book': str(item['_id']), 'id_user': str(usermuon['_id'])})
                ds.append({'id_borrowbook': objectborrow['_id'], 'hoten_usermuon': usermuon['hoten_user'],
                           'ten_sach': item['ten_sach']})
        return render_template('Notification.html', user=user, ds=ds)
    return render_template('Notification.html', user=user, ds=ds)





#check muon sach chua
@app.route('/api/user/checkbookborrow/<string:id_book>/<string:id_user>', methods=['GET'])
def checkbookborrow(id_book, id_user):
    checkborow = ConllectionBorrowBook.find_one({'id_user': str(id_user), 'id_book': str(id_book)})
    checkrequest = ConllectionRequest.find_one({'id_user': str(id_user), 'id_book': str(id_book)})
    user_name = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(user_name)})
    book = ConllectionBook.find_one({'_id': ObjectId(id_book)})
    if user['_id'] == ObjectId(book['id_nsh']):
        return jsonify(1)
    if book['soluong'] <= 0:
        return jsonify(2)
    else:
        if checkborow is None:
            if checkrequest is None:
                return jsonify(True)
            else:
                if checkrequest['trangthai'] == 2:
                    return jsonify(True)
                return jsonify(False)
        else:
            return jsonify(0)




# # SEARCH BOOK THEO TEN THE LOAI
# @app.route('/api/category/searchbook', methods=['POST'])
# @for_check_token
# def searchcategory():
#     if request.method == 'POST':
#         data_sach = []
#         searchid = ConllectionCategory.find_one({'ten_TL': request.form['searchnamecategory']})
#         if searchid:
#             data_sach.append(
#                 {"ma sach": searchid['ma_sach'], "ten sach": searchid['ten_sach'], "ten tac gia": searchid['ten_TG'],
#                  "ten the loai": searchid['ten_TL'],
#                  "likesach": int(searchid['likes_sach']),
#                  "mota": searchid['mota_sach'],
#                  "url": searchid['url_sach']})
#             return jsonify(data_sach)
#         return 'Khong tim thay ten the loai'
#     return redirect(url_for('showbook'))





# Lấy danh sách tác giả
@app.route('/api/author/showauthor/<int:pn>', methods=['GET'])
@for_check_token
def showauthor(pn):
    skips = 8 * (pn - 1)
    cursor = ConllectionAuthor.find().skip(skips).limit(8)
    username = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(username)})
    return render_template('List_Author.html', cursor1=cursor, user=user)


# Hiển thị chi tiết tác giả
@app.route('/api/author/detailauthor/<string:post_id>', methods=['GET'])
@for_check_token
def DetailAuthor(post_id):
    global urlauthor
    username = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(username)})
    author = ConllectionAuthor.find_one({'_id': ObjectId(post_id)})
    cursor = ConllectionBook.find({'ten_TG': author['ten_TG']}).limit(4)
    return render_template('Detail_Author.html', author=author, user=user, cursor=cursor)


# Lay tac gia theo ten
@app.route('/api/author/detailauthorname/<string:ten_tg>', methods=['GET'])
def DetailUserhihi(ten_tg):
    global urlauthor, author, user
    if request.method == 'GET':
        username = session.get("USERNAME")
        user = ConllectionUser.find_one({'username': str(username)})
        author = ConllectionAuthor.find_one({'ten_TG': str(ten_tg)})
        cursor = ConllectionBook.find({'ten_TG': author['ten_TG']}).limit(4)
        if author:
            urlauthor = "/api/image/" + author['url_TG']
    return render_template('Detail_Author.html', urlauthor=urlauthor, author=author, user=user, cursor=cursor)


# ADD AUTHOR
@app.route('/api/author/addauthor', methods=['GET', 'POST'])
@for_check_token
def Addauthor():
    if request.method == 'POST':
        exiting_author = ConllectionAuthor.find_one({'ma_TG': request.form['ma_tg']})
        if exiting_author is None:
            # hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())

            taget = os.path.join(APP_ROUTE, 'Image/')  # Folder store image
            if not os.path.isdir(taget):  # TAO THU MUC MOI NEU NO KHONG TON TAI
                os.mkdir(taget)
            for upload in request.files.getlist('url_tg'):
                filename = secure_filename(upload.filename)
                destination = "/".join([taget, filename])
                ConllectionAuthor.insert({'ma_TG': request.form['ma_tg'], 'ten_TG': request.form['ten_tg'],
                                          'diachi_TG': request.form['diachi_tg'], 'likes_TG': request.form['likes_tg'],
                                          'mota_TG': request.form['mota_tg'], 'url_TG': filename})
                upload.save(destination)
                return 'Add Success!'
        return 'Ma tac gia da co!'
    return render_template('Add_Author.html')


# EDIT AUTHOR
@app.route('/api/author/editauthor/<string:post_id>', methods=['POST'])
@for_check_token
def updateAuthor(post_id):
    if request.method == 'POST':
        exiting = ConllectionAuthor.find_one({'_id': ObjectId(post_id)})
        if exiting is None:
            return 'Không tồn tại ID tác giả'
        else:
            taget = os.path.join(APP_ROUTE, 'Image/')  # Folder store image
            if not os.path.isdir(taget):  # TAO THU MUC MOI NEU NO KHONG TON TAI
                os.mkdir(taget)
            for upload in request.files.getlist('anhddtacgia'):
                filename = secure_filename(upload.filename)
                destination = "/".join([taget, filename])
                ConllectionBook.update_one(
                    {'ma_TG': request.form['ma_TG']}, {
                        '$set': {'ten_TG': request.form['ten_tg'], 'diachi_TG': request.form['diachi_tg'],
                                 'likes_TG': int(request.form['likes_tg']), 'mota_tg': request.form['mota_tg'],
                                 'mota': request.form['mota'], 'url_TG': 'Image/' + filename}})
                upload.save(destination)
                return 'Sua thanh cong'
    return render_template('Update.html')


# API hiển thị ảnh
@app.route('/api/image/<path:path>')
def showphoto(path):
    return send_from_directory('Image', path)


# Lấy danh sách thể loại
@app.route('/api/category/showcategory/<int:pn>', methods=['GET'])
@for_check_token
def skiplimit(pn):
    skips = 4 * (pn - 1)
    data = []
    cursor = ConllectionCategory.find().skip(skips).limit(4)
    username = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(username)})
    for item in cursor:
        count = ConllectionBook.count_documents({'ten_TL': item['ten_TL']})
        ten = item['ten_TL']
        anh = item['url_TL']
        data.append({'ten': ten, 'soluong': count, 'url_TL': anh})
    return render_template('List_Category.html', data=data, user=user)


# SEARCH BOOK THEO TEN THE LOAI VỚI TÊN ĐƯỢC TRUYỀN VÀO TỰ ĐỘNG
@app.route('/api/category/getcategorybook/<string:tentheloai>')
@for_check_token
def searchcategoryauto(tentheloai):
    data_sach = []
    searchid = ConllectionBook.find({'ten_TL': tentheloai})
    if searchid:
        for acc in searchid:
            data_sach.append({"ma sach": acc['ma_sach'], "ten sach": acc['ten_sach'], "ten tac gia": acc['ten_TG'],
                              "ten the loai": acc['ten_TL'],
                              "likesach": int(acc['likes_sach']),
                              "mota": acc['mota_sach'],
                              "url": acc['url_sach']})
        return jsonify(data_sach)
    return 'Loi roi'
#Liên hệ
@app.route('/api/bookborrow/contact/<string:id_book>')
@for_check_token
def contact(id_book):
    username = session.get("USERNAME")
    user = ConllectionUser.find_one({'username': str(username)})
    exiting = ConllectionBook.find_one({'_id': ObjectId(id_book)})
    id_nsh = exiting['id_nsh']
    nsh = ConllectionUser.find_one({'_id': ObjectId(id_nsh)})
    return render_template('Lienhe.html', nsh=nsh, user=user, exiting=exiting)






# @app.route('/api/bookborrow/contact/send_email/<string:id_nsh>/<string:id_book>')
# @for_check_token
# def send_email(id_nsh, id_book):
#     username = session.get("USERNAME")
#     user = ConllectionUser.find_one({'username': str(username)})
#     nsh = ConllectionUser.find_one({'_id': ObjectId(id_nsh)})
#     exiting = ConllectionBook.find_one({'_id': ObjectId(id_book)})
#     with app.app_context():
#         msg = Message(subject="Tin nhắn",
#                       sender=app.config.get(user['email_user']),
#                       recipients=[nsh['email_user']], # replace with your email for testing
#                       body=request.form['message'])
#         mail.send(msg)
#         flash("Gửi tin nhắn thành công! ", "success")
#         return render_template('Lienhe.html', nsh=nsh, user=user, exiting=exiting)


if __name__ == '__main__':
    app.run(host='localhost', port=5002, debug=True)

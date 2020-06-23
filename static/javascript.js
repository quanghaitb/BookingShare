function check_field_signup() {
            var ho_user = document.forms["register"]["ho_user"].value;
            var ten_user = document.forms["register"]["ten_user"].value;
            var gioitinh_user = document.forms["register"]["gioitinh_user"].value;
            var email_user = document.forms["register"]["email_user"].value;
            var diachi_user = document.forms["register"]["diachi_user"].value;
            var sdt_user = document.forms["register"]["sdt_user"].value;
            var username = document.forms["register"]["username"].value;
            var password = document.forms["register"]["password"].value;
            if (ho_user=="" ||ten_user=="" || gioitinh_user=="" || email_user=="" || diachi_user=="" || sdt_user==""|| username==""|| password=="")
            {
                alert("Field Emmpty");
                return false;
            }
        }
function check_field_signin() {
            var hoten_user = document.forms["register"]["hoten_user"].value;
            var gioitinh_user = document.forms["register"]["gioitinh_user"].value;
            var email_user = document.forms["register"]["email_user"].value;
            var diachi_user = document.forms["register"]["diachi_user"].value;
            var sdt_user = document.forms["register"]["sdt_user"].value;
            var username = document.forms["register"]["username"].value;
            var password = document.forms["register"]["password"].value;
            if (hoten_user=="" || gioitinh_user=="" || email_user=="" || diachi_user=="" || sdt_user==""|| username==""|| password=="")
            {
                alert("Không được để trống!");
                return false;
            }
        }
// $(document).ready(function(){
//         if({{ post_id === user['_id']}})
//         {
//             $(".edit_user").show();
//         }
//         else {
//             $(".edit_user").hide();
//         }
//         function back() {
//             window.back();
//         }
//     });
function check_field_edituser() {
            var ho_user = document.forms["edituser"]["ho_user"].value;
            var ten_user = document.forms["edituser"]["ten_user"].value;
            var email_user = document.forms["edituser"]["email_user"].value;
            var address_user = document.forms["edituser"]["diachi_user"].value;
            var phone_user = document.forms["edituser"]["sdt_user"].value;
            if (ho_user=="" || ten_user=="" || email_user=="" || address_user=="" || phone_user=="" )
            {
                alert("Không được để trống!");
                return false;
            }

        }
function check_field_password() {
            var password_old = document.forms["password"]["password_old"].value;
            var password_new1 = document.forms["password"]["password_new1"].value;
            var password_new2 = document.forms["password"]["password_new2"].value;
            if (password_old =="" || password_new1=="" || password_new2=="")
            {
                alert("Không được để trống!");
                return false;
            }
        }
function goBack() {
  window.history.back();
}
function showimagepreview(input)
    {
     if (input.files && input.files[0])
     {
     var filerdr = new FileReader();
     filerdr.onload = function(e) {
      $('#imgDisplayarea').attr('src', e.target.result);
     };
     filerdr.readAsDataURL(input.files[0]);
     }
    }
function check_field_addbook() {
            var ten_sach = document.forms["addbook"]["ten_sach"].value;
            var ten_TG = document.forms["addbook"]["ten_TG"].value;
            var ten_TL = document.forms["addbook"]["ten_TL"].value;
             var soluong = document.forms["addbook"]["soluong"].value;
            if ( ten_sach=="" || ten_TG =="" || ten_TL =="" )
            {
                alert("Không được để trống!");
                return false;
            }
            if (soluong<1){
                alert("Số lượng phải lớn hơn 0");
                return false;
            }
        }

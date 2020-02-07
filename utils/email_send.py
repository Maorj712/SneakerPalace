from users.models import EmailVerifyRecord
from SneakerPalace.settings import EMAIL_FROM
from django.core.mail import send_mail

import random


def gen_random_code(code_length=4):
    code = ''
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    length = len(chars) - 1
    for i in range(code_length):
        code += chars[random.randint(0, length)]
    return code


def send_register_email(email, send_type="register"):
    email_record = EmailVerifyRecord()
    code = gen_random_code()
    email_record.email = email
    email_record.code = code
    email_record.send_type = send_type
    email_record.save()

    email_title = ""
    email_body = ""

    if send_type == "register":
        email_title = "鞋宫注册激活链接"
        email_body = "请点击下面的链接激活您的帐号: http://127.0.0.1:8000/active/{0}".format(code)

        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == "forget":
        email_title = "鞋宫找回密码链接"
        email_body = "请点击下面的链接找回您的密码: http://127.0.0.1:8000/reset/{0}".format(code)

        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass


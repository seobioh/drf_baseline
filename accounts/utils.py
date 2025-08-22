# accounts/utils.py
app_name = 'accounts'

import time
import json
import hmac
import base64
import string
import random
import hashlib
import secrets
import requests
import urllib.parse

from datetime import datetime
from Crypto.Cipher import AES

# Password Generator
# <-------------------------------------------------------------------------------------------------------------------------------->
def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"

    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


# Mobile Generator
# <-------------------------------------------------------------------------------------------------------------------------------->
def generate_random_mobile():
    prefix = "010"
    middle = ''.join(secrets.choice(string.digits) for _ in range(4))
    suffix = ''.join(secrets.choice(string.digits) for _ in range(4))
    
    return f"{prefix}{middle}{suffix}"


# Response Objects
# <-------------------------------------------------------------------------------------------------------------------------------->
class NaverResponse:
    def __init__(self, data):
        self.data = data
        self.response = data.get('response', {})
    
    @property
    def id(self):
        return self.response.get('id')
    
    @property
    def email(self):
        return self.response.get('email')
    
    @property
    def mobile(self):
        mobile = self.response.get('mobile')
        if mobile:
            mobile = mobile.replace('-', '')
        return mobile if mobile else None
    
    @property
    def name(self):
        return self.response.get('name')
    
    @property
    def nickname(self):
        return self.response.get('nickname')
    
    @property
    def profile_image(self):
        return self.response.get('profile_image')
    
    @property
    def age(self):
        return self.response.get('age')
    
    @property
    def gender(self):
        return self.response.get('gender')
    
    @property
    def birthday(self):
        return self.response.get('birthday')
    
    @property
    def birthyear(self):
        return self.response.get('birthyear')
    
    @property
    def resultcode(self):
        return self.data.get('resultcode')
    
    @property
    def message(self):
        return self.data.get('message')
    
    @property
    def is_valid(self):
        return bool(self.id and self.email and self.resultcode == '00' and self.name)
    
    def to_user_data(self):
        return {
            'provider': 'naver',
            'provider_user_id': self.id,
            'email': self.email,
            'name': self.name,
            'mobile': self.mobile,
            'password': generate_random_password(),
        }
    
    def debug_print(self):
        return f"NaverResponse(id={self.id}, email={self.email}, name={self.name}, mobile={self.mobile})"
    
    @classmethod
    def create_from_code(cls, code, state, naver_client_id, naver_client_secret):
        # 1. 인증 코드로 액세스 토큰 요청
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': naver_client_id,
            'client_secret': naver_client_secret,
            'code': code,
            'state': state
        }
        
        token_response = requests.post("https://nid.naver.com/oauth2.0/token", data=token_data)
        token_response_json = token_response.json()
        
        # 2. 토큰 요청 에러 처리
        error = token_response_json.get("error")
        if error:
            error_description = token_response_json.get("error_description", "An error occurred during token acquisition.")
            raise ValueError(f"Token request failed: {error} - {error_description}")
        
        # 3. 액세스 토큰 추출
        naver_access_token = token_response_json.get("access_token")
        if not naver_access_token:
            raise ValueError("Missing naver_access_token")
        
        # 4. 네이버 프로필 정보 요청
        profile_response = requests.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {naver_access_token}"}
        )
        
        if profile_response.status_code != 200:
            raise ValueError("Failed to get profile from Naver")
        
        # 5. NaverResponse 객체 생성
        profile_data = profile_response.json()
        naver_response = cls(profile_data)
        
        if not naver_response.is_valid:
            raise ValueError("Invalid response from Naver")
        
        return naver_response


class GoogleResponse:
    def __init__(self, data):
        self.data = data
    
    @property
    def id(self):
        return self.data.get('id')
    
    @property
    def email(self):
        return self.data.get('email')
    
    @property
    def name(self):
        return self.data.get('name')
    
    @property
    def given_name(self):
        return self.data.get('given_name')
    
    @property
    def family_name(self):
        return self.data.get('family_name')
    
    @property
    def picture(self):
        return self.data.get('picture')
    
    @property
    def locale(self):
        return self.data.get('locale')
    
    @property
    def verified_email(self):
        return self.data.get('verified_email')
    
    @property
    def hd(self):
        return self.data.get('hd')
    
    @property
    def is_valid(self):
        return bool(self.id and self.email and self.name)
    
    def to_user_data(self):
        return {
            'provider': 'google',
            'provider_user_id': self.id,
            'email': self.email,
            'name': self.name,
            'password': generate_random_password(),
        }
    
    def debug_print(self):
        return f"GoogleResponse(id={self.id}, email={self.email}, name={self.name}, verified={self.verified_email})"
    
    @classmethod
    def create_from_code(cls, code, google_client_key, google_client_secret, google_callback_uri):
        # 1. URL 디코딩
        decoded_code = urllib.parse.unquote(code)
        
        # 2. 인증 코드로 액세스 토큰 요청
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': google_client_key,
            'client_secret': google_client_secret,
            'redirect_uri': google_callback_uri,
            'code': decoded_code
        }
        
        token_response = requests.post("https://oauth2.googleapis.com/token", data=token_data)
        token_response_json = token_response.json()
        
        # 3. 토큰 요청 에러 처리
        error = token_response_json.get("error")
        if error:
            error_description = token_response_json.get("error_description", "An error occurred during token acquisition.")
            raise ValueError(f"Token request failed: {error} - {error_description}")
        
        # 4. 액세스 토큰 추출
        google_access_token = token_response_json.get("access_token")
        if not google_access_token:
            raise ValueError("Missing google_access_token")
        
        # 5. 구글 프로필 정보 요청
        profile_response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", 
            headers={"Authorization": f"Bearer {google_access_token}"}
        )
        
        if profile_response.status_code != 200:
            raise ValueError("Failed to get profile from Google")
        
        # 6. GoogleResponse 객체 생성
        profile_data = profile_response.json()
        google_response = cls(profile_data)
        
        if not google_response.is_valid:
            raise ValueError("Invalid response from Google")
        
        return google_response


class KakaoResponse:
    def __init__(self, data):
        self.data = data
        self.kakao_account = data.get('kakao_account', {})
        self._properties = data.get('properties', {})
    
    @property
    def id(self):
        return self.data.get('id')
    
    @property
    def email(self):
        return self.kakao_account.get('email')
    
    @property
    def mobile(self):
        phone_number = self.kakao_account.get('phone_number')
        if phone_number:
            phone_number = phone_number.replace('+82 ', '0').replace('-', '')
        return phone_number if phone_number else None
    
    @property
    def name(self):
        return self.kakao_account.get('name')
    
    @property
    def nickname(self):
        return self.properties.get('nickname')
    
    @property
    def profile_image(self):
        return self.properties.get('profile_image')
    
    @property
    def thumbnail_image(self):
        return self.properties.get('thumbnail_image')
    
    @property
    def gender(self):
        return self.kakao_account.get('gender')
    
    @property
    def birthday(self):
        return self.kakao_account.get('birthday')
    
    @property
    def birthyear(self):
        return self.kakao_account.get('birthyear')
    
    @property
    def age_range(self):
        return self.kakao_account.get('age_range')
    
    @property
    def ci(self):
        return self.kakao_account.get('ci')
    
    @property
    def ci_authenticated_at(self):
        return self.kakao_account.get('ci_authenticated_at')
    
    @property
    def birthday_type(self):
        return self.kakao_account.get('birthday_type')
    
    @property
    def is_leap_month(self):
        return self.kakao_account.get('is_leap_month')
    
    @property
    def has_signed_up(self):
        return self.data.get('has_signed_up')
    
    @property
    def connected_at(self):
        return self.data.get('connected_at')
    
    @property
    def synched_at(self):
        return self.data.get('synched_at')
    
    @property
    def properties(self):
        return self._properties
    
    @property
    def for_partner(self):
        return self.data.get('for_partner', {})
    
    @property
    def profile_needs_agreement(self):
        return self.kakao_account.get('profile_needs_agreement')
    
    @property
    def profile_nickname_needs_agreement(self):
        return self.kakao_account.get('profile_nickname_needs_agreement')
    
    @property
    def profile_image_needs_agreement(self):
        return self.kakao_account.get('profile_image_needs_agreement')
    
    @property
    def name_needs_agreement(self):
        return self.kakao_account.get('name_needs_agreement')
    
    @property
    def email_needs_agreement(self):
        return self.kakao_account.get('email_needs_agreement')
    
    @property
    def age_range_needs_agreement(self):
        return self.kakao_account.get('age_range_needs_agreement')
    
    @property
    def birthyear_needs_agreement(self):
        return self.kakao_account.get('birthyear_needs_agreement')
    
    @property
    def birthday_needs_agreement(self):
        return self.kakao_account.get('birthday_needs_agreement')
    
    @property
    def gender_needs_agreement(self):
        return self.kakao_account.get('gender_needs_agreement')
    
    @property
    def phone_number_needs_agreement(self):
        return self.kakao_account.get('phone_number_needs_agreement')
    
    @property
    def ci_needs_agreement(self):
        return self.kakao_account.get('ci_needs_agreement')
    
    @property
    def is_email_valid(self):
        return self.kakao_account.get('is_email_valid')
    
    @property
    def is_email_verified(self):
        return self.kakao_account.get('is_email_verified')
    
    @property
    def is_valid(self):
        return bool(self.id and self.email and self.name)
    
    def to_user_data(self):
        return {
            'provider': 'kakao',
            'provider_user_id': self.id,
            'email': self.email,
            'mobile': self.mobile,
            'name': self.name,
            'password': generate_random_password(),
        }
    
    def debug_print(self):
        return f"KakaoResponse(id={self.id}, email={self.email}, name={self.name}, mobile={self.mobile}, ci={self.ci})"
    
    @classmethod
    def create_from_code(cls, code, kakao_client_key, kakao_callback_uri):
        # 1. 인증 코드로 액세스 토큰 요청
        token_url = "https://kauth.kakao.com/oauth/token"
        token_params = {
            'grant_type': 'authorization_code',
            'client_id': kakao_client_key,
            'redirect_uri': kakao_callback_uri,
            'code': code
        }
        
        token_response = requests.get(token_url, params=token_params)
        token_data = token_response.json()
        
        # 2. 토큰 요청 에러 처리
        error = token_data.get("error")
        if error:
            error_description = token_data.get("error_description", "An error occurred during token acquisition.")
            raise ValueError(f"Token request failed: {error} - {error_description}")
        
        # 3. 액세스 토큰 추출
        access_token = token_data.get("access_token")
        if not access_token:
            raise ValueError("Missing kakao_access_token")
        
        # 4. 카카오 프로필 정보 요청
        profile_url = "https://kapi.kakao.com/v2/user/me"
        profile_headers = {"Authorization": f"Bearer {access_token}"}
        
        profile_response = requests.post(profile_url, headers=profile_headers)
        if profile_response.status_code != 200:
            raise ValueError("Failed to get profile from Kakao")
        
        # 5. KakaoResponse 객체 생성
        profile_data = profile_response.json()
        kakao_response = cls(profile_data)
        
        if not kakao_response.is_valid:
            raise ValueError("Invalid response from Kakao")
        
        return kakao_response


class PassRequest:
    def __init__(self, data):
        self.data = data
    
    @property
    def req_no(self):
        return self.data.get('req_no')
    
    @property
    def req_dtim(self):
        return self.data.get('req_dtim')
    
    @property
    def token_val(self):
        return self.data.get('token_val')
    
    @property
    def result_val(self):
        return self.data.get('resultVal')
    
    @property
    def key(self):
        return self.data.get('key')
    
    @property
    def iv(self):
        return self.data.get('iv')
    
    @property
    def hmac_key(self):
        return self.data.get('hmac_key')
    
    @property
    def plain(self):
        return self.data.get('plain')
    
    @property
    def token_version_id(self):
        return self.data.get('token_version_id')
    
    @property
    def enc_data(self):
        return self.data.get('enc_data')
    
    @property
    def integrity(self):
        return self.data.get('integrity')
    
    @property
    def is_valid(self):
        return bool(
            self.req_no and 
            self.token_version_id and 
            self.enc_data and 
            self.integrity
        )
    
    def to_frontend_data(self):
        return {
            'req_no': self.req_no,
            'req_dtim': self.req_dtim,
            'token_version_id': self.token_version_id,
            'enc_data': self.enc_data,
            'integrity_value': self.integrity,
            'nice_server_url': 'https://nice.checkplus.co.kr/CheckPlusSafeModel/service.cb'
        }
    
    def to_session_data(self):
        return {
            'token_version_id': self.token_version_id,
            'req_no': self.req_no,
            'key': self.key,
            'iv': self.iv,
            'hmac_key': self.hmac_key
        }
    
    def debug_print(self):
        return f"PassRequest(req_no={self.req_no}, token_version_id={self.token_version_id}, is_valid={self.is_valid})"
    
    @classmethod
    def create_from_nice_api(cls, nice_access_token, nice_client_id, nice_product_id, nice_server_uri):
        # 1. 요청 데이터 생성
        now = str(int(time.time()))
        req_dtim = datetime.now().strftime('%Y%m%d%H%M%S')
        req_no = f"REQ{req_dtim}{str(random.randint(0, 10000)).zfill(4)}"
        
        # 2. NICE API 호출
        url = "https://svc.niceapi.co.kr:22001/digital/niceid/api/v1.0/common/crypto/token"
        auth = f"{nice_access_token}:{now}:{nice_client_id}"
        base64_auth = base64.b64encode(auth.encode('utf-8')).decode('utf-8')
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'bearer {base64_auth}',
            'productID': nice_product_id
        }
        
        data = {
            "dataHeader": {
                "CNTY_CD": "ko",
                "TRAN_ID": ""
            },
            "dataBody": {
                "req_dtim": req_dtim,
                "req_no": req_no,
                "enc_mode": "1"
            }
        }
        
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response_data = response.json()["dataBody"]
        
        site_code = response_data["site_code"]
        token_version_id = response_data["token_version_id"]
        token_val = response_data["token_val"]
        
        # 3. 암호화 키 생성
        result = f"{req_dtim}{req_no}{token_val}"
        result_val = base64.b64encode(hashlib.sha256(result.encode()).digest()).decode('utf-8')
        
        key = result_val[:16]
        iv = result_val[-16:]
        hmac_key = result_val[:32]
        
        # 4. 평문 데이터 생성
        plain_data = json.dumps({
            "requestno": req_no,
            "returnurl": nice_server_uri,
            "sitecode": site_code
        })
        
        # 5. 데이터 암호화
        enc_data = cls.encrypt_data(plain_data, key, iv)
        
        # 6. 무결성 값 생성
        h = hmac.new(
            key=hmac_key.encode(), 
            msg=enc_data.encode('utf-8'), 
            digestmod=hashlib.sha256
        ).digest()
        integrity_value = base64.b64encode(h).decode('utf-8')
        
        # 7. PassResponse 객체 생성
        render_params = {
            'req_no': req_no,
            'req_dtim': req_dtim,
            'token_val': token_val,
            'resultVal': result_val,
            'key': key,
            'iv': iv,
            'hmac_key': hmac_key,
            'plain': plain_data,
            'token_version_id': token_version_id,
            'enc_data': enc_data,
            'integrity': integrity_value
        }
        
        return cls(render_params)
    
    @staticmethod
    def encrypt_data(plain_data, key, iv):
        block_size = 16
        pad = lambda s: s + (block_size - len(s) % block_size) * chr(block_size - len(s) % block_size)
        cipher = AES.new(key.encode("utf8"), AES.MODE_CBC, iv.encode("utf8"))
        return base64.b64encode(cipher.encrypt(pad(plain_data).encode('utf-8'))).decode('utf-8')


class PassResponse:
    def __init__(self, data):
        self.data = data
    
    @property
    def req_no(self):
        return self.data.get('req_no')
    
    @property
    def token_version_id(self):
        return self.data.get('token_version_id')
    
    @property
    def enc_data(self):
        return self.data.get('enc_data')
    
    @property
    def integrity_value(self):
        return self.data.get('integrity_value')
    
    @property
    def is_valid(self):
        return bool(
            self.req_no and 
            self.token_version_id and 
            self.enc_data and 
            self.integrity_value
        )
    
    def parse_user_data(self, key, iv):
        try:
            # 데이터 복호화
            decrypted_data = self.decrypt_data(self.enc_data, key, iv)
            user_data = json.loads(decrypted_data)
            
            # 사용자 정보 추출
            parsed_data = {
                'name': user_data.get('name', ''),
                'birthdate': user_data.get('birthdate', ''),
                'gender': user_data.get('gender', ''),
                'mobile': user_data.get('mobile', ''),
                'ci': user_data.get('ci', ''),
                'di': user_data.get('di', ''),
                'auth_type': user_data.get('authtype', ''),
                'auth_date': user_data.get('authdate', ''),
                'auth_time': user_data.get('authtime', ''),
                'req_no': self.req_no,
                'token_version_id': self.token_version_id
            }
            
            return parsed_data
            
        except Exception as e:
            raise ValueError(f"사용자 데이터 파싱 실패: {str(e)}")
    
    @staticmethod
    def decrypt_data(enc_data, key, iv):
        encryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        unpad = lambda s: s[0:-ord(s[-1:])]
        return unpad(encryptor.decrypt(base64.b64decode(enc_data))).decode('euc-kr')
    
    def to_user_data(self):
        return {
            'name': '',
            'birthdate': '',
            'gender': '',
            'mobile': '',
            'ci': '',
            'di': '',
            'auth_type': '',
            'auth_date': '',
            'auth_time': '',
            'req_no': self.req_no,
            'token_version_id': self.token_version_id
        }
    
    def debug_print(self):
        return f"PassResponse(req_no={self.req_no}, token_version_id={self.token_version_id}, is_valid={self.is_valid})"
    
    @classmethod
    def create_from_request_data(cls, req_no, token_version_id, enc_data, integrity_value):
        data = {
            'req_no': req_no,
            'token_version_id': token_version_id,
            'enc_data': enc_data,
            'integrity_value': integrity_value
        }
        return cls(data)


class PortOneResponse:
    def __init__(self, data):
        self.data = data
        self.verified_customer = data.get('verifiedCustomer', {})
    
    @property
    def status(self):
        return self.data.get('status')
    
    @property
    def is_verified(self):
        return self.status == 'VERIFIED'
        
    @property
    def identity_verification_id(self):
        return self.data.get('id')
    
    @property
    def ci(self):
        return self.verified_customer.get('ci')
    
    @property
    def di(self):
        return self.verified_customer.get('di')
    
    @property
    def name(self):
        return self.verified_customer.get('name')
    
    @property
    def gender(self):
        return self.verified_customer.get('gender')
    
    @property
    def birthday(self):
        return self.verified_customer.get('birthDate')
    
    @property
    def operator(self):
        return self.verified_customer.get('operator')
    
    @property
    def mobile(self):
        phone_number = self.verified_customer.get('phoneNumber')
        if phone_number:
            return ''.join(filter(str.isdigit, str(phone_number)))
        return None
    
    @property
    def is_foreigner(self):
        is_foreigner = self.verified_customer.get('isForeigner')
        if is_foreigner is not None:
            return bool(is_foreigner)
        return None

    def to_user_data(self):
        return {
            'ci': self.ci,
            'name': self.name,
            'mobile': self.mobile,
            'birthday': self.birthday,
            'gender': self.gender,
        }


    def debug_print(self):
        return f"PortOneResponse(status={self.status}, is_verified={self.is_verified}, customer_exists={bool(self.verified_customer)})"
    
    @classmethod
    def create_from_code(cls, code, portone_api_secret):
        url = f"https://api.portone.io/identity-verifications/{code}"
        headers = {
            "Authorization": f"PortOne {portone_api_secret}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if not response.ok:
            error_detail = response.json() if response.content else "Unknown error"
            raise Exception(f"포트원 API 호출 실패: {response.status_code} - {error_detail}")
        
        response_json = response.json()
        
        # 인증 상태 확인
        if response_json.get('status') != 'VERIFIED':
            raise Exception(f"인증이 완료되지 않았습니다. 상태: {response_json.get('status')}")
        
        # 인증된 고객 정보 확인
        verified_customer = response_json.get('verifiedCustomer')
        if not verified_customer:
            raise Exception("인증된 고객 정보를 찾을 수 없습니다.")
        
        return cls(response_json)
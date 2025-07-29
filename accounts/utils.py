# accounts/utils.py
app_name = 'accounts'

import secrets, string

# Password Generator
# <-------------------------------------------------------------------------------------------------------------------------------->
def generate_random_password(length=12):
    # 사용할 문자 집합 (대문자, 소문자, 숫자, 특수문자)
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"

    # 길이만큼 랜덤하게 선택해 문자열 생성
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


# Mobile Generator
# <-------------------------------------------------------------------------------------------------------------------------------->
def generate_random_mobile():
    # 한국 휴대폰 번호 형식: 010-XXXX-XXXX (11자리)
    prefix = "010"
    middle = ''.join(secrets.choice(string.digits) for _ in range(4))
    suffix = ''.join(secrets.choice(string.digits) for _ in range(4))
    
    return f"{prefix}{middle}{suffix}"


# Response Objects
# <-------------------------------------------------------------------------------------------------------------------------------->
class NaverResponse:
    def __init__(self, response_data):
        self.response_data = response_data
        self.profile = response_data.get("response", {})
    
    @property
    def resultcode(self):
        return self.response_data.get('resultcode')
    
    @property
    def message(self):
        return self.response_data.get('message')
    
    @property
    def id(self):
        return self.profile.get('id')
    
    @property
    def email(self):
        return self.profile.get('email')
    
    @property
    def mobile(self):
        mobile = self.profile.get('mobile')
        if not mobile:
            return None
        return mobile.replace('-', '')
    
    @property
    def name(self):
        return self.profile.get('name')
    
    @property
    def nickname(self):
        return self.profile.get('nickname')
    
    @property
    def profile_image(self):
        return self.profile.get('profile_image')
    
    @property
    def age(self):
        return self.profile.get('age')
    
    @property
    def gender(self):
        return self.profile.get('gender')
    
    @property
    def birthday(self):
        return self.profile.get('birthday')
    
    @property
    def birthyear(self):
        return self.profile.get('birthyear')
    
    @property
    def is_valid(self):
        return self.resultcode == "00" and bool(self.profile)
    
    def to_user_data(self, provider='naver'):
        user_data = {
            'email': self.email,
            'mobile': self.mobile,
            'name': self.name,
            'password': generate_random_password(),
            'provider': provider,
            'provider_user_id': self.id,
        }
        
        if self.nickname:
            user_data['username'] = self.nickname
            
        return user_data
    
    def debug_print(self):
        print("=== NaverResponse Debug Info ===")
        print(f"Result Code: {self.resultcode}")
        print(f"Message: {self.message}")
        print(f"ID: {self.id}")
        print(f"Email: {self.email}")
        print(f"Mobile: {self.mobile}")
        print(f"Name: {self.name}")
        print(f"Nickname: {self.nickname}")
        print(f"Profile Image: {self.profile_image}")
        print(f"Age: {self.age}")
        print(f"Gender: {self.gender}")
        print(f"Birthday: {self.birthday}")
        print(f"Birthyear: {self.birthyear}")
        print("=== Raw Response Data ===")
        print(f"Full Response: {self.response_data}")
        print("================================")


class GoogleResponse:
    def __init__(self, response_data):
        self.response_data = response_data
    
    @property
    def id(self):
        return self.response_data.get('id')
    
    @property
    def email(self):
        return self.response_data.get('email')
    
    @property
    def name(self):
        return self.response_data.get('name')
    
    @property
    def given_name(self):
        return self.response_data.get('given_name')
    
    @property
    def family_name(self):
        return self.response_data.get('family_name')
    
    @property
    def picture(self):
        return self.response_data.get('picture')
    
    @property
    def locale(self):
        return self.response_data.get('locale')
    
    @property
    def verified_email(self):
        return self.response_data.get('verified_email')
    
    @property
    def hd(self):
        return self.response_data.get('hd')  # hosted domain
    
    @property
    def is_valid(self):
        return bool(self.response_data.get('id'))
    
    def to_user_data(self, provider='google'):
        user_data = {
            'email': self.email,
            'name': self.name,
            'password': generate_random_password(),
            'provider': provider,
            'provider_user_id': self.id,
        }
        
        # 이름이 없으면 given_name과 family_name 조합 사용
        if not self.name and (self.given_name or self.family_name):
            user_data['name'] = f"{self.given_name or ''} {self.family_name or ''}".strip()
        
        return user_data
    
    def debug_print(self):
        print("=== GoogleResponse Debug Info ===")
        print(f"ID: {self.id}")
        print(f"Email: {self.email}")
        print(f"Name: {self.name}")
        print(f"Given Name: {self.given_name}")
        print(f"Family Name: {self.family_name}")
        print(f"Picture: {self.picture}")
        print(f"Locale: {self.locale}")
        print(f"Verified Email: {self.verified_email}")
        print(f"Hosted Domain: {self.hd}")
        print("=== Raw Response Data ===")
        print(f"Full Response: {self.response_data}")
        print("================================")


class KakaoResponse:
    def __init__(self, response_data):
        self.response_data = response_data
        self.kakao_account = response_data.get("kakao_account", {})
        self.profile = self.kakao_account.get("profile", {})
    
    @property
    def id(self):
        return self.response_data.get('id')
    
    @property
    def email(self):
        return self.kakao_account.get('email')
    
    @property
    def mobile(self):
        phone_number = self.kakao_account.get('phone_number')
        # phone_number가 None이거나 빈 문자열이면 None 반환
        if not phone_number:
            return None
        # +82 00-0000-0000 형식을 00000000000 형식으로 변환
        if phone_number.startswith('+82 '):
            return phone_number.replace('+82 ', '0').replace('-', '')
        return phone_number.replace('-', '')
    
    @property
    def name(self):
        return self.kakao_account.get('name')
    
    @property
    def nickname(self):
        return self.profile.get('nickname')
    
    @property
    def profile_image(self):
        return self.profile.get('profile_image_url')
    
    @property
    def thumbnail_image(self):
        return self.profile.get('thumbnail_image_url')
    
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
        return self.kakao_account.get('birthday_type')  # SOLAR(양력) 또는 LUNAR(음력)
    
    @property
    def is_leap_month(self):
        return self.kakao_account.get('is_leap_month')
    
    @property
    def has_signed_up(self):
        return self.response_data.get('has_signed_up')
    
    @property
    def connected_at(self):
        return self.response_data.get('connected_at')
    
    @property
    def synched_at(self):
        return self.response_data.get('synched_at')
    
    @property
    def properties(self):
        return self.response_data.get('properties', {})
    
    @property
    def for_partner(self):
        return self.response_data.get('for_partner', {})
    
    # 동의 관련 프로퍼티들
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
    def is_email_valid(self):
        return self.kakao_account.get('is_email_valid')
    
    @property
    def is_email_verified(self):
        return self.kakao_account.get('is_email_verified')
    
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
    def is_valid(self):
        return bool(self.response_data.get('id'))
    
    def to_user_data(self, provider='kakao'):
        user_data = {
            'email': self.email,
            'mobile': self.mobile,
            'name': self.name,
            'password': generate_random_password(),
            'provider': provider,
            'provider_user_id': self.id,
        }
        
        if self.nickname:
            user_data['username'] = self.nickname
            
        return user_data
    
    def debug_print(self):
        print("=== KakaoResponse Debug Info ===")
        print(f"ID: {self.id}")
        print(f"Email: {self.email}")
        print(f"Mobile: {self.mobile}")
        print(f"Name: {self.name}")
        print(f"Nickname: {self.nickname}")
        print(f"Profile Image: {self.profile_image}")
        print(f"Thumbnail Image: {self.thumbnail_image}")
        print(f"Gender: {self.gender}")
        print(f"Birthday: {self.birthday}")
        print(f"Birthyear: {self.birthyear}")
        print(f"Age Range: {self.age_range}")
        print(f"CI: {self.ci}")
        print(f"CI Authenticated At: {self.ci_authenticated_at}")
        print(f"Birthday Type: {self.birthday_type}")
        print(f"Is Leap Month: {self.is_leap_month}")
        print(f"Has Signed Up: {self.has_signed_up}")
        print(f"Connected At: {self.connected_at}")
        print(f"Synched At: {self.synched_at}")
        print(f"Properties: {self.properties}")
        print(f"For Partner: {self.for_partner}")
        print("=== Agreement Info ===")
        print(f"Profile Needs Agreement: {self.profile_needs_agreement}")
        print(f"Name Needs Agreement: {self.name_needs_agreement}")
        print(f"Email Needs Agreement: {self.email_needs_agreement}")
        print(f"Phone Number Needs Agreement: {self.phone_number_needs_agreement}")
        print(f"CI Needs Agreement: {self.ci_needs_agreement}")
        print("=== Raw Response Data ===")
        print(f"Full Response: {self.response_data}")
        print("================================")
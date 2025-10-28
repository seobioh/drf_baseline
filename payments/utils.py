# payments/utils.py
app_name = 'payments'

import uuid
import requests
from datetime import datetime

from django.utils import timezone as django_timezone

from server.settings.base import TOSS_API_SECRET_BASE64, PORTONE_API_SECRET
from .models import Billing, Payment

# Billing
def create_toss_billing(user, auth_key, customer_key):
    url = "https://api.tosspayments.com/v1/billing/authorizations/issue"
    
    headers = {
        'Authorization': f'Basic {TOSS_API_SECRET_BASE64}',
        'Content-Type': 'application/json'
    }
    data = {
        "authKey": auth_key,
        "customerKey": customer_key
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        if 'error' in response_data:
            error_code = response_data.get('error', {}).get('code', 'UNKNOWN')
            error_message = response_data.get('error', {}).get('message', 'Unknown error')
            raise ValueError(f"Toss Payments API error: {error_code} - {error_message}")

        card_info = response_data.get('card', {})
        
        billing = Billing.objects.create(
            user=user,
            vender='TOSS',
            customer_key=response_data.get('customerKey'),
            billing_key=response_data.get('billingKey'),
            card_company=response_data.get('cardCompany'),
            card_number=response_data.get('cardNumber'),
            card_type=card_info.get('cardType'),
            card_owner_type=card_info.get('ownerType'),
            card_issuer_code=card_info.get('issuerCode'),
            card_acquirer_code=card_info.get('acquirerCode'),
        )
        
        return billing
        
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"Failed to create billing key: {str(e)}")

    except ValueError as e:
        raise e

    except Exception as e:
        raise Exception(f"Unexpected error creating billing key: {str(e)}")


def payment_toss_billing(user, billing, amount, order_id, order_name, tax_free_amount=0, tax_exemption_amount=0):
    url = f"https://api.tosspayments.com/v1/billing/{billing.billing_key}"
    
    headers = {
        'Authorization': f'Basic {TOSS_API_SECRET_BASE64}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "customerKey": billing.customer_key,
        "amount": amount,
        "orderId": order_id,
        "orderName": order_name,
        "taxFreeAmount": tax_free_amount,
        "taxExemptionAmount": tax_exemption_amount,
        "customerEmail": user.email,
        "customerName": user.name,
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        
        if 'error' in response_data:
            error_code = response_data.get('error', {}).get('code', 'UNKNOWN')
            error_message = response_data.get('error', {}).get('message', 'Unknown error')
            raise ValueError(f"Toss Payments API error: {error_code} - {error_message}")

        requested_at_str = response_data.get('requestedAt', '').replace('+09:00', '')
        requested_at = django_timezone.make_aware(datetime.fromisoformat(requested_at_str))
        approved_at = None
        if response_data.get('approvedAt'):
            approved_at_str = response_data.get('approvedAt', '').replace('+09:00', '')
            approved_at = django_timezone.make_aware(datetime.fromisoformat(approved_at_str))
        
        # Extract card information
        card_info = response_data.get('card') or {}
        
        # Extract EasyPay information
        easypay_info = response_data.get('easyPay') or {}
        
        # Extract receipt and checkout URLs
        receipt_info = response_data.get('receipt') or {}
        checkout_info = response_data.get('checkout') or {}
        
        # Create Payment object
        payment = Payment.objects.create(
            user=user,
            billing=billing,
            vender='TOSS',
            payment_key=response_data.get('paymentKey'),
            status=response_data.get('status'),
            type=response_data.get('type'),
            order_id=response_data.get('orderId'),
            order_name=response_data.get('orderName'),
            merchant_id=response_data.get('mId'),
            currency=response_data.get('currency'),
            method=response_data.get('method'),
            total_amount=response_data.get('totalAmount'),
            balance_amount=response_data.get('balanceAmount'),
            supplied_amount=response_data.get('suppliedAmount'),
            vat=response_data.get('vat'),
            tax_exemption_amount=response_data.get('taxExemptionAmount'),
            tax_free_amount=response_data.get('taxFreeAmount'),
            
            # Card information
            card_issuer_code=card_info.get('issuerCode'),
            card_acquirer_code=card_info.get('acquirerCode'),
            card_number=card_info.get('number'),
            card_installment_plan_months=card_info.get('installmentPlanMonths'),
            card_is_interest_free=card_info.get('isInterestFree'),
            card_interest_payer=card_info.get('interestPayer'),
            card_approve_no=card_info.get('approveNo'),
            card_use_card_point=card_info.get('useCardPoint'),
            card_type=card_info.get('cardType'),
            card_owner_type=card_info.get('ownerType'),
            card_acquire_status=card_info.get('acquireStatus'),
            card_amount=card_info.get('amount'),
            
            # EasyPay information
            easypay_provider=easypay_info.get('provider'),
            easypay_amount=easypay_info.get('amount'),
            easypay_discount_amount=easypay_info.get('discountAmount'),
            
            # Other information
            country=response_data.get('country'),
            is_partial_cancelable=response_data.get('isPartialCancelable'),
            use_escrow=response_data.get('useEscrow'),
            culture_expense=response_data.get('cultureExpense'),
            receipt_url=receipt_info.get('url'),
            checkout_url=checkout_info.get('url'),
            last_transaction_key=response_data.get('lastTransactionKey'),
            secret=response_data.get('secret'),
            version=response_data.get('version'),
            
            requested_at=requested_at,
            approved_at=approved_at,
        )
        
        return payment
        
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"Failed to process payment: {str(e)}")
        
    except ValueError as e:
        raise e
        
    except Exception as e:
        raise Exception(f"Unexpected error processing payment: {str(e)}")


def delete_toss_billing(billing_key):
    url = f"https://api.tosspayments.com/v1/billing/{billing_key}"
    
    headers = {
        'Authorization': f'Basic {TOSS_API_SECRET_BASE64}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        
        if response.status_code == 200:
            return True
        else:
            raise ValueError(f"Unexpected response status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"Failed to delete billing key: {str(e)}")
        
    except ValueError as e:
        raise e
        
    except Exception as e:
        raise Exception(f"Unexpected error deleting billing key: {str(e)}")


def create_portone_billing(user, billing_key):
    billing = Billing.objects.create(
        user=user,
        vender='PORTONE',
        billing_key=billing_key,
    )
    
    return billing


def payment_portone_billing(user, billing, order_id, order_name, amount, currency="KRW"):
    payment_url = f"https://api.portone.io/payments/{order_id}/billing-key"
    
    headers = {
        'Authorization': f'PortOne {PORTONE_API_SECRET}',
        'Content-Type': 'application/json'
    }
    
    payment_data = {
        "billingKey": billing.billing_key,
        "orderName": order_name,
        "customer": {
            "name": {"full": user.name},
            "email": user.email,
            "phoneNumber": user.mobile,
        },
        "amount": {
            "total": amount
        },
        "currency": currency
    }
    
    try:
        response = requests.post(payment_url, headers=headers, json=payment_data)
        response.raise_for_status()
        
        if not response.ok:
            raise ValueError(f"Payment request failed: {response.status_code}")
        
        detail_url = f"https://api.portone.io/payments/{order_id}"
        
        detail_response = requests.get(detail_url, headers=headers)
        detail_response.raise_for_status()
        
        if not detail_response.ok:
            raise ValueError(f"Payment detail request failed: {detail_response.status_code}")
        
        payment_detail = detail_response.json()
        method_info = payment_detail.get('method', {})
        amount_info = payment_detail.get('amount', {})
        
        # 상태 매핑 (PortOne -> Django 모델)
        status_mapping = {
            'READY': 'READY',
            'PAID': 'DONE',
            'CANCELLED': 'CANCELED',
            'PARTIAL_CANCELLED': 'PARTIAL_CANCELED',
            'FAILED': 'ABORTED',
            'PAY_PENDING': 'IN_PROGRESS',
            'VIRTUAL_ACCOUNT_ISSUED': 'WAITING_FOR_DEPOSIT'
        }
        
        mapped_status = status_mapping.get(payment_detail.get('status'), 'READY')
        
        # 날짜 파싱
        requested_at = datetime.fromisoformat(payment_detail.get('requestedAt', '').replace('Z', '+00:00'))
        approved_at = None
        if payment_detail.get('paidAt'):
            approved_at = datetime.fromisoformat(payment_detail.get('paidAt', '').replace('Z', '+00:00'))
        
        # Payment 객체 생성
        payment = Payment.objects.create(
            user=user,
            billing=billing,
            vender='PORTONE',
            payment_key=payment_detail.get('transactionId'),
            status=mapped_status,
            type='BILLING',
            order_id=payment_detail.get('id'),
            order_name=payment_detail.get('orderName'),
            merchant_id=payment_detail.get('merchantId'),
            currency=payment_detail.get('currency'),
            method=method_info.get('type') if method_info else None,
            total_amount=amount_info.get('total', 0),
            balance_amount=amount_info.get('balance', 0),
            supplied_amount=amount_info.get('supplied', 0),
            vat=amount_info.get('vat', 0),
            tax_exemption_amount=amount_info.get('taxExemption', 0),
            tax_free_amount=amount_info.get('taxFree', 0),
            
            # 카드 정보
            card_issuer_code=method_info.get('issuerCode') if method_info else None,
            card_acquirer_code=method_info.get('acquirerCode') if method_info else None,
            card_number=method_info.get('number') if method_info else None,
            card_installment_plan_months=method_info.get('installmentPlanMonths') if method_info else None,
            card_is_interest_free=method_info.get('isInterestFree') if method_info else None,
            card_interest_payer=method_info.get('interestPayer') if method_info else None,
            card_approve_no=method_info.get('approveNo') if method_info else None,
            card_use_card_point=method_info.get('useCardPoint') if method_info else None,
            card_type=method_info.get('cardType') if method_info else None,
            card_owner_type=method_info.get('ownerType') if method_info else None,
            card_acquire_status=method_info.get('acquireStatus') if method_info else None,
            card_amount=method_info.get('amount') if method_info else None,
            
            # 기타 정보
            country=payment_detail.get('country', 'KR'),
            is_partial_cancelable=payment_detail.get('isPartialCancelable', True),
            use_escrow=payment_detail.get('escrow', {}).get('status') == 'REGISTERED' if payment_detail.get('escrow') else False,
            culture_expense=payment_detail.get('isCulturalExpense', False),
            receipt_url=payment_detail.get('receiptUrl'),
            checkout_url=None,
            last_transaction_key=payment_detail.get('transactionId'),
            secret=None,
            version='2022-11-16',
            
            requested_at=requested_at,
            approved_at=approved_at,
            cancelled_at=None,
        )
        
        return payment
        
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"Failed to process PortOne billing payment: {str(e)}")
        
    except ValueError as e:
        raise e
        
    except Exception as e:
        raise Exception(f"Unexpected error processing PortOne billing payment: {str(e)}")


def delete_portone_billing(billing_key):
    url = f"https://api.portone.io/billing-keys/{billing_key}"
    
    headers = {
        'Authorization': f'PortOne {PORTONE_API_SECRET}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        if response.status_code == 200:
            return True
        else:
            raise ValueError(f"Unexpected response status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"Failed to delete billing key: {str(e)}")
        
    except ValueError as e:
        raise e
        
    except Exception as e:
        raise Exception(f"Unexpected error deleting billing key: {str(e)}")


def payment_billing(user, billing, amount, order_name, tax_free_amount=0, tax_exemption_amount=0, currency="KRW"):
    order_id = str(uuid.uuid4())
    
    if billing.vender == 'TOSS':
        return payment_toss_billing(
            user=user,
            billing=billing,
            amount=amount,
            order_id=order_id,
            order_name=order_name,
            tax_free_amount=tax_free_amount,
            tax_exemption_amount=tax_exemption_amount
        )
    elif billing.vender == 'PORTONE':
        return payment_portone_billing(
            user=user,
            billing=billing,
            order_id=order_id,
            order_name=order_name,
            amount=amount,
            currency=currency
        )
    else:
        raise ValueError(f"Unsupported billing vendor: {billing.vender}")


def inactivate_billing(billing):
    if billing.vender == 'TOSS':
        return delete_toss_billing(billing.billing_key)
    elif billing.vender == 'PORTONE':
        return delete_portone_billing(billing.billing_key)
    else:
        raise ValueError(f"Unsupported billing vendor: {billing.vender}")


# Payment
def confirm_toss_payment(user, payment_key, amount, order_id):    
    url = "https://api.tosspayments.com/v1/payments/confirm"
    
    headers = {
        'Authorization': f'Basic {TOSS_API_SECRET_BASE64}',
        'Content-Type': 'application/json'
    }

    data = {
        "paymentKey": payment_key,
        "orderId" : order_id,
        "amount" : amount
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()

        if 'error' in response_data:
            error_code = response_data.get('error', {}).get('code', 'UNKNOWN')
            error_message = response_data.get('error', {}).get('message', 'Unknown error')
            raise ValueError(f"Toss Payments API error: {error_code} - {error_message}")

        requested_at_str = response_data.get('requestedAt', '').replace('+09:00', '')
        requested_at = django_timezone.make_aware(datetime.fromisoformat(requested_at_str))
        approved_at = None
        if response_data.get('approvedAt'):
            approved_at_str = response_data.get('approvedAt', '').replace('+09:00', '')
            approved_at = django_timezone.make_aware(datetime.fromisoformat(approved_at_str))
        
        # Extract card information
        card_info = response_data.get('card') or {}
        
        # Extract EasyPay information
        easypay_info = response_data.get('easyPay') or {}
        
        # Extract receipt and checkout URLs
        receipt_info = response_data.get('receipt') or {}
        checkout_info = response_data.get('checkout') or {}
        
        payment = Payment.objects.create(
            user=user,
            vender='TOSS',
            payment_key=response_data.get('paymentKey'),
            status=response_data.get('status'),
            type=response_data.get('type'),
            order_id=response_data.get('orderId'),
            order_name=response_data.get('orderName'),
            merchant_id=response_data.get('mId'),
            currency=response_data.get('currency'),
            method=response_data.get('method'),
            total_amount=response_data.get('totalAmount'),
            balance_amount=response_data.get('balanceAmount'),
            supplied_amount=response_data.get('suppliedAmount'),
            vat=response_data.get('vat'),
            tax_exemption_amount=response_data.get('taxExemptionAmount'),
            tax_free_amount=response_data.get('taxFreeAmount'),
            
            # Card information
            card_issuer_code=card_info.get('issuerCode'),
            card_acquirer_code=card_info.get('acquirerCode'),
            card_number=card_info.get('number'),
            card_installment_plan_months=card_info.get('installmentPlanMonths'),
            card_is_interest_free=card_info.get('isInterestFree'),
            card_interest_payer=card_info.get('interestPayer'),
            card_approve_no=card_info.get('approveNo'),
            card_use_card_point=card_info.get('useCardPoint'),
            card_type=card_info.get('cardType'),
            card_owner_type=card_info.get('ownerType'),
            card_acquire_status=card_info.get('acquireStatus'),
            card_amount=card_info.get('amount'),
            
            # EasyPay information
            easypay_provider=easypay_info.get('provider'),
            easypay_amount=easypay_info.get('amount'),
            easypay_discount_amount=easypay_info.get('discountAmount'),
            
            # Other information
            country=response_data.get('country'),
            is_partial_cancelable=response_data.get('isPartialCancelable'),
            use_escrow=response_data.get('useEscrow'),
            culture_expense=response_data.get('cultureExpense'),
            receipt_url=receipt_info.get('url'),
            checkout_url=checkout_info.get('url'),
            last_transaction_key=response_data.get('lastTransactionKey'),
            secret=response_data.get('secret'),
            version=response_data.get('version'),
            
            requested_at=requested_at,
            approved_at=approved_at,
        )
        
        return payment
        
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"Failed to process payment: {str(e)}")
        
    except ValueError as e:
        raise e
        
    except Exception as e:
        raise Exception(f"Unexpected error processing payment: {str(e)}")
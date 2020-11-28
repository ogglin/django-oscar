import json

import requests
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from oscar.apps.checkout import views
from oscar.apps.checkout.views import ShippingAddressForm
from oscar.apps.payment import forms, models

import modnaya_shtuchka.settings as settings

user_name = 'userName-api'
password = 'password'
return_url = '/checkout/payment-details/'
fail_url = '/checkout/payment-details/error_payment'
if settings.SBER_USERNAME:
    user_name = settings.SBER_USERNAME
if settings.SBER_PASSWORD:
    password = settings.SBER_PASSWORD
if settings.SBER_PASSWORD:
    return_url = settings.SBER_RETURNURL
if settings.SBER_PASSWORD:
    fail_url = settings.SBER_FAILURL

# # Subclass the core Oscar view so we can customise
# class ShippingAddressView(views.ShippingAddressView):
#     print('----------------')
#     print('Sber ShippingAddressView')
#     template_name = 'oscar/checkout/shipping_address.html'
#     form_class = ShippingAddressForm
#     success_url = reverse_lazy('checkout:shipping-method')
#     pre_conditions = ['check_basket_is_not_empty',
#                       'check_basket_is_valid',
#                       'check_user_email_is_captured']
#     skip_conditions = ['skip_unless_basket_requires_shipping']
from modnaya_shtuchka import settings


def new_order(order_number, incl_tax):
    url = "https://3dsec.sberbank.ru/payment/rest/register.do"
    summa = str(incl_tax).replace('.', '')
    payload = f'userName={user_name}&password={password}&orderNumber={order_number}&amount={summa}' \
              f'&returnUrl={return_url}' \
              f'&failUrl={fail_url}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response


def get_order_status(order_number):
    url = "https://3dsec.sberbank.ru/payment/rest/getOrderStatusExtended.do"
    payload = f'userName={user_name}&password={password}&orderNumber={order_number}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response


def sber_pay(order_id, request):
    url = f'https://3dsec.sberbank.ru/payment/merchants/sbersafe_id/payment_ru.html'
    print('URL: ', url, order_id)
    return redirect(url, {'mdOrder': order_id})
    # return render(request, url, {'url': url, 'mdOrder': order_id})


class PaymentDetailsView(views.PaymentDetailsView):
    """
    An example view that shows how to integrate BOTH PayPal Express
    (see `get_context_data method`) and PayPal Flow (the other methods).
    Naturally, you will only want to use one of the two.
    """
    template_name = 'checkout/payment_details.html'
    template_name_preview = 'checkout/preview.html'

    def get_context_data(self, **kwargs):
        """
        Add data for Paypal Express flow.
        """
        # Override method so the bankcard and billing address forms can be
        # added to the context.
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        ctx['bankcard_form'] = kwargs.get(
            'bankcard_form', forms.BankcardForm())
        ctx['billing_address_form'] = kwargs.get(
            'billing_address_form', forms.BillingAddressForm())
        return ctx

    def post(self, request, *args, **kwargs):
        # Override so we can validate the bankcard/billing_address submission.
        # If it is valid, we render the preview screen with the forms hidden
        # within it.  When the preview is submitted, we pick up the 'action'
        # parameters and actually place the order.
        method = 'Выберите способ оплаты'
        if request.POST.get('method') == 'sber':
            method = 'Сбербанк'
        if request.POST.get('action', '') == 'place_order':
            return self.do_place_order(request, method=request.POST.get('method'))

        # Render preview with bankcard and billing address details hidden
        return self.render_preview(request, method=method)

    def do_place_order(self, request, method):
        # Helper method to check that the hidden forms wasn't tinkered
        # with.
        print(method, request.POST, self)

        # Attempt to submit the order, passing the bankcard object so that it
        # gets passed back to the 'handle_payment' method below.
        submission = self.build_submission()
        submission['payment_kwargs']['method'] = method
        print(submission)
        return self.submit(**submission)

    def handle_payment(self, order_number, order_total, **kwargs):
        print('Sber handle_payment')
        """
        Make submission to Sber Bank
        """
        '''Set sber config from settings'''

        # Using authorization here (two-stage model).  You could use sale to
        # perform the auth and capture in one step.  The choice is dependent
        # on your business model.
        result = new_order(order_number, incl_tax=order_total.incl_tax)
        jdata = json.loads(result.text)
        order_id = ''
        if jdata['errorCode']:
            error_code = jdata['errorCode']
            print(error_code, jdata['errorMessage'])
            if int(error_code) == 1:
                status = json.loads(get_order_status(order_number).text)
                if int(status['errorCode']) == 0:
                    order_id = status['attributes'][0]['value']
        else:
            order_id = jdata['orderId']
        if order_id != '':
            sber_pay(order_id, self.request)

        # Record payment source and event
        # source_type, is_created = models.SourceType.objects.get_or_create(
        #     name='Sber')
        # source = source_type.sources.model(
        #     source_type=source_type,
        #     amount_allocated=total.incl_tax, currency=total.currency)
        # self.add_payment_source(source)
        # self.add_payment_event('Authorised', total.incl_tax)

    def handle_place_order_submission(self, request):
        print('handle_place_order_submission')
        """
        Handle a request to place an order.

        This method is normally called after the customer has clicked "place
        order" on the preview page. It's responsible for (re-)validating any
        form information then building the submission dict to pass to the
        `submit` method.

        If forms are submitted on your payment details view, you should
        override this method to ensure they are valid before extracting their
        data into the submission dict and passing it onto `submit`.
        """
        return self.submit(**self.build_submission())

from utils.parsing import NoRaiseBaseModel
from typing import Optional, Sequence

from pydantic import BaseModel, Field, StrictStr


class CustomerInformationInvoice(NoRaiseBaseModel):
    customer_name: Optional[StrictStr]
    customer_address: Optional[StrictStr]  # Deprecated need to be removed
    customer_email: Optional[StrictStr]  # New
    customer_id: Optional[StrictStr]  # New
    customer_tax_id: Optional[StrictStr]  # New
    customer_mailing_address: Optional[StrictStr]  # New
    customer_billing_address: Optional[StrictStr]  # New
    customer_shipping_address: Optional[StrictStr]  # New
    customer_service_address: Optional[StrictStr]  # New
    customer_remittance_address: Optional[StrictStr]  # New
    abn_number: Optional[StrictStr]  # New
    gst_number: Optional[StrictStr]  # New
    pan_number: Optional[StrictStr]  # New
    vat_number: Optional[StrictStr]  # New
    siret_number: Optional[StrictStr] = None # New
    siren_number: Optional[StrictStr] = None # New

    @staticmethod
    def default() -> "CustomerInformationInvoice":
        return CustomerInformationInvoice(
            customer_name=None,
            customer_address=None,
            customer_email=None,
            customer_id=None,
            customer_tax_id=None,
            customer_mailing_address=None,
            customer_billing_address=None,
            customer_shipping_address=None,
            customer_service_address=None,
            customer_remittance_address=None,
            abn_number=None,
            gst_number=None,
            pan_number=None,
            vat_number=None,
        )


class MerchantInformationInvoice(NoRaiseBaseModel):
    merchant_name: Optional[StrictStr]
    merchant_address: Optional[StrictStr]
    merchant_phone: Optional[StrictStr]  # New
    merchant_email: Optional[StrictStr]  # New
    merchant_fax: Optional[StrictStr]  # New
    merchant_website: Optional[StrictStr]  # New
    merchant_tax_id: Optional[StrictStr]  # New
    merchant_siret: Optional[StrictStr]  # New
    merchant_siren: Optional[StrictStr]  # New
    abn_number: Optional[StrictStr]  # New
    gst_number: Optional[StrictStr]  # New
    pan_number: Optional[StrictStr]  # New
    vat_number: Optional[StrictStr]

    @staticmethod
    def default() -> "MerchantInformationInvoice":
        return MerchantInformationInvoice(
            merchant_name=None,
            merchant_address=None,
            merchant_phone=None,
            merchant_email=None,
            merchant_fax=None,
            merchant_website=None,
            merchant_tax_id=None,
            merchant_siret=None,
            merchant_siren=None,
            abn_number=None,
            gst_number=None,
            pan_number=None,
            vat_number=None,
        )


class LocaleInvoice(NoRaiseBaseModel):
    currency: Optional[StrictStr]
    language: Optional[StrictStr]

    @staticmethod
    def default() -> "LocaleInvoice":
        return LocaleInvoice(currency=None, language=None)


class ItemLinesInvoice(NoRaiseBaseModel):
    description: Optional[StrictStr] = None
    quantity: Optional[float] = None
    amount: Optional[float] = None
    unit_price: Optional[float] = None
    discount: Optional[float] = None  # New
    product_code: Optional[StrictStr] = None  # New
    date_item: Optional[str] = None  # New
    tax_item: Optional[float] = None  # New
    tax_rate: Optional[float] = None  # New


class TaxesInvoice(NoRaiseBaseModel):
    value: Optional[float]
    rate: Optional[float]

    @staticmethod
    def default() -> "TaxesInvoice":
        return TaxesInvoice(value=None, rate=None)


class BankInvoice(NoRaiseBaseModel):  # New obj
    account_number: Optional[StrictStr]  # New
    iban: Optional[StrictStr]  # New
    bsb: Optional[StrictStr]  # New
    sort_code: Optional[StrictStr]  # New
    vat_number: Optional[StrictStr]  # New
    rooting_number: Optional[StrictStr]  # New
    swift: Optional[StrictStr]

    @staticmethod
    def default() -> "BankInvoice":
        return BankInvoice(
            account_number=None,
            iban=None,
            bsb=None,
            sort_code=None,
            vat_number=None,
            rooting_number=None,
            swift=None,
        )


class InfosInvoiceParserDataClass(NoRaiseBaseModel):
    customer_information: CustomerInformationInvoice = (
        CustomerInformationInvoice.default()
    )
    merchant_information: MerchantInformationInvoice = (
        MerchantInformationInvoice.default()
    )
    # --------------------------------------------#
    invoice_number: Optional[StrictStr] = None
    invoice_total: Optional[float] = None
    invoice_subtotal: Optional[float] = None
    gratuity: Optional[float] = None  # New
    amount_due: Optional[float] = None  # New
    previous_unpaid_balance: Optional[float] = None  # New
    discount: Optional[float] = None  # New
    taxes: Sequence[TaxesInvoice] = Field(
        default_factory=list
    )  # Change from list to item -> total_tax
    service_charge: Optional[float] = None  # New
    # --------------------------------------------#
    payment_term: Optional[StrictStr] = None  # New
    purchase_order: Optional[StrictStr] = None  # New
    date: Optional[StrictStr] = None
    due_date: Optional[StrictStr] = None
    service_date: Optional[StrictStr] = None  # New
    service_due_date: Optional[StrictStr] = None  # New
    po_number: Optional[StrictStr] = None  # New
    # --------------------------------------------#
    locale: LocaleInvoice = LocaleInvoice(currency=None, language=None)
    bank_informations: BankInvoice = BankInvoice.default()  # New
    # --------------------------------------------#
    item_lines: Sequence[ItemLinesInvoice] = Field(default_factory=list)


class InvoiceParserDataClass(NoRaiseBaseModel):
    extracted_data: Sequence[InfosInvoiceParserDataClass] = Field(default_factory=list)

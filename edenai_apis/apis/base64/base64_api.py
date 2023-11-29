import base64
import json
import mimetypes
import uuid
from collections import defaultdict
from enum import Enum
from itertools import zip_longest
from typing import Any, Dict, Sequence, Type, TypeVar, Union

import requests

from edenai_apis.features import ProviderInterface, OcrInterface
from edenai_apis.features.image.face_compare import (
    FaceCompareDataClass,
    FaceMatch,
    FaceCompareBoundingBox,
)
from edenai_apis.features.ocr.anonymization_async.anonymization_async_dataclass import (
    AnonymizationAsyncDataClass,
)
from edenai_apis.features.ocr.bank_check_parsing import (
    BankCheckParsingDataClass,
    MicrModel,
)
from edenai_apis.features.ocr.bank_check_parsing.bank_check_parsing_dataclass import (
    ItemBankCheckParsingDataClass,
)
from edenai_apis.features.ocr.data_extraction.data_extraction_dataclass import (
    DataExtractionDataClass,
    ItemDataExtraction,
)
from edenai_apis.features.ocr.identity_parser import (
    IdentityParserDataClass,
    InfoCountry,
    ItemIdentityParserDataClass,
    get_info_country,
    InfosIdentityParserDataClass,
)
from edenai_apis.features.ocr.identity_parser.identity_parser_dataclass import (
    Country,
    format_date,
)
from edenai_apis.features.ocr.invoice_parser import (
    CustomerInformationInvoice,
    InfosInvoiceParserDataClass,
    InvoiceParserDataClass,
    ItemLinesInvoice,
    LocaleInvoice,
    MerchantInformationInvoice,
    TaxesInvoice,
    BankInvoice,
)
from edenai_apis.features.ocr.receipt_parser import (
    CustomerInformation,
    InfosReceiptParserDataClass,
    ItemLines,
    Locale,
    MerchantInformation,
    ReceiptParserDataClass,
    Taxes,
    PaymentInformation,
)
from edenai_apis.loaders.data_loader import ProviderDataEnum
from edenai_apis.loaders.loaders import load_provider
from edenai_apis.utils.bounding_box import BoundingBox
from edenai_apis.utils.conversion import (
    combine_date_with_time,
    convert_string_to_number,
    retreive_first_number_from_string,
)
from apis.amazon.helpers import check_webhook_result
from edenai_apis.utils.exception import ProviderException
from edenai_apis.utils.types import (
    AsyncBaseResponseType,
    AsyncLaunchJobResponseType,
    ResponseType,
    AsyncPendingResponseType,
    AsyncResponseType,
)
from edenai_apis.utils.upload_s3 import upload_file_bytes_to_s3, USER_PROCESS
from io import BytesIO


class SubfeatureParser(Enum):
    RECEIPT = "receipt"
    INVOICE = "invoice"


T = TypeVar("T")


class Base64Api(ProviderInterface, OcrInterface):
    provider_name = "base64"

    def __init__(self, api_keys: Dict = {}) -> None:
        self.api_settings = load_provider(
            ProviderDataEnum.KEY, self.provider_name, api_keys=api_keys
        )
        self.api_key = self.api_settings["secret"]
        self.url = "https://base64.ai/api/scan"
        self.webhook_settings = load_provider(ProviderDataEnum.KEY, "webhooksite")
        self.webhook_token = self.webhook_settings.get("webhook_token")

    class Field:
        def __init__(self, document: dict) -> None:
            self.document = document

        def __getitem__(self, key) -> Any:
            return self.document.get("fields", {}).get(key, {}).get("value")

    def _get_response(self, response: requests.Response) -> Any:
        print(response.text)
        print(response.status_code)
        try:
            original_response = response.json()
            if response.status_code >= 400:
                message_error = original_response["message"]
                raise ProviderException(message_error, code=response.status_code)
            return original_response
        except Exception:
            raise ProviderException(response.text, code=response.status_code)

    def _extract_item_lignes(
        self, data, item_lines_type: Union[Type[ItemLines], Type[ItemLinesInvoice]]
    ) -> list:
        items_description = [
            value["value"]
            for key, value in data.items()
            if key.startswith("lineItem") and key.endswith("Description")
        ]
        items_quantity = [
            value["value"]
            for key, value in data.items()
            if key.startswith("lineItem") and key.endswith("Quantity")
        ]
        items_unit_price = [
            value["value"]
            for key, value in data.items()
            if key.startswith("lineItem") and key.endswith("UnitPrice")
        ]
        items_total_cost = [
            value["value"]
            for key, value in data.items()
            if key.startswith("lineItem") and key.endswith("LineTotal")
        ]

        items: Sequence[item_lines_type] = []
        for item in zip_longest(
            items_description,
            items_quantity,
            items_total_cost,
            items_unit_price,
            fillvalue=None,
        ):
            item_quantity = retreive_first_number_from_string(
                item[1]
            )  # avoid cases where the quantity is concatenated with a string
            items.append(
                item_lines_type(
                    description=item[0] if item[0] else "",
                    quantity=convert_string_to_number(item_quantity, float),
                    amount=convert_string_to_number(item[2], float),
                    unit_price=convert_string_to_number(item[3], float),
                )
            )
        return items

    def _format_invoice_document_data(self, data) -> InvoiceParserDataClass:
        fields = data[0].get("fields", [])

        items: Sequence[ItemLinesInvoice] = self._extract_item_lignes(
            fields, ItemLinesInvoice
        )

        default_dict = defaultdict(lambda: None)
        # ----------------------Merchant & customer informations----------------------#
        merchant_name = fields.get("companyName", default_dict).get("value")
        merchant_address = fields.get("from", default_dict).get("value")
        customer_name = fields.get("billTo", default_dict).get("value")
        customer_address = fields.get("address", default_dict).get(
            "value"
        )  # DEPRECATED need to be removed
        customer_mailing_address = fields.get("address", default_dict).get("value")
        customer_billing_address = fields.get("billTo", default_dict).get("value")
        customer_shipping_address = fields.get("shipTo", default_dict).get("value")
        customer_remittance_address = fields.get("soldTo", default_dict).get("value")
        # ---------------------- invoice  informations----------------------#
        invoice_number = fields.get("invoiceNumber", default_dict).get("value")
        invoice_total = fields.get("total", default_dict).get("value")
        invoice_total = convert_string_to_number(invoice_total, float)
        invoice_subtotal = fields.get("subtotal", default_dict).get("value")
        invoice_subtotal = convert_string_to_number(invoice_subtotal, float)
        amount_due = fields.get("balanceDue", default_dict).get("value")
        amount_due = convert_string_to_number(amount_due, float)
        discount = fields.get("discount", default_dict).get("value")
        discount = convert_string_to_number(discount, float)
        taxe = fields.get("tax", default_dict).get("value")
        taxe = convert_string_to_number(taxe, float)
        taxes: Sequence[TaxesInvoice] = [(TaxesInvoice(value=taxe, rate=None))]
        # ---------------------- payment informations----------------------#
        payment_term = fields.get("paymentTerms", default_dict).get("value")
        purchase_order = fields.get("purchaseOrder", default_dict).get("value")
        date = fields.get("invoiceDate", default_dict).get("value")
        time = fields.get("invoiceTime", default_dict).get("value")
        date = combine_date_with_time(date, time)
        due_date = fields.get("dueDate", default_dict).get("value")
        due_time = fields.get("dueTime", default_dict).get("value")
        due_date = combine_date_with_time(due_date, due_time)
        # ---------------------- bank and local informations----------------------#
        iban = fields.get("iban", default_dict).get("value")
        account_number = fields.get("accountNumber", default_dict).get("value")
        currency = fields.get("currency", default_dict).get("value")

        invoice_parser = InfosInvoiceParserDataClass(
            merchant_information=MerchantInformationInvoice(
                merchant_name=merchant_name,
                merchant_address=merchant_address,
                merchant_email=None,
                merchant_phone=None,
                merchant_website=None,
                merchant_fax=None,
                merchant_siren=None,
                merchant_siret=None,
                merchant_tax_id=None,
                abn_number=None,
                vat_number=None,
                pan_number=None,
                gst_number=None,
            ),
            customer_information=CustomerInformationInvoice(
                customer_name=customer_name,
                customer_address=customer_address,
                customer_email=None,
                customer_id=None,
                customer_mailing_address=customer_mailing_address,
                customer_remittance_address=customer_remittance_address,
                customer_shipping_address=customer_shipping_address,
                customer_billing_address=customer_billing_address,
                customer_service_address=None,
                customer_tax_id=None,
                pan_number=None,
                gst_number=None,
                vat_number=None,
                abn_number=None,
            ),
            invoice_number=invoice_number,
            invoice_total=invoice_total,
            invoice_subtotal=invoice_subtotal,
            amount_due=amount_due,
            discount=discount,
            taxes=taxes,
            payment_term=payment_term,
            purchase_order=purchase_order,
            date=date,
            due_date=due_date,
            locale=LocaleInvoice(
                currency=currency,
                language=None,
            ),
            bank_informations=BankInvoice(
                iban=iban,
                account_number=account_number,
                bsb=None,
                sort_code=None,
                vat_number=None,
                rooting_number=None,
                swift=None,
            ),
            item_lines=items,
        )

        standardized_response = InvoiceParserDataClass(extracted_data=[invoice_parser])

        return standardized_response

    def _format_receipt_document_data(self, data) -> ReceiptParserDataClass:
        fields = data[0].get("fields", [])

        items: Sequence[ItemLines] = self._extract_item_lignes(fields, ItemLines)

        default_dict = defaultdict(lambda: None)
        invoice_number = fields.get("receiptNo", default_dict)["value"]
        invoice_total = fields.get("total", default_dict)["value"]
        invoice_total = convert_string_to_number(invoice_total, float)
        date = fields.get("date", default_dict)["value"]
        time = fields.get("time", default_dict)["value"]
        date = combine_date_with_time(date, time)
        invoice_subtotal = fields.get("subtotal", default_dict)["value"]
        invoice_subtotal = convert_string_to_number(invoice_subtotal, float)
        customer_name = fields.get("shipTo", default_dict)["value"]
        merchant_name = fields.get("companyName", default_dict)["value"]
        merchant_address = fields.get("addressBlock", default_dict)["value"]
        currency = fields.get("currency", default_dict)["value"]
        card_number = fields.get("cardNumber", default_dict)["value"]
        card_type = fields.get("cardType", default_dict)["value"]

        taxe = fields.get("tax", default_dict)["value"]
        taxe = convert_string_to_number(taxe, float)
        taxes: Sequence[Taxes] = [(Taxes(taxes=taxe))]
        receipt_infos = {
            "payment_code": fields.get("paymentCode", default_dict)["value"],
            "host": fields.get("host", default_dict)["value"],
            "payment_id": fields.get("paymentId", default_dict)["value"],
            "card_type": card_type,
            "receipt_number": invoice_number,
        }

        receipt_parser = InfosReceiptParserDataClass(
            invoice_number=invoice_number,
            invoice_total=invoice_total,
            invoice_subtotal=invoice_subtotal,
            locale=Locale(currency=currency),
            merchant_information=MerchantInformation(
                merchant_name=merchant_name, merchant_address=merchant_address
            ),
            customer_information=CustomerInformation(customer_name=customer_name),
            payment_information=PaymentInformation(
                card_number=card_number, card_type=card_type
            ),
            date=str(date),
            time=str(time),
            receipt_infos=receipt_infos,
            item_lines=items,
            taxes=taxes,
        )

        standardized_response = ReceiptParserDataClass(extracted_data=[receipt_parser])

        return standardized_response

    def _send_ocr_document(self, file: str, model_type: str) -> Dict:
        file_ = open(file, "rb")
        image_as_base64 = (
            f"data:{mimetypes.guess_type(file)[0]};base64,"
            + base64.b64encode(file_.read()).decode()
        )
        file_.close()

        data = {"modelTypes": [model_type], "image": image_as_base64}

        headers = {"Content-type": "application/json", "Authorization": self.api_key}

        response = requests.post(url=self.url, headers=headers, json=data)

        if response.status_code != 200:
            raise ProviderException(response.text, code=response.status_code)

        return response.json()

    def _ocr_finance_document(
        self, ocr_file, document_type: SubfeatureParser
    ) -> ResponseType[T]:
        original_response = self._send_ocr_document(
            ocr_file, "finance/" + document_type.value
        )
        if document_type == SubfeatureParser.RECEIPT:
            standardized_response = self._format_receipt_document_data(
                original_response
            )
        elif document_type == SubfeatureParser.INVOICE:
            standardized_response = self._format_invoice_document_data(
                original_response
            )

        result = ResponseType[T](
            original_response=original_response,
            standardized_response=standardized_response,
        )
        return result

    def ocr__ocr(
        self,
        file: str,
        language: str,
        file_url: str = "",
    ):
        raise ProviderException(
            message="This provider is deprecated. You won't be charged for your call.",
            code=500,
        )

    def ocr__invoice_parser(
        self, file: str, language: str, file_url: str = ""
    ) -> ResponseType[InvoiceParserDataClass]:
        return self._ocr_finance_document(file, SubfeatureParser.INVOICE)

    def ocr__receipt_parser(
        self, file: str, language: str, file_url: str = ""
    ) -> ResponseType[ReceiptParserDataClass]:
        return self._ocr_finance_document(file, SubfeatureParser.RECEIPT)

    def ocr__identity_parser(
        self, file: str, file_url: str = ""
    ) -> ResponseType[IdentityParserDataClass]:
        file_ = open(file, "rb")

        image_as_base64 = (
            f"data:{mimetypes.guess_type(file)[0]};base64,"
            + base64.b64encode(file_.read()).decode()
        )

        payload = json.dumps({"image": image_as_base64})

        headers = {"Content-Type": "application/json", "Authorization": self.api_key}

        response = requests.post(url=self.url, headers=headers, data=payload)

        file_.close()

        original_response = self._get_response(response)

        items = []

        for document in original_response:
            image_id = [
                ItemIdentityParserDataClass(
                    value=doc.get("image", []), confidence=doc.get("confidence")
                )
                for doc in document["features"].get("faces", {})
            ]
            image_signature = [
                ItemIdentityParserDataClass(
                    value=doc.get("image", []), confidence=doc.get("confidence")
                )
                for doc in document["features"].get("signatures", {})
            ]
            given_names_dict = document["fields"].get("givenName", {}) or {}
            given_names_string = given_names_dict.get("value", "") or ""
            given_names = (
                given_names_string.split(" ") if given_names_string != "" else []
            )
            given_names_final = []
            for given_name in given_names:
                given_names_final.append(
                    ItemIdentityParserDataClass(
                        value=given_name,
                        confidence=document["fields"]
                        .get("givenName", {})
                        .get("confidence"),
                    )
                )

            country = get_info_country(
                key=InfoCountry.ALPHA3,
                value=document["fields"].get("countryCode", {}).get("value", ""),
            )
            if country:
                country["confidence"] = (
                    document["fields"].get("countryCode", {}).get("confidence")
                )

            items.append(
                InfosIdentityParserDataClass(
                    document_type=ItemIdentityParserDataClass(
                        value=document["fields"].get("documentType", {}).get("value"),
                        confidence=document["fields"]
                        .get("documentType", {})
                        .get("confidence"),
                    ),
                    last_name=ItemIdentityParserDataClass(
                        value=document["fields"].get("familyName", {}).get("value"),
                        confidence=document["fields"]
                        .get("familyName", {})
                        .get("confidence"),
                    ),
                    given_names=given_names_final,
                    birth_date=ItemIdentityParserDataClass(
                        value=format_date(
                            document["fields"].get("dateOfBirth", {}).get("value")
                        ),
                        confidence=document["fields"]
                        .get("dateOfBirth", {})
                        .get("confidence"),
                    ),
                    country=country or Country.default(),
                    document_id=ItemIdentityParserDataClass(
                        value=document["fields"].get("documentNumber", {}).get("value"),
                        confidence=document["fields"]
                        .get("documentNumber", {})
                        .get("confidence"),
                    ),
                    age=ItemIdentityParserDataClass(
                        value=str(document["fields"].get("age", {}).get("value")),
                        confidence=document["fields"].get("age", {}).get("confidence"),
                    ),
                    nationality=ItemIdentityParserDataClass(
                        value=document["fields"].get("nationality", {}).get("value"),
                        confidence=document["fields"]
                        .get("nationality", {})
                        .get("confidence"),
                    ),
                    issuing_state=ItemIdentityParserDataClass(
                        value=document["fields"].get("issuingState", {}).get("value"),
                        confidence=document["fields"]
                        .get("issuingState", {})
                        .get("confidence"),
                    ),
                    image_id=image_id,
                    image_signature=image_signature,
                    gender=ItemIdentityParserDataClass(
                        value=document["fields"].get("sex", {}).get("value"),
                        confidence=document["fields"].get("sex", {}).get("confidence"),
                    ),
                    expire_date=ItemIdentityParserDataClass(
                        value=format_date(
                            document["fields"].get("expirationDate", {}).get("value")
                        ),
                        confidence=document["fields"]
                        .get("expirationDate", {})
                        .get("confidence"),
                    ),
                    issuance_date=ItemIdentityParserDataClass(
                        value=format_date(
                            document["fields"].get("issueDate", {}).get("value")
                        ),
                        confidence=document["fields"]
                        .get("issueDate", {})
                        .get("confidence"),
                    ),
                    address=ItemIdentityParserDataClass(
                        value=document["fields"].get("address", {}).get("value"),
                        confidence=document["fields"]
                        .get("address", {})
                        .get("confidence"),
                    ),
                    birth_place=ItemIdentityParserDataClass(
                        value=None, confidence=None
                    ),
                    mrz=ItemIdentityParserDataClass(),
                )
            )

        standardized_response = IdentityParserDataClass(extracted_data=items)

        return ResponseType[IdentityParserDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )

    def image__face_compare(
        self,
        file1: str,
        file2: str,
        file1_url: str = "",
        file2_url: str = "",
    ) -> ResponseType[FaceCompareDataClass]:
        url = "https://base64.ai/api/face"

        headers = {"Authorization": self.api_key, "Content-Type": "application/json"}

        if file1_url and file2_url:
            payload = json.dumps({"url": file1_url, "queryUrl": file2_url})
        else:
            file_reference_ = open(file1, "rb")
            file_query_ = open(file2, "rb")
            image_reference_as_base64 = (
                f"data:{mimetypes.guess_type(file1)[0]};base64,"
                + base64.b64encode(file_reference_.read()).decode()
            )
            image_query_as_base64 = (
                f"data:{mimetypes.guess_type(file2)[0]};base64,"
                + base64.b64encode(file_query_.read()).decode()
            )
            payload = json.dumps(
                {
                    "document": image_reference_as_base64,
                    "query": image_query_as_base64,
                }
            )

        response = requests.request("POST", url, headers=headers, data=payload)
        original_response = self._get_response(response)

        faces = []
        for matching_face in original_response.get("matches", []):
            faces.append(
                FaceMatch(
                    confidence=matching_face.get("confidence") or 0,
                    bounding_box=FaceCompareBoundingBox(
                        top=matching_face.get("top"),
                        left=matching_face.get("left"),
                        height=matching_face.get("height"),
                        width=matching_face.get("width"),
                    ),
                )
            )
        standardized_response = FaceCompareDataClass(items=faces)

        return ResponseType[FaceCompareDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )

    def ocr__data_extraction(
        self, file: str, file_url: str = ""
    ) -> ResponseType[DataExtractionDataClass]:
        with open(file, "rb") as f_stream:
            image_as_base64 = (
                f"data:{mimetypes.guess_type(file)[0]};base64,"
                + base64.b64encode(f_stream.read()).decode()
            )

            payload = json.dumps({"image": image_as_base64})
            headers = {
                "Content-Type": "application/json",
                "Authorization": self.api_key,
            }

            response = requests.post(url=self.url, headers=headers, data=payload)

        original_response = self._get_response(response)

        items: Sequence[ItemDataExtraction] = []

        for document in original_response:
            for _, value in document.get("fields", {}).items():
                try:
                    bbox = BoundingBox.from_normalized_vertices(
                        normalized_vertices=value.get("location")
                    )
                except ValueError:
                    bbox = BoundingBox.unknown()

                items.append(
                    ItemDataExtraction(
                        key=value.get("key"),
                        value=value.get("value"),
                        confidence_score=value.get("confidence"),
                        bounding_box=bbox,
                    )
                )

        standardized_response = DataExtractionDataClass(fields=items)

        return ResponseType(
            original_response=original_response,
            standardized_response=standardized_response,
        )

    def ocr__bank_check_parsing(
        self, file: str, file_url: str = ""
    ) -> ResponseType[BankCheckParsingDataClass]:
        with open(file, "rb") as fstream:
            image_as_base64 = (
                f"data:{mimetypes.guess_type(file)[0]};base64,"
                + base64.b64encode(fstream.read()).decode()
            )

            payload = json.dumps({"modelTypes": ["finance/"], "image": image_as_base64})
            headers = {
                "Content-Type": "application/json",
                "Authorization": self.api_key,
            }

            response = requests.post(url=self.url, headers=headers, data=payload)
            original_response = self._get_response(response)

            items: Sequence[ItemBankCheckParsingDataClass] = []
            for fields_not_formated in original_response:
                fields = Base64Api.Field(fields_not_formated)
                items.append(
                    ItemBankCheckParsingDataClass(
                        amount=fields["amount"],
                        amount_text=None,
                        bank_name=None,
                        bank_address=None,
                        date=fields["date"],
                        memo=None,
                        payer_address=fields["address"],
                        payer_name=fields["payee"],
                        receiver_name=None,
                        receiver_address=None,
                        currency=fields["currency"],
                        micr=MicrModel(
                            raw=fields["micr"],
                            account_number=fields["accountMumber"],
                            serial_number=None,
                            check_number=fields["checkNumber"],
                            routing_number=fields["routingNumber"],
                        ),
                    )
                )
            return ResponseType[BankCheckParsingDataClass](
                original_response=original_response,
                standardized_response=BankCheckParsingDataClass(extracted_data=items),
            )

    def ocr__anonymization_async__launch_job(
        self, file: str, file_url: str = ""
    ) -> AsyncLaunchJobResponseType:
        data_job_id = {}
        file_ = open(file, "rb")
        image_as_base64 = (
            f"data:{mimetypes.guess_type(file)[0]};base64,"
            + base64.b64encode(file_.read()).decode()
        )
        file_.close()
        payload = json.dumps(
            {
                "image": image_as_base64,
                "settings": {
                    "redactions": {
                        "fields": [
                            "name",
                            "givenName",
                            "familyName",
                            "organization",
                            "documentNumber",
                            "address",
                            "date",
                            "dateOfBirth",
                            "issueDate",
                            "expirationDate",
                            "vin" "total",
                            "tax",
                        ],
                        "faces": True,
                        "signatures": True,
                    }
                },
            }
        )

        headers = {"Content-Type": "application/json", "Authorization": self.api_key}

        response = requests.post(url=self.url, headers=headers, data=payload)

        original_response = self._get_response(response)

        job_id = "document_anonymization_base64" + str(uuid.uuid4())
        data_job_id[job_id] = original_response
        requests.post(
            url=f"https://webhook.site/{self.webhook_token}",
            data=json.dumps(data_job_id),
            headers={"content-type": "application/json"},
        )

        return AsyncLaunchJobResponseType(provider_job_id=job_id)

    def ocr__anonymization_async__get_job_result(
        self, provider_job_id: str
    ) -> AsyncBaseResponseType[AnonymizationAsyncDataClass]:
        wehbook_result, response_status = check_webhook_result(
            provider_job_id, self.webhook_settings
        )

        if response_status != 200:
            raise ProviderException(wehbook_result, code=response_status)

        result_object = (
            next(
                filter(
                    lambda response: provider_job_id in response["content"],
                    wehbook_result,
                ),
                None,
            )
            if wehbook_result
            else None
        )

        if not result_object or not result_object.get("content"):
            raise ProviderException("Provider returned an empty response")

        try:
            original_response = json.loads(result_object["content"]).get(
                provider_job_id, None
            )
        except json.JSONDecodeError:
            raise ProviderException("An error occurred while parsing the response.")

        if original_response is None:
            return AsyncPendingResponseType[AnonymizationAsyncDataClass](
                provider_job_id=provider_job_id
            )
        # Extract the B64 redacted document
        redacted_document = original_response[0].get("redactedDocument")
        # document_mimetype = original_response[0]['features']['properties']['mimeType']

        # # Use the mimetypes module to guess the file extension based on the MIME type
        # extension = mimetypes.guess_extension(document_mimetype)

        # Extract the base64-encoded data from 'redacted_document'
        base64_data = redacted_document.split(";base64,")[1]

        content_bytes = base64.b64decode(base64_data)
        resource_url = upload_file_bytes_to_s3(
            BytesIO(content_bytes), ".png", USER_PROCESS
        )
        return AsyncResponseType[AnonymizationAsyncDataClass](
            original_response=original_response,
            standardized_response=AnonymizationAsyncDataClass(
                document=base64_data, document_url=resource_url
            ),
            provider_job_id=provider_job_id,
        )

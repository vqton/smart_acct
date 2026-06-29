"""Digital signing service for Vietnamese e-invoices."""

import logging
from typing import Optional, Tuple
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from domain import Result, EInvoice, ValidationError

logger = logging.getLogger(__name__)


class SigningService:
    """Digital signing service for e-invoices using RSA-SHA256.

    Handles invoice signing, signature verification, and key pair
    generation per Vietnam e-invoice standards.
    """

    SIGNATURE_ALGORITHM = "RSA-SHA256"
    KEY_SIZE = 2048

    def __init__(
        self,
        private_key: Optional[RSAPrivateKey] = None,
        public_key: Optional[RSAPublicKey] = None,
    ):
        self._private_key = private_key
        self._public_key = public_key
        if private_key:
            logger.info("SigningService initialized with private key loaded")
        else:
            logger.info("SigningService initialized without keys (signing disabled)")

    @staticmethod
    def generate_key_pair(key_size: int = KEY_SIZE) -> Tuple[RSAPrivateKey, RSAPublicKey]:
        """Generate a new RSA key pair for e-invoice signing."""
        logger.info("Generating RSA key pair: key_size=%d", key_size)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        public_key = private_key.public_key()
        logger.info("RSA key pair generated successfully")
        return private_key, public_key

    @staticmethod
    def serialize_private_key(key: RSAPrivateKey) -> bytes:
        """Serialize a private key to PEM bytes."""
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

    @staticmethod
    def serialize_public_key(key: RSAPublicKey) -> bytes:
        """Serialize a public key to PEM bytes."""
        return key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def set_private_key(self, key: RSAPrivateKey) -> None:
        """Set or replace the signing private key."""
        self._private_key = key
        logger.info("Private key updated")

    def set_public_key(self, key: RSAPublicKey) -> None:
        """Set or replace the verification public key."""
        self._public_key = key
        logger.info("Public key updated")

    def sign_invoice(self, invoice: EInvoice) -> Result:
        """Digitally sign an e-invoice and return the signed XML string.

        In production, this serializes the invoice to XML per GDT format,
        computes the digest, and signs with the private key. Currently
        returns a stub signature envelope.
        """
        logger.info(
            "Signing invoice: series=%s, number=%s",
            invoice.invoice_series, invoice.invoice_number,
        )
        if not self._private_key:
            return Result.failure(
                ValidationError("No private key configured for signing")
            )

        signed_xml = (
            f'<?xml version="1.0" encoding="UTF-8"?>'
            f'<Invoice>'
            f'<InvoiceNumber>{invoice.invoice_number}</InvoiceNumber>'
            f'<InvoiceSeries>{invoice.invoice_series}</InvoiceSeries>'
            f'<SellerTaxCode>{invoice.seller_tax_code}</SellerTaxCode>'
            f'<BuyerTaxCode>{invoice.buyer_tax_code or ""}</BuyerTaxCode>'
            f'<Total>{invoice.grand_total}</Total>'
            f'<Signature algorithm="{self.SIGNATURE_ALGORITHM}">'
            f'STUB-SIGNATURE-{datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")}'
            f'</Signature>'
            f'</Invoice>'
        )
        logger.info("Invoice %s-%s signed successfully", invoice.invoice_series, invoice.invoice_number)
        return Result.success({
            "signed_xml": signed_xml,
            "algorithm": self.SIGNATURE_ALGORITHM,
            "signed_at": datetime.now(timezone.utc).isoformat(),
        })

    def verify_signature(self, signed_content: str) -> bool:
        """Verify the digital signature on signed invoice content.

        Returns True if the signature is valid, False otherwise.
        Current stub implementation checks for the presence of a
        signature envelope in the XML.
        """
        logger.info("Verifying digital signature")
        if not signed_content:
            logger.warning("Verify called with empty content")
            return False

        has_signature = (
            "<Signature" in signed_content
            and "</Signature>" in signed_content
            and self.SIGNATURE_ALGORITHM in signed_content
        )
        logger.info(
            "Signature verification %s",
            "passed" if has_signature else "failed",
        )
        return has_signature

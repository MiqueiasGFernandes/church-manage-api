import unittest

from modules.organizations.domain.model import (
    CNPJ,
    ChurchName,
    ChurchSlug,
    EmailAddress,
    InvalidFieldError,
    PhoneNumber,
)


class OrganizationValueObjectsTest(unittest.TestCase):
    def test_normalizes_business_values(self) -> None:
        self.assertEqual(ChurchName("  Igreja   Central  ").value, "Igreja Central")
        self.assertEqual(EmailAddress(" CONTATO@EXEMPLO.COM.BR ").value, "contato@exemplo.com.br")
        self.assertEqual(PhoneNumber("+55 (11) 99999-9999").value, "+5511999999999")
        self.assertEqual(CNPJ("11.222.333/0001-81").value, "11222333000181")

    def test_rejects_invalid_and_reserved_slugs(self) -> None:
        for slug in ("-igreja", "igreja--central", "igreja_central", "admin"):
            with self.subTest(slug=slug), self.assertRaises(InvalidFieldError):
                ChurchSlug(slug)

    def test_rejects_invalid_cnpj_check_digits(self) -> None:
        with self.assertRaises(InvalidFieldError):
            CNPJ("12.345.678/0001-90")


if __name__ == "__main__":
    unittest.main()

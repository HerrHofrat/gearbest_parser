"""Module to parse gearbest site"""

import logging
import re
import json

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup


_LOGGER = logging.getLogger(__name__)

class GearbestParser:
    """Parses the og data of an Gearbest item"""
    def __init__(self):
        self._converter = CurrencyConverter()
        self.update_conversion_list()

    def load(self, url, currency=None):
        """Load an url an get an GearbestItem for that"""
        page = self._load_url(url)
        soup = BeautifulSoup(page, 'lxml')
        meta_data = {}
        for meta in soup.findAll("meta"):
            name = meta.get('name', None)
            if name is None:
                name = meta.get('property', None)
            content = meta.get('content', None)
            meta_data[name] = content
        return GearbestItem(meta_data, self._converter, currency)

    def update_conversion_list(self):
        """Load the conversion array from Gearbest"""
        url = "https://order.gearbest.com/data-cache/currency_huilv.js?v=20171102105238"
        page = self._load_url(url)
        search_object = re.search("({[^}]*})", page, re.M|re.I)
        if search_object:
            self._converter.set_conversion_list(json.loads(search_object.group(1)))

    def _load_url(self, url):
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(req).read().decode('utf-8')
        return page

class CurrencyConverter:
    """A simple currency converter."""
    def __init__(self):
        self._conversion_list = {}

    def set_conversion_list(self, conversion_list):
        """Set the actual conversion_list."""
        self._conversion_list = conversion_list

    def is_supported_currency(self, currency):
        """Check if the currency is part of the conversion list."""
        return currency in self._conversion_list

    def convert(self, amount, from_currency, to_currency):
        """Convert the amount from a currency to another."""
        if self.is_supported_currency(from_currency) and self.is_supported_currency(to_currency):
            return float(amount) / float(self._conversion_list.get(from_currency)) * \
                   float(self._conversion_list.get(to_currency))

class GearbestItem:
    """Representation of an item at Gearbest"""
    def __init__(self, meta_data, converter, currency=None):
        self._name = meta_data.get("og:title", None)
        self._description = meta_data.get("og:description", None)
        self._image = meta_data.get("og:image", None)
        self._price = meta_data.get("og:price:amount", None)
        self._currency = meta_data.get("og:price:currency", None)

        if currency is not None and \
           currency is not self._currency and \
           converter.is_supported_currency(currency):
            self._price = "{0:.2f}".format(converter.convert(self._price, self._currency, currency))
            self._currency = currency


    @property
    def name(self):
        """The name of the item."""
        return self._name

    @property
    def description(self):
        """The description of the item."""
        return self._description

    @property
    def image(self):
        """The image of this item."""
        return self._image

    @property
    def price(self):
        """The price of this item."""
        return self._price

    @property
    def currency(self):
        """The currency of this item."""
        return self._currency

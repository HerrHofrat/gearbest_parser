"""Module to parse gearbest site"""

import re
import json
from datetime import datetime

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

class GearbestParser:
    """Parses the og data of an Gearbest item"""
    def __init__(self):
        self._converter = None

    @staticmethod
    def is_valid_url(url):
        """Check if the provided url is a valid gearbest url"""
        search_object = re.match(r"^(https?:\/\/(www\.)?gearbest\.com\/).*$",
                                 url, re.M|re.I)
        return search_object is not None

    def set_currency_converter(self, converter):
        """Set a currency converter instance"""
        self._converter = converter

    def load(self, item_id=None, url=None, currency=None):
        """Load an url an get an GearbestItem for that"""
        if item_id is not None:
            url = "https://www.gearbest.com/q/pp_{}.html".format(item_id)

        if url is not None and GearbestParser.is_valid_url(url):
            return GearbestItem(url, self._get_meta_data, self._converter, currency)
        else:
            return None

    def _get_meta_data(self, url):
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(req).read().decode('utf-8')
        soup = BeautifulSoup(page, 'html.parser')
        meta_data = {}
        for meta in soup.findAll("meta"):
            name = meta.get('name', None)
            if name is None:
                name = meta.get('property', None)
            content = meta.get('content', None)
            meta_data[name] = content
        return meta_data

class CurrencyConverter:
    """A simple currency converter."""
    def __init__(self):
        self._conversion_list = {}

    def update(self):
        """Load the conversion array from Gearbest"""
        try:
            url = "https://www.gearbest.com/exchange-rate?v=" \
                  "{:%Y%m%d%H%M%S}".format(datetime.now())
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            page = urlopen(req).read().decode('utf-8')
            search_object = re.search(r"(\[[^\]]*\])", page, re.M|re.I)
            data = json.loads(search_object.group(1))
            for element in data:
                self._conversion_list[element['currencyCode']] = element['currencyRate']
        except:
            self._conversion_list = {}


    def is_supported_currency(self, currency):
        """Check if the currency is part of the conversion list."""
        return currency in self._conversion_list

    def convert(self, amount, from_currency, to_currency):
        """Convert the amount from a currency to another."""
        if self.is_supported_currency(from_currency) and self.is_supported_currency(to_currency):
            return float(amount) / float(self._conversion_list.get(from_currency)) * \
                   float(self._conversion_list.get(to_currency))
        else:
            return 0

class GearbestItem:
    """Representation of an item at Gearbest"""
    def __init__(self, url, loader, converter, currency=None):
        self._name = None
        self._description = None
        self._image = None
        self._price = None
        self._currency = None
        self._url = url
        self._override_currency = currency
        self._loader = loader
        self._converter = converter

    def update(self):
        """Reload properties"""
        meta_data = self._loader(self._url)

        self._name = meta_data.get("og:title", None)
        search_object = re.search(r"^(.*)( ?)-\$[0-9.]* Online Shopping\| GearBest\.com",
                                  self._name, re.M|re.I)
        if search_object:
            self._name = search_object.group(1).strip()
        self._description = meta_data.get("og:description", None)
        self._image = meta_data.get("og:image", None)
        self._price = meta_data.get("og:price:amount", None)
        self._currency = meta_data.get("og:price:currency", None)

        if self._override_currency is not None and \
           self._override_currency is not self._currency and \
           self._converter is not None and \
           self._converter.is_supported_currency(self._override_currency):
            self._price = "{0:.2f}".format(
                self._converter.convert(self._price, self._currency, self._override_currency))
            self._currency = self._override_currency

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

    @property
    def url(self):
        """The url of this item."""
        return self._url

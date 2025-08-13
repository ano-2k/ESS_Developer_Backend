from django.utils import timezone
from decimal import Decimal
from io import BytesIO
from django.db import models
from django.forms import ValidationError
import requests
import barcode
from django.core.files.base import ContentFile
from barcode.writer import ImageWriter


# Measuring Unit Choices
MEASURING_UNIT_CHOICES = [
    ('UNT', 'Units'),
    ('UGS', 'US Gallons'),
    ('KGS', 'Kilograms'),
    ('LTR', 'Liters'),
    ('AAN', 'Aanna'),
    ('ACS', 'Accessories'),
    ('AC', 'Acre'),
    ('AMP', 'Ampoule'),
    ('BAG', 'Bags'),
    ('BAL', 'Bale'),
    ('BALL', 'Balls'),
    ('BAR', 'Barni'),
    ('BOU', 'Billions Of Units'),
    ('BLISTER', 'Blister'),
    ('BOLUS', 'Bolus'),
    ('BK', 'Book'),
    ('BOR', 'Bora'),
    ('BTL', 'Bottles'),
    ('BOX', 'Box'),
    ('BRASS', 'Brass'),
    ('BRICK', 'Brick'),
    ('BCK', 'Buckets'),
    ('BKL', 'Buckles'),
    ('BUN', 'Bunches'),
    ('BDL', 'Bundles'),
    ('CAN', 'Cans'),
    ('CAP', 'Cap'),
    ('CPS', 'Capsules'),
    ('CT', 'Carat'),
    ('CTS', 'Carats'),
    ('CARD', 'Card'),
    ('CTN', 'Cartons'),
    ('CASE', 'Case'),
    ('CMS', 'Centimeter'),
    ('CNT', 'Cents'),
    ('CHAIN', 'Chain'),
    ('CHOKA', 'Choka'),
    ('CHUDI', 'Chudi'),
    ('CLT', 'Cloth'),
    ('COIL', 'Coil'),
    ('CONT', 'Container'),
    ('COPY', 'Copy'),
    ('COURSE', 'Course'),
    ('CRT', 'Crate'),
    ('CRM', 'Cream'),
    ('CCM', 'Cubic Centimeter'),
    ('CUFT', 'Cubic Feet'),
    ('CFM', 'Cubic Feet Per Minute'),
    ('CFT', 'Cubic Foot'),
    ('CBM', 'Cubic Meter'),
    ('CUP', 'Cup'),
    ('CV', 'Cv'),
    ('DAILY', 'Daily'),
    ('DANGLER', 'Dangler'),
    ('DAY', 'Day'),
    ('DEZ', 'Daze'),
    ('DOZ', 'Dozen'),
    ('DROP', 'Drop'),
    ('DRM', 'Drum'),
    ('EA', 'Each'),
    ('EACH', 'Each'),
    ('FT', 'Feet'),
    ('FT2', 'Feet Square'),
    ('FIT', 'Fit'),
    ('FLD', 'Fold'),
    ('FREE', 'Free'),
    ('FTS', 'Fts'),
    ('GEL', 'Gel'),
    ('GLS', 'Glasses'),
    ('GMS', 'Grams'),
    ('GGR', 'Great Gross'),
    ('GRS', 'Gross'),
    ('GYD', 'Gross Yards'),
    ('HF', 'Half'),
    ('HEGAR', 'Hanger'),
    ('HA', 'Hectare'),
    ('HMT', 'Helmet'),
    ('HRS', 'Hours'),
    ('INJECTION', 'Injection'),
    ('IN', 'Inches'),
    ('ITEM ID', 'Item Id'),
    ('JAR', 'Jars'),
    ('JL', 'Jhal'),
    ('JO', 'Jhola'),
    ('JHL', 'Jhola Jhal'),
    ('JOB', 'Job'),
    ('KT', 'Katta'),
    ('KGS', 'Kilograms'),
    ('KLR', 'Kiloliter'),
    ('KME', 'Kilometre'),
    ('KMS', 'Kilometres'),
    ('KVA', 'Kilovolt-amp'),
    ('KW', 'Kilowatt'),
    ('KIT', 'Kit'),
    ('LAD', 'Ladi'),
    ('LENG', 'Length'),
    ('LBS', 'Libra Pondo'),
    ('LTR', 'Litre'),
    ('LOT', 'Lot'),
    ('LS', 'Lump Sum'),
    ('MAN-DAY', 'Man-days'),
    ('MRK', 'Mark'),
    ('MBPS', 'Mbps'),
    ('MTR', 'Meters'),
    ('MMBTU', 'Metric Million British Thermal Unit'),
    ('MTON', 'Metric Ton'),
    ('MG', 'Microgram'),
    ('M/C', 'Millicoulomb'),
    ('MLG', 'Milligram'),
    ('MLT', 'Millilitre'),
    ('MM', 'Millimeter'),
    ('MINS', 'Minutes'),
    ('MONTH', 'Month'),
    ('MON', 'Months'),
    ('MORA', 'Mora'),
    ('NIGHT', 'Night'),
    ('NONE', 'None'),
    ('NOS', 'Numbers'),
    ('OINT', 'Ointment'),
    ('OTH', 'Others'),
    ('OR', 'Outer'),
    ('PKG', 'Package'),
    ('PKT', 'Packets'),
    ('PAC', 'Packs'),
    ('PAD', 'Pad'),
    ('PADS', 'Pads'),
    ('PAGE', 'Pages'),
    ('PAIR', 'Pair'),
    ('PRS', 'Pairs'),
    ('PATTA', 'Patta'),
    ('PAX', 'Pax'),
    ('PER', 'Per'),
    ('PWP', 'Per Watt Peak'),
    ('PERSON', 'Persons'),
    ('PET', 'Peti'),
    ('PHILE', 'Phile'),
    ('PCS', 'Pieces'),
    ('PLT', 'Plates'),
    ('PT', 'Point'),
    ('PRT', 'Portion'),
    ('POCH', 'Pouch'),
    ('QUAD', 'Quad'),
    ('QTY', 'Quantity'),
    ('QTL', 'Quintal'),
    ('RTI', 'Ratti'),
    ('REAM', 'Ream'),
    ('REEL', 'Reel'),
    ('RIM', 'Rim'),
    ('ROL', 'Rolls'),
    ('ROOM', 'Room'),
    ('RFT', 'Running Foot'),
    ('RMT', 'Running Meter'),
    ('RS', 'Rupees'),
    ('SAC', 'Sachet'),
    ('SEC', 'Seconds'),
    ('SEM', 'Semester'),
    ('SSN', 'Session'),
    ('SET', 'Sets'),
    ('SHEET', 'Sheet'),
    ('SKINS', 'Skins'),
    ('SLEVES', 'Sleeves'),
    ('SPRAY', 'Spray'),
    ('SQCM', 'Square Centimeters'),
    ('SQF', 'Square Feet'),
    ('SQY', 'Square Yards'),
    ('SARAM', 'Saram'),
    ('STICKER', 'Stickers'),
    ('STONE', 'Stone'),
    ('STRP', 'Strips'),
    ('SYRP', 'Syrup'),
    ('TBS', 'Tablets'),
    ('TGM', 'Ten Gross'),
    ('TKT', 'Ticket'),
    ('TIN', 'Tin'),
    ('TON', 'Tonnes'),
    ('TRY', 'Trays'),
    ('TRIP', 'Trp'),
    ('TRK', 'Truck'),
    ('TUB', 'Tubes'),
    ('UNT', 'Units'),
    ('UGS', 'US Gallons'),
    ('VIAL', 'Vials'),
    ('W', 'Watt'),
    ('WEEK', 'Week'),
    ('YDS', 'Yards'),
    ('YRS', 'Years'),
]

# GST Tax Rate Choices
GST_TAX_CHOICES = [
    ('exempted', 'Exempted'),
    ('0', 'GST @ 0%'),
    ('0.1', 'GST @ 0.1%'),
    ('0.25', 'GST @ 0.25%'),
    ('1.5', 'GST @ 1.5%'),
    ('3', 'GST @ 3%'),
    ('5', 'GST @ 5%'),
    ('6', 'GST @ 6%'),
    ('12', 'GST @ 12%'),
    ('13.8', 'GST @ 13.8%'),
    ('18', 'GST @ 18%'),
    ('14_12', 'GST @ 14% + Cess @ 12%'),
    ('28', 'GST @ 28%'),
    ('28_12', 'GST @ 28% + Cess @ 12%'),
    ('28_60', 'GST @ 28% + Cess @ 60%'),
]


class GSTTax(models.Model):
    """Stores GST tax rates and cess percentages in the database"""
    name = models.CharField(max_length=50, unique=True)  # Example: "GST @ 18%"
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="GST Rate (%)")  # Example: 18.00
    cess_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Cess Rate (%)")  # Example: 12.00

    def __str__(self):
        if self.cess_rate > 0:
            return f"{self.name} (GST: {self.gst_rate}%, Cess: {self.cess_rate}%)"
        return f"{self.name} (GST: {self.gst_rate}%)"
    
class HSNCode(models.Model):
    hsn_code = models.CharField(max_length=20, primary_key=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.hsn_code} - {self.description}"
    
class SACCode(models.Model):
    sac_code = models.CharField(max_length=20, unique=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.sac_code} - {self.description}" 

# **Product Item Model**
class ProductItem(models.Model):
    """ Combined ProductItem, StockDetail, and PricingDetails Models """

    # **Product Item Fields**
    item_name = models.CharField(max_length=255)
    product_code = models.CharField(max_length=50, unique=True, blank=True, null=True)# Auto-generate
    gst_tax_rate = models.CharField(max_length=10, choices=GST_TAX_CHOICES, blank=True, null=True)
    measuring_unit = models.CharField(max_length=10, choices=MEASURING_UNIT_CHOICES)
    opening_stock = models.DecimalField(max_digits=10, decimal_places=2)
    stock_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    low_stock_warning = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    as_of_date = models.DateField(default=timezone.now)
    stock_image = models.ImageField(upload_to="stock_images/", blank=True, null=True)

    # **Pricing Details Fields**
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sales_price_without_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sales_price_with_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    final_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # **Stock Detail Fields**
    barcode_image = models.ImageField(upload_to="barcodes/", blank=True, null=True)  # Store barcode image
    hsn_code = models.CharField(max_length=10, default="UNKNOWN")
    # Foreign Key Relationship with GST Tax
    gst_tax = models.ForeignKey("GSTTax", on_delete=models.SET_NULL, null=True, blank=True, related_name="products")

    def save(self, *args, **kwargs):
        """ Handle saving logic for combined model """
        self.generate_item_code()  # Generates item code
        self.generate_barcode()  # Generates barcode image
        self.check_low_stock()  # Check low stock warning
        self.calculate_pricing()  # Calculate pricing based on tax
        super().save(*args, **kwargs)

    def generate_item_code(self):
     if not self.product_code or not self.product_code.startswith("ITM"):
        last_item = ProductItem.objects.filter(product_code__startswith="ITM").order_by("-id").first()
        try:
            next_number = (
                1 if not last_item else int(last_item.product_code[3:]) + 1
            )
        except ValueError:
            next_number = 1
        self.product_code = f"ITM{next_number:05d}"


    def generate_barcode(self):
        """ Generate a barcode from the product_code and store it as an image """
        if not self.product_code:
            return  # Ensure product_code exists

        barcode_class = barcode.get_barcode_class("code128")  # Supports alphanumeric codes
        barcode_instance = barcode_class(self.product_code, writer=ImageWriter())

        buffer = BytesIO()
        barcode_instance.write(buffer)
        buffer.seek(0)

        filename = f"{self.product_code}.png"
        self.barcode_image.save(filename, ContentFile(buffer.read()), save=False)

    def check_low_stock(self):
        """ Set low stock warning flag """
        self.low_stock_warning = self.opening_stock < self.stock_threshold

    def calculate_pricing(self):
     """ Calculate the pricing with or without tax """
     gst_rate = Decimal(0)
     if self.gst_tax:
        gst_rate = Decimal(self.gst_tax.gst_rate) if self.gst_tax.gst_rate != 'exempted' else Decimal(0)

    # If sales_price_with_tax is provided, calculate sales_price_without_tax and store final_total
     if self.sales_price_with_tax is not None:
        # Calculate sales_price_without_tax from sales_price_with_tax
        self.sales_price_without_tax = self.sales_price_with_tax / (Decimal(1) + gst_rate / Decimal(100))
        self.final_total = self.sales_price_with_tax  # Set final_total to sales_price_with_tax
        self.sales_price_with_tax = self.sales_price_with_tax  # Keep the same value for sales_price_with_tax
        self.sales_price_without_tax = None  # Set sales_price_without_tax to null

    # If sales_price_without_tax is provided, calculate sales_price_with_tax and store final_total
     elif self.sales_price_without_tax is not None:
        # Calculate sales_price_with_tax from sales_price_without_tax
        self.sales_price_with_tax = self.sales_price_without_tax * (Decimal(1) + gst_rate / Decimal(100))
        self.final_total = self.sales_price_with_tax  # Set final_total to sales_price_with_tax
        self.sales_price_without_tax = self.sales_price_without_tax  # Keep the same value for sales_price_without_tax
        self.sales_price_with_tax = None  # Set sales_price_with_tax to null

     else:
        # If neither price is provided, set final_total to None or handle accordingly
        self.final_total = None


class ServiceItem(models.Model):
    """ Combined ServiceItem and OtherDetails Models """

    # **Service Item Fields**
    service_name = models.CharField(max_length=255)
    sales_price_without_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sales_price_with_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gst_tax_rate = models.CharField(max_length=10, choices=GST_TAX_CHOICES)
    opening_stock = models.DecimalField(max_digits=10, decimal_places=2,default=1)
    measuring_unit = models.CharField(max_length=10, choices=MEASURING_UNIT_CHOICES)
    service_code = models.CharField(max_length=50, unique=True)
    final_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    service_description = models.TextField(blank=True, null=True)

    # **Other Details Fields**
    sac_code = models.CharField(max_length=20, default="default_sac_code")
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """ Calculate the final total based on GST tax rate and store the value """
        gst_rate = Decimal(self.gst_tax_rate) if self.gst_tax_rate != 'exempted' else Decimal(0)

        if self.sales_price_with_tax is not None:
            # If sales_price_with_tax is provided, calculate sales_price_without_tax and store final total
            self.sales_price_without_tax = self.sales_price_with_tax / (Decimal(1) + gst_rate / Decimal(100))
            self.final_total = self.sales_price_with_tax  # Set final_total to sales_price_with_tax
            self.sales_price_with_tax = self.sales_price_with_tax  # Keep the same value for sales_price_with_tax
            self.sales_price_without_tax = None  # Set sales_price_without_tax to null as it's not posted

        elif self.sales_price_without_tax is not None:
            # If sales_price_without_tax is provided, calculate sales_price_with_tax and store final total
            gst_amount = (self.sales_price_without_tax * gst_rate) / Decimal(100)
            self.sales_price_with_tax = self.sales_price_without_tax + gst_amount
            self.final_total = self.sales_price_with_tax  # Set final_total to sales_price_with_tax
            self.sales_price_with_tax = None  # Set sales_price_with_tax to null as it's not posted

        else:
            self.final_total = None  # If no values are provided, set final_total as null

        # Validate SAC code and auto-fill description
        self.clean()

        super().save(*args, **kwargs)

    def clean(self):
        """ Validate that SAC code exists in SACCode model and set description """
        if not SACCode.objects.filter(sac_code=self.sac_code).exists():
            raise ValidationError(f"SAC Code {self.sac_code} does not exist. Please enter a valid SAC code.")
        
        # If SAC code is valid, fetch and set the description
        sac_code_instance = SACCode.objects.get(sac_code=self.sac_code)
        self.description = sac_code_instance.description

    def __str__(self):
        return self.service_name 
"""Run with python -m unittest discover -s tests -v."""
import unittest
from test_monochrome import test_skill_has_monochrome_gate
from test_image_crops import test_normal_contain, test_missing_crop_data_rejected, test_unapproved_crop_rejected, test_crop_requires_roi_approval
class PublicPackageTests(unittest.TestCase):
    def test_monochrome_rules(self): test_skill_has_monochrome_gate()
    def test_contain(self): test_normal_contain()
    def test_missing_crop_data(self): test_missing_crop_data_rejected()
    def test_unapproved_crop(self): test_unapproved_crop_rejected()
    def test_approved_detail(self): test_crop_requires_roi_approval()

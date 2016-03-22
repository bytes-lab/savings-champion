from ckeditor.widgets import CKEditorWidget
from django import forms
from pages.models import ParentPage, ChildPage, FAQBlock, StaticPageBlock, RateAlert

class ParentPageAdForm(forms.ModelForm):
     class Meta:
        model = ParentPage
        widgets = {
                   'body' : CKEditorWidget()
                   }

class ChildPageAdForm(forms.ModelForm):
     class Meta:
        model = ChildPage
        widgets = {
                   'body' : CKEditorWidget()
                   }
        
class FAQAdForm(forms.ModelForm):
     class Meta:
        model = FAQBlock
        widgets = {
                   'answer' : CKEditorWidget()
                   }
        
class StaticPageBlockAdForm(forms.ModelForm):
     class Meta:
        model = StaticPageBlock
        widgets = {
                   'block' : CKEditorWidget()
                   }

class RateAlertAdForm(forms.ModelForm):
     class Meta:
        model = RateAlert
        widgets = {
                   'body' : CKEditorWidget()
                   }
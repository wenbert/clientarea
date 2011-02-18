from django import forms

class EditDescForm(forms.Form):
    dialog_filename = forms.CharField(widget=forms.HiddenInput)
    dialog_groupname = forms.CharField(widget=forms.HiddenInput)
    dialog_desc = forms.CharField(widget=forms.Textarea)
    
    
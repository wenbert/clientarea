from django import forms

class AddMessageForm(forms.Form):
    title = forms.CharField(max_length=250)
    groupid = forms.CharField(widget=forms.HiddenInput) 
    #categories = forms.ChoiceField(choices = CATEGORY_CHOICES, required=True) 
    category = forms.ChoiceField() 
    body = forms.CharField(widget=forms.Textarea)
    
class AddCommentForm(forms.Form):
    postid = forms.CharField(widget=forms.HiddenInput)
    category = forms.CharField(widget=forms.HiddenInput)
    title = forms.CharField(max_length=250)
    groupid = forms.CharField(widget=forms.HiddenInput) 
    body = forms.CharField(widget=forms.Textarea)
    
    
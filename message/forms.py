from django import forms

# Define your choices 
CATEGORY_CHOICES = ((1,'location1'), 
                    (2,'location2'), 
                    (3,'location3'), 
                    (4,'location4'), 
                   ) 
                   
GROUP_CHOICES = ((1,'Group 1'), 
                    (2,'Group 2'), 
                    (3,'Group 3'), 
                    (4,'Group 4'), 
                   ) 
                   
NOTIFY_GROUP_MEMBER_CHOICES = ((1,'Group Member 1'), 
                    (2,'Group Member 2'), 
                    (3,'Group Member 3'), 
                    (4,'Group Member 4'), 
                   ) 

class AddMessageForm(forms.Form):
    title = forms.CharField(max_length=250)
    groupid = forms.CharField(widget=forms.HiddenInput) 
    #categories = forms.ChoiceField(choices = CATEGORY_CHOICES, required=True) 
    category = forms.ChoiceField() 
    body = forms.CharField(widget=forms.Textarea)
    
    
    
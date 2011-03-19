from django import forms

class AddMessageForm(forms.Form):
    title = forms.CharField(max_length=250)
    groupid = forms.CharField(widget=forms.HiddenInput) 
    #categories = forms.ChoiceField(choices = CATEGORY_CHOICES, required=True) 
    category = forms.ChoiceField() 
    body = forms.CharField(widget=forms.Textarea)
    users = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,label="Notify and subscribe users to this post:")
    
class AddCommentForm(forms.Form):
    postid = forms.CharField(widget=forms.HiddenInput)
    category = forms.CharField(widget=forms.HiddenInput)
    title = forms.CharField(max_length=250)
    groupid = forms.CharField(widget=forms.HiddenInput) 
    body = forms.CharField(widget=forms.Textarea)
    users = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput,
                                    required=False)    
    
class CommentIdForm(forms.Form):
    commentid = forms.CharField(widget=forms.HiddenInput)
    commentid.widget.attrs['class'] = 'commentid'
    
class GroupMembersCheckboxForm(forms.Form):
    users = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                    label="Notify and subscribe users to this post:",
                                    required=False)    
                              
class GroupMembersHiddenForm(forms.Form):
    users = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput,
                                    label="Notify and subscribe users to this post:",
                                    required=False)  
                              
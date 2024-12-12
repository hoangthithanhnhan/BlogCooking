from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
# Create your models here.
 
#Form register
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','password1','password2']


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('T', 'Trai'),
        ('G', 'Gái'),
        ('B', 'Chưa Xác Định'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    profile_image = models.ImageField(upload_to='images/', null=True, blank=True)
    def __str__(self):
        return self.user.username
    
class Classify(models.Model): 
    name = models.CharField(max_length=100) 
    def __str__(self): return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=100,null=True)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    introduce =  models.CharField(max_length=100,null=True)
    description = models.CharField(max_length=200,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    liked_tym = models.ManyToManyField(User, related_name='liked_recipes', blank=True)
    classify = models.ManyToManyField(Classify, related_name='recipes', blank=True)
    reported = models.BooleanField(default=False)
    
    def __str__(self):
            return self.title
    def total_likes(self): 
        return self.liked_tym.count()


class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/') 
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ảnh Của Bài : {self.recipe.title}"



class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.recipe.title}"

    def is_reply(self):
        return self.parent is not None


class Follow(models.Model): 
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE) 
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return f'{self.follower.username} follows {self.followed.username}'

class Notification(models.Model): 
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications') 
    sender = models.ForeignKey(User, on_delete=models.CASCADE) 
    recipess = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255) 
    read = models.BooleanField(default=False) 
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self): 
        return f'Notification for {self.recipient.username}'
    
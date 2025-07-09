from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from datetime import datetime, date

#The first main video on deusmagnus website

# The main model for Deus Magnus Model category
class DeusMagnusMainPost(models.Model):
    deus_magnus_title = models.CharField(max_length=255, blank=True, null=True)
    deus_magnus_status = models.CharField(max_length=255, blank=True, null=True)
    deus_magnus_description = models.TextField()
    deus_magnus_slug = models.SlugField (max_length=255,blank=True, null=True)
    deus_manus_video = models.FileField(upload_to='videos/') 
    #thumbnail = models.ImageField(max_length=100, null=True, blank=True)
    deus_magnus_publish_date = models.DateTimeField (auto_now_add= True)
    deus_magnus_author = models.ForeignKey(User, on_delete=models.CASCADE)

       
    class Meta:
        ordering =['-deus_magnus_publish_date']
    
    def __str__(self):
        return self.deus_magnus_title + ' | ' + str(self.deus_magnus_author)
    
    def get_absolute_url(self):
        return reverse('home','sub_video_img_detail','sub_detail_video','sub_detail',
                       'board_detail','blog_detail','last_detail','second_detail','detail')
    
# The second model for Deus Magnus Model category
class SecondDeusMagnusMainPicturePost(models.Model):
    second_deus_magnus_title = models.CharField(max_length=255, blank=True, null=True)
    second_deus_magnus_status = models.CharField(max_length=255, blank=True, null=True)
    second_deus_magnus_description = models.TextField()
    second_deus_magnus_slug = models.SlugField (max_length=255,blank=True, null=True)
    second_deus_magnus_img = models.ImageField(upload_to='images/')
    second_deus_magnus_publish_date = models.DateTimeField (auto_now_add= True)
    second_deus_magnus_author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering =['second_deus_magnus_publish_date']
    
    def __str__(self):
        return self.second_deus_magnus_title + ' | ' + str(self.second_deus_magnus_author)
    
    def get_absolute_url(self):
        return reverse('home',)

    
#first sub picture category of the picture
class SubPicture_1(models.Model):
    sub_title_1 = models.CharField(max_length=200, blank=True, null=True)
    sub_description_1 = models.TextField()
    sub_slug_1 = models.SlugField (max_length=255,blank=True, null=True)
    sub_image_1 = models.ImageField(upload_to='images_sub/')
    #sub_image_2 = models.ImageField(upload_to='images_sub2/')
    #sub_image_3 = models.ImageField(upload_to='images_sub2/')
    sub_publish_date_1 = models.DateTimeField (auto_now_add= True)
    sub_author_1 = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering =['-sub_publish_date_1']
    def __str__(self):
        return self.sub_title_1 + ' | ' + str(self.sub_author_1)

    def get_absolute_url(self):
        return reverse('home')

class SubPicture_2 (models.Model):
    sub_title_2 = models.CharField(max_length=255, blank=True, null=True)
    sub_description_2 = models.TextField()
    sub_slug_2 = models.SlugField (max_length=255,blank=True, null=True)
    #sub_image_2 = models.ImageField(upload_to='images_sub/')
    sub_video_2 = models.FileField(upload_to='video_sub/')
    sub_publish_date_2 = models.DateTimeField (auto_now_add= True)
    sub_author_2 = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        ordering =['sub_publish_date_2']
    
    def __str__(self):
        return self.sub_title_2 + ' | ' + str(self.sub_author_2)

    def get_absolute_url(self):
        return reverse('home','sub_video_img_detail','sub_detail_video','sub_detail',
                       'board_detail','blog_detail','last_detail','second_detail','detail')
    
#first sub video category of the video
class VideoSubImage(models.Model):
    video_sub_title = models.CharField(max_length=200, blank=True, null=True)
    video_sub_description = models.TextField()
    video_sub_slug = models.SlugField (max_length=255,blank=True, null=True)
    video_sub_image = models.ImageField(upload_to='video_sub_images/')
    video_sub_publish_date = models.DateTimeField (auto_now_add= True)
    video_sub_author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering =['video_sub_publish_date']
    
    def __str__(self):
        return self.video_sub_title + ' | ' + str(self.video_sub_author)

    def get_absolute_url(self):
        return reverse('home','sub_video_img_detail','sub_detail_video',
                       'board_detail','blog_detail','sub_detail','last_detail','second_detail','detail')
    
#The blog category
class BlogDeusMagnus(models.Model):
    blog_deus_magnus_title = models.CharField(max_length=255, blank=True, null=True)
    blog_deus_magnus_description = models.TextField()
    blog_deus_magnus_slug = models.SlugField (max_length=255,blank=True, null=True)
    blog_deus_magnus_img = models.ImageField(upload_to='blog_images/')
    blog_deus_magnus_publish_date = models.DateTimeField (auto_now_add= True)
    blog_deus_magnus_author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering =['-blog_deus_magnus_publish_date']
    
    def __str__(self):
        return self.blog_deus_magnus_title + ' | ' + str(self.blog_deus_magnus_author)
    
    def get_absolute_url(self):
        return reverse('home','sub_video_img_detail','sub_detail_video','sub_detail',
                       'last_detail','second_detail','detail','board_detail','blog_detail',)

#The deus_magnus_event view model page
class DeusMagnusEventBlog(models.Model):
    deus_magnus_event_title = models.CharField(max_length=255, blank=True, null=True)
    deus_magnus_event_description = models.TextField()
    deus_magnus_event_sub_title_1 = models.CharField(max_length=200, blank=True, null=True)
    deus_magnus_event_description_1 = models.TextField()
    deus_magnus_event_sub_title_2 = models.CharField(max_length=200, blank=True, null=True)
    deus_magnus_event_description_2 = models.TextField()
    deus_magnus_event_sub_title_3 = models.CharField(max_length=200, blank=True, null=True)
    deus_magnus_event_description_3 = models.TextField()
    deus_magnus_event_sub_title_4 = models.CharField(max_length=200, blank=True, null=True)
    deus_magnus_event_description_4 = models.TextField()
    deus_magnus_event_sub_title_5 = models.CharField(max_length=200, blank=True, null=True)
    deus_magnus_event_description_5 = models.TextField()
    deus_magnus_event_slug = models.SlugField (max_length=255,blank=True, null=True)
    deus_magnus_event_img = models.ImageField(upload_to='even_images/')
    deus_magnus_event_author = models.ForeignKey(User, on_delete=models.CASCADE)
    deus_magnus_event_publish_date = models.DateTimeField (auto_now_add= True)

    class Meta:
        ordering =['-deus_magnus_event_publish_date']
    
    def __str__(self):
        return self.deus_magnus_event_title + ' | ' + str(self.deus_magnus_event_author)
    
    def get_absolute_url(self):
        return reverse('home','sub_video_img_detail','sub_detail_video','sub_detail','last_detail',
                       'second_detail','detail','board_detail','blog_detail',)

from django.db import models

class Guides(models.Model):
    guides_title = models.CharField(max_length=255, blank=True, null=True)
    guides_description = models.TextField()
    guides_sub_title_1 = models.CharField(max_length=200, blank=True, null=True)
    guides_description_1 = models.TextField()
    guides_sub_title_2 = models.CharField(max_length=200, blank=True, null=True)
    guides_description_2 = models.TextField()
    guides_sub_title_3 = models.CharField(max_length=200, blank=True, null=True)
    guides_description_3 = models.TextField()
    guides_sub_title_4 = models.CharField(max_length=200, blank=True, null=True)
    guides_description_4 = models.TextField()
    guides_sub_title_5 = models.CharField(max_length=200, blank=True, null=True)
    guides_description_5 = models.TextField()
    guides_img = models.ImageField(upload_to='guides_images/')
    guides_author = models.ForeignKey(User, on_delete=models.CASCADE)
    '''guides_publish_date = models.DateTimeField (auto_now_add= True)
    class Meta:
        ordering = ['-guides_publish_date']'''

    def __str__(self):
        return self.guides_title
    
    def get_absolute_url(self):
        return reverse('home')

#Our Team management of deus magnus view
class OurManagementsInDeusMagnus(models.Model):
    our_team_name = models.CharField(max_length=255, blank=True, null=True)
    our_team_position = models.CharField(max_length=255, blank=True, null=True)
    our_team_description = models.TextField()
    our_team_slug = models.SlugField (max_length=255,blank=True, null=True)
    our_team_img = models.ImageField(upload_to='our_team_images/')
    our_team_author = models.ForeignKey(User, on_delete=models.CASCADE)
    our_team_publish_date = models.DateTimeField (auto_now_add= True)

    class Meta:
        ordering =['-our_team_publish_date']
    
    def __str__(self):
        return self.our_team_name + ' | ' + str(self.our_team_author)
    
    def get_absolute_url(self):
        return reverse('home','sub_video_img_detail','sub_detail_video','sub_detail','last_detail',
                       'second_detail','detail','board_detail','blog_detail',)

# Resources FAQs of deus magnus view
class FAQs(models.Model):
    FAQs_title = models.CharField(max_length=255, blank=True, null=True)
    FAQs_response = models.TextField()
    FAQs_slug = models.SlugField (max_length=255,blank=True, null=True)
    FAQs_author = models.ForeignKey(User, on_delete=models.CASCADE)
    FAQs_publish_date = models.DateTimeField (auto_now_add= True)

    class Meta:
        ordering =['-FAQs_publish_date']
    
    def __str__(self):
        return self.FAQs_title + ' | ' + str(self.FAQs_author)
    
    def get_absolute_url(self):
        return reverse('home')

# Resources GLOSSARY of deus magnus view
class GLOSSARY(models.Model):
    GLOSSARY_title = models.CharField(max_length=255, blank=True, null=True)
    GLOSSARY_response = models.TextField()
    GLOSSARY_slug = models.SlugField (max_length=255,blank=True, null=True)
    GLOSSARY_author = models.ForeignKey(User, on_delete=models.CASCADE)
    GLOSSARY_publish_date = models.DateTimeField (auto_now_add= True)

    class Meta:
        ordering =['-GLOSSARY_publish_date']
    
    def __str__(self):
        return self.GLOSSARY_title + ' | ' + str(self.GLOSSARY_author)
    
    def get_absolute_url(self):
        return reverse('home')

class Mainvideo(models.Model):
    deus_magnus_first_video = models.FileField(upload_to='main_videos/') 
#The Contactvideo on deusmagnus website
class Contactvideo(models.Model):
    deus_magnus_contact_video = models.FileField(upload_to='contact_videos/') 
#The Aboutvideo on deusmagnus website
class Aboutvideo(models.Model):
    deus_magnus_about_video = models.FileField(upload_to='about_videos/') 

class FounderPicture(models.Model):
    deus_magnus_founder_p = models.ImageField(upload_to='founder_p/') 

class BashPicture(models.Model):
    deus_magnus_bash_p = models.ImageField(upload_to='bash_p/') 

class ServicesPagePicture(models.Model):
    deus_magnus_services_p = models.ImageField(upload_to='services_p/') 

class RealEstatePicture(models.Model):
    deus_magnus_real_estate_p = models.ImageField(upload_to='real_estate_p/') 

class FacilityManagementPicture(models.Model):
    deus_magnus_facility_p = models.ImageField(upload_to='facility_p/')

class ConstructionPicture(models.Model):
    deus_magnus_construction_p = models.ImageField(upload_to='construction_p/')
    
class ProjectPicture(models.Model):
    deus_magnus_project_p = models.ImageField(upload_to='project_p/')
    
class EquipmentHire(models.Model):
    deus_magnus_equipment_p= models.ImageField(upload_to='equipment_p/')
    
class BoomPump(models.Model):
    deus_magnus_boom_p = models.ImageField(upload_to='boom_p/')
    
class ConcreteSupply(models.Model):
    deus_magnus_concrete_p = models.ImageField(upload_to='concrete_p/')
    
class MaterialSupply(models.Model):
    deus_magnus_material_p = models.ImageField(upload_to='material_p/')
    
class SpecializedServices(models.Model):
    deus_magnus_specialized_p = models.ImageField(upload_to='specialized_p/')



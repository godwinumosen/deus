
from django.urls import path
from . import views
from .views import HomeView, ArticleDetailView, SecondConstructionDetailViewArticleDetailView,VideoImageDetailView
from .views import SubPictureDetailView,SubVideoDetailView
from .views import BlogArticleDetail,EventBlog,OurTeam,ManagementTeamArticleOfDuesMagnusDetail,ContactView,AboutView
from .views import DeusMagnusEventBlogArticleDetailView,BlogView,FAQs_item,GLOSSARY_item,GuidesView,GuidesDetailView
from .views import FounderMessageView,ServicesPage,RealEstateServices,FacilityManagement,ConstructionDevelopment,Project
from .views import Equipment,Boom,Concrete,Material,Specialized,ProjectVideo

urlpatterns = [
    path('index/', views.index, name='index'),
    path('', HomeView.as_view(), name="home"),
    path('home/', HomeView.as_view(), name='home'),
    path('article/<int:pk>/', ArticleDetailView.as_view(), name="detail"),
    path('article2/<int:pk>/', SecondConstructionDetailViewArticleDetailView.as_view(), name="second_detail"),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('message/', views.message, name='message'),
    path('sub_picture/<int:pk>/', SubPictureDetailView.as_view(), name="sub_detail"),
    path('sub_video/<int:pk>/', SubVideoDetailView.as_view(), name="sub_detail_video"),
    path('sub_video_img/<int:pk>/', VideoImageDetailView.as_view(), name="sub_video_img_detail"),
    path('blog/', BlogView.as_view(), name='blog'),
    path('blog_article/<int:pk>/', BlogArticleDetail.as_view(), name="blog_detail"),
    
    path('projectvideo/', ProjectVideo.as_view(), name='projectvideo'),
    
    path('deus_magnus_event/', EventBlog.as_view(), name='deus_magnus_event'),
    path('projects', Project.as_view(), name="projects"),
    path('events_article_detail/<int:pk>/', DeusMagnusEventBlogArticleDetailView.as_view(), name='events_article_detail'),
    path('guides_1/', GuidesView.as_view(), name='guides_1'),
    path('guides_article/<int:pk>/', GuidesDetailView.as_view(), name='guides_article'),
    path('our_management_team/', OurTeam.as_view(), name='our_management_team'),
    path('our_management_team_article/<int:pk>/', ManagementTeamArticleOfDuesMagnusDetail.as_view(), name="our_management_team_article"),
    path('mission_vision_strategy/', views.MissionVisionStrategesView, name='mission_vision_strategy'),
    path('faqs_items/', FAQs_item.as_view(), name='faqs_items'),
    path('glossary_items/', GLOSSARY_item.as_view(), name='glossary_items'),
    path('founder_message/', FounderMessageView.as_view(), name='founder_message'),
    path('services/', ServicesPage.as_view(), name='services'),
    path('facility_management/', FacilityManagement.as_view(), name='facility_management'),
    path('real_estate_services/', RealEstateServices.as_view(), name='real_estate_services'),
    path('construction_development/', ConstructionDevelopment.as_view(), name='construction_development'),
    path('equipmenthire/', Equipment.as_view(), name='equipmenthire'),
    path('boom/', Boom.as_view(), name='boom'),
    path('concrete/', Concrete.as_view(), name='concrete'),
    path('material/', Material.as_view(), name='material'),
    path('specialized/', Specialized.as_view(), name='specialized'),

    
    
]   

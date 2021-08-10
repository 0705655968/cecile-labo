from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from .forms import FileUploadForm
import os
from PIL import Image
import imagehash


class DegitalcatalogView(View):
    def get(self, request, *args, **kwargs):
        self.template_name = "front/viewer.html"
        context = {
            'code': '15101',
        }
        return render(self.request, self.template_name)

class ViewerView(View):
    def get(self, request, *args, **kwargs):
        self.template_name = "front/viewer.html"
        return render(self.request, self.template_name)

class DesignView(View):
    def get(self, request, *args, **kwargs):
        self.template_name = "front/load.html"
        return render(self.request, self.template_name)

class CatalogView(View):
    def get(self, request, *args, **kwargs):
        self.template_name = "front/catalog.html"
        return render(self.request, self.template_name)

class SimilarView(View):
    def get(self, request, *args, **kwargs):
        template_name = "front/photo.html"
        form = FileUploadForm
        return render(request, template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        # ファイルが転送されるケース
        template_name = "front/similar.html"
        form = FileUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            template_name = "front/photo.html"
            return render(request, template_name, {"form": form})
        filename_save = form.save()

        # 画像処理
        media_dir = '/opt/app/cecile/data'
        target = media_dir+filename_save.replace('/static','')
        target_hash = imagehash.average_hash(Image.open(target))
        
        userpath = '/opt/app/cecile/data/hash/'
        image_files = []
        f = [os.path.join(userpath, path) for path in os.listdir(userpath)]
        for i in f:
            image_files.append(i)
        
        idx = {'haming':1000, 'path':''}
        for img in image_files:
            hash = imagehash.average_hash(Image.open(img))
            haming = target_hash - hash
            if idx['haming'] > haming:
                idx['path'] = img
                idx['haming'] = haming
        
        pagepath = idx['path'].replace('/opt/app/cecile/data/hash/','').replace('.jpg','')
        template_name = "front/sample/"+pagepath+".html"

        context = {
            'form': form,
            'filename_save': filename_save,
        }
        return render(request, template_name, context)

class ImageView(View):
    def post(self, request, *args, **kwargs):
        # ファイルが転送されるケース
        template_name = "front/image.html"
        form = FileUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, template_name, {"form": form})
        filename_save = form.save()
        context = {
            'form': form,
            'filename_save': filename_save,
        }
        return render(request, template_name, context)

class NewsView(View):
    def get(self, request, *args, **kwargs):
        self.template_name = "front/news.html"
        return render(self.request, self.template_name)

class SettingsView(View):
    def get(self, request, *args, **kwargs):
        self.template_name = "front/settings.html"
        return render(self.request, self.template_name)

class HomeView(View):
    def get(self, request, *args, **kwargs):
        self.template_name = "front/home.html"
        return render(self.request, self.template_name)

degitalcatalog = DegitalcatalogView.as_view()
viewer = ViewerView.as_view()
design = DesignView.as_view()
catalog = CatalogView.as_view()
similar = SimilarView.as_view()
news = NewsView.as_view()
settings = SettingsView.as_view()
home = HomeView.as_view()
image = ImageView.as_view()

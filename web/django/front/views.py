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
        # カタログの表紙判定
        media_dir = '/opt/app/cecile/data'
        target = media_dir+filename_save.replace('/static','')
        target_hash = imagehash.phash(Image.open(target))
        
        userpath = '/opt/app/cecile/data/imgsearch/hash/catalog/'
        image_files = []
        f = [os.path.join(userpath, path) for path in os.listdir(userpath)]
        for i in f:
            image_files.append(i)
        
        idx = {'haming':1000, 'path':''}
        for img in image_files:
            hash = imagehash.phash(Image.open(img))
            haming = target_hash - hash
            if idx['haming'] > haming:
                idx['path'] = img
                idx['haming'] = haming
        
        template_name = "front/sample/catalog.html"
        catalog_data = '<div class="nodata">情報がみつかりませんでした</div>'
        if idx['haming'] < 20:
            code = idx['path'].replace('/opt/app/cecile/data/imgsearch/hash/catalog/','').replace('.jpg','')
            data = CatalogMaster.objects.get(catalog=code)
            genre = CatalogGenreLink.objects.get(catalog=code)

            catalog_data = '<div class="title"><i class="material-icons submit">manage_search</i>検索されたカタログ</div>'
            catalog_data += '<ol class="search_result">'
            catalog_data += '<li>'
            catalog_data += '<a href="https://cecile-dev.prm.bz/viewer/'+str(code)+'/">'
            catalog_data += '<img src="https://cecile-dev.prm.bz/static/images/s.gif" style="background-image:url('+str(data.image)+')">'
            catalog_data += '<div>'
            catalog_data += '<p class="title">'+str(data.name)+'</p>'
            catalog_data += '<p><span>'+str(genre.genre)+'</span></p>'
            catalog_data += '</div>'
            catalog_data += '</a>'
            catalog_data += '</ol>'

            #template_name = "front/sample/"+pagepath+".html"

        context = {
            'form': form,
            'catalog_data': catalog_data,
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

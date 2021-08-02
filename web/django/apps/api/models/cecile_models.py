from django.db import models
from django.core.validators import MinLengthValidator


class CatalogMaster(models.Model):
    """ カタログマスタ """
    id                     = models.AutoField(verbose_name='ID', primary_key=True)
    catalog                = models.CharField(verbose_name='カタログID', max_length=15, unique=True)
    name                   = models.CharField(verbose_name='カタログ名', max_length=200, blank=True, null=True)
    introduction           = models.TextField(verbose_name='紹介文', blank=True, null=True)
    image                  = models.CharField(verbose_name='表紙画像', max_length=150, blank=True, null=True)
    local                  = models.CharField(verbose_name='表紙画像(保存画像パス)', max_length=150, blank=True, null=True)
    url                    = models.CharField(verbose_name='URL', max_length=150, blank=True, null=True)
    created                = models.DateTimeField(verbose_name='データ作成日時', auto_now_add=True, db_index=True)
    updated                = models.DateTimeField(verbose_name='データ更新日時', auto_now=True)
    status                 = models.BooleanField(verbose_name='掲載可否フラグ', default=True, db_index=True)

    def __str__(self):
        return str(self.id)

    class Meta():
        db_table = 'catalog_master'

class CatalogGenre(models.Model):
    """ カタログジャンルマスタ """
    id                     = models.AutoField(verbose_name='ID', primary_key=True)
    name                   = models.CharField(verbose_name='ジャンル名', max_length=255, unique=True, db_index=True)
    created                = models.DateTimeField(verbose_name='データ作成日時', auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta():
        db_table = 'catalog_genre'

class CatalogGenreLink(models.Model):
    """ セシールカタログジャンルリンク """
    id                     = models.AutoField(verbose_name='ID', primary_key=True)
    genre                  = models.CharField(verbose_name='ジャンル名', max_length=255, db_index=True)
    catalog                = models.CharField(verbose_name='カタログID', max_length=15, db_index=True)
    created                = models.DateTimeField(verbose_name='データ作成日時', auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta():
        db_table = 'catalog_genre_link'
        constraints = [
            models.UniqueConstraint(fields=['genre', 'catalog'], name='unique_cgl'),
        ]

class CatalogPages(models.Model):
    """ カタログページデータ """
    id                     = models.AutoField(verbose_name='ID', primary_key=True)
    catalog                = models.CharField(verbose_name='カタログID', max_length=15, db_index=True)
    page                   = models.CharField(verbose_name='ページ番号', max_length=15)
    image1                 = models.CharField(verbose_name='デジタルカタログ用画像1', max_length=150, blank=True, null=True)
    image2                 = models.CharField(verbose_name='デジタルカタログ用画像2', max_length=150, blank=True, null=True)
    local1                 = models.CharField(verbose_name='デジタルカタログ用画像1の保存先', max_length=150, blank=True, null=True)
    local2                 = models.CharField(verbose_name='デジタルカタログ用画像2の保存先', max_length=150, blank=True, null=True)
    url                    = models.CharField(verbose_name='URL', max_length=150, blank=True, null=True)
    created                = models.DateTimeField(verbose_name='データ作成日時', auto_now_add=True)
    updated                = models.DateTimeField(verbose_name='データ更新日時', auto_now=True)
    status                 = models.BooleanField(verbose_name='掲載可否フラグ', default=True, db_index=True)

    def __str__(self):
        return str(self.id)

    class Meta():
        db_table = 'catalog_pages'
        constraints = [
            models.UniqueConstraint(fields=['catalog', 'page'], name='unique_cp'),
        ]
        indexes = [
            models.Index(fields=['catalog', 'page'])
        ]

class CatalogPageItems(models.Model):
    """ カタログページ商品リスト """
    id                     = models.AutoField(verbose_name='ID', primary_key=True)
    catalog                = models.CharField(verbose_name='カタログID', max_length=15, db_index=True)
    page                   = models.CharField(verbose_name='ページ番号', max_length=15)
    item                   = models.CharField(verbose_name='商品番号', max_length=50)
    code                   = models.CharField(verbose_name='カタログ番号', max_length=20)
    order                  = models.CharField(verbose_name='申込番号', max_length=20)
    name                   = models.CharField(verbose_name='商品名', max_length=200)
    url                    = models.CharField(verbose_name='商品ページURL', max_length=150, blank=True, null=True)
    coordinate             = models.BooleanField(verbose_name='コーディネート情報可否フラグ', default=True, db_index=True)
    created                = models.DateTimeField(verbose_name='データ作成日時', auto_now_add=True)
    updated                = models.DateTimeField(verbose_name='データ更新日時', auto_now=True)
    status                 = models.BooleanField(verbose_name='掲載可否フラグ', default=True, db_index=True)

    def __str__(self):
        return str(self.id)

    class Meta():
        db_table = 'catalog_page_items'
        constraints = [
            models.UniqueConstraint(fields=['catalog', 'page', 'item'], name='unique_cpi'),
        ]
        indexes = [
            models.Index(fields=['catalog', 'page'])
        ]

class ItemImages(models.Model):
    """ 商品画像リスト """
    id                     = models.AutoField(verbose_name='ID', primary_key=True)
    item                   = models.CharField(verbose_name='商品番号', max_length=15, db_index=True)
    image                  = models.CharField(verbose_name='画像URL', max_length=150)
    local                  = models.CharField(verbose_name='画像保存先', max_length=150)
    introduction           = models.CharField(verbose_name='紹介文', max_length=255, blank=True, null=True)
    created                = models.DateTimeField(verbose_name='データ作成日時', auto_now_add=True)
    updated                = models.DateTimeField(verbose_name='データ更新日時', auto_now=True)
    status                 = models.BooleanField(verbose_name='掲載可否フラグ', default=True, db_index=True)

    def __str__(self):
        return str(self.id)

    class Meta():
        db_table = 'item_images'
        constraints = [
            models.UniqueConstraint(fields=['item', 'image'], name='unique_ii'),
        ]
        indexes = [
            models.Index(fields=['item', 'image'])
        ]

class CoordinateStyle(models.Model):
    """ コーディネート特集マスタ """
    id                     = models.AutoField(verbose_name='ID', primary_key=True)
    style                  = models.CharField(verbose_name='コーディネートスタイル名', max_length=255, unique=True)
    created                = models.DateTimeField(verbose_name='データ作成日時', auto_now_add=True)
    updated                = models.DateTimeField(verbose_name='データ更新日時', auto_now=True)
    status                 = models.BooleanField(verbose_name='掲載可否フラグ', default=True, db_index=True)

    def __str__(self):
        return str(self.id)

    class Meta():
        db_table = 'coordinate_style'

class CoordinateMaster(models.Model):
    """ コーディネートマスタ """
    id                     = models.AutoField(verbose_name='ID', primary_key=True)
    coordinate             = models.CharField(verbose_name='コーディネートID', max_length=30, unique=True, db_index=True)
    name                   = models.CharField(verbose_name='コーディネート名', max_length=255)
    image                  = models.CharField(verbose_name='コーディネート画像', max_length=150)
    local                  = models.CharField(verbose_name='コーディネート画像保存先', max_length=150)
    url                    = models.CharField(verbose_name='コーディネートページURL', max_length=200, blank=True, null=True)
    style1                 = models.CharField(verbose_name='スタイル名1', max_length=255, blank=True, null=True, db_index=True)
    style2                 = models.CharField(verbose_name='スタイル名2', max_length=255, blank=True, null=True, db_index=True)
    style3                 = models.CharField(verbose_name='スタイル名3', max_length=255, blank=True, null=True, db_index=True)
    created                = models.DateTimeField(verbose_name='データ作成日時', auto_now_add=True)
    updated                = models.DateTimeField(verbose_name='データ更新日時', auto_now=True)
    status                 = models.BooleanField(verbose_name='掲載可否フラグ', default=True, db_index=True)

    def __str__(self):
        return str(self.id)

    class Meta():
        db_table = 'coordinate_master'

class CoordinateItemLink(models.Model):
    """ コーディネート商品リンクテーブル """
    id                     = models.AutoField(verbose_name='ID', primary_key=True)
    coordinate             = models.CharField(verbose_name='コーディネートID', max_length=30, db_index=True)
    item                   = models.CharField(verbose_name='商品番号', max_length=15, db_index=True)
    created                = models.DateTimeField(verbose_name='データ作成日時', auto_now_add=True)
    status                 = models.BooleanField(verbose_name='掲載可否フラグ', default=True, db_index=True)

    def __str__(self):
        return str(self.id)

    class Meta():
        db_table = 'coordinate_item_link'
        constraints = [
            models.UniqueConstraint(fields=['coordinate', 'item'], name='unique_cl'),
        ]
        indexes = [
            models.Index(fields=['coordinate', 'item'])
        ]

class CoordinatePhotoMaster(models.Model):
    """ 商品画像リスト """
    id                     = models.AutoField(verbose_name='ID', primary_key=True)
    item                   = models.CharField(verbose_name='商品番号', max_length=15, db_index=True)
    name                   = models.CharField(verbose_name='商品名', max_length=255)
    image                  = models.CharField(verbose_name='画像URL', max_length=150)
    local                  = models.CharField(verbose_name='画像保存先', max_length=150)
    created                = models.DateTimeField(verbose_name='データ作成日時', auto_now_add=True)
    updated                = models.DateTimeField(verbose_name='データ更新日時', auto_now=True)
    status                 = models.BooleanField(verbose_name='掲載可否フラグ', default=True, db_index=True)

    def __str__(self):
        return str(self.id)

    class Meta():
        db_table = 'coordinate_photo_master'
        constraints = [
            models.UniqueConstraint(fields=['item', 'image'], name='unique_cpm'),
        ]
        indexes = [
            models.Index(fields=['item', 'image'])
        ]

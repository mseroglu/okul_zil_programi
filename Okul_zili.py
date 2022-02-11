uyari_texti="""
Bu klasöre ekleyeceğiniz mp3 ve wav uzantılı dosyalar
program yeniden açıldığında listede gözükür.
Ekle butonu ile eklenince hemen listede gözükür.

'toren' ve 'ikaz' kelimeleri ile başlayan melodiler listede gözükmez.
'toren' ve 'ikaz' kelimeleri ile başlayan melodiler silinmemelidir.
yenisi aynı isimle kayıt edilmelidir.


Dosya isimleri aşağıdaki şekilde olmalı, (dosya standardı 128 kbps)

toren_istiklal_marsi.mp3
toren_saygi_durusu.mp3
toren_saygi_ve_istiklal.mp3

ikaz_kirmizi.mp3
ikaz_sari.mp3
ikaz_siyah.mp3

iconlari da değiştirebilirsiniz, ancak isimleri değişmemelidir. yanlışlıkla silerseniz isimleri aşağıdadır.
sol_menu_2.PNG
sol_menu_3.PNG
zil.png
ana_sayfa.png
melodi_sayfasi.png
ayarlar_sayfasi.png
takvim.png
info.png
loading.gif
"""
with open("./melodies/okuyunuz.txt", "w", encoding="utf-8") as dosya:
    dosya.write(uyari_texti)


import time, sys, datetime, locale, os, shutil
locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')

from okul_zili_UI import Ui_MainWindow

from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QStyle, QFileDialog, QDialog, QMessageBox, QVBoxLayout
from PyQt5 import QtMultimedia, QtMultimediaWidgets, QtWidgets, QtCore, QtGui, Qt
from PyQt5.QtMultimedia import *

from my_database import MyDatabase, conn, cursor
MyDatabase()

class LoadingScreen(QDialog):
    def __init__(self, sure=1000):
        super(LoadingScreen, self).__init__()
        self.setFixedSize(125,125)
        self.setWindowFlags( Qt.Qt.WindowStaysOnTopHint | Qt.Qt.CustomizeWindowHint )
        self.label_animation = QtWidgets.QLabel(self)
        self.movie = QtGui.QMovie("./icons/loading.gif")
        self.movie.setScaledSize(QtCore.QSize(100,100))         # gif resize

        lay = QVBoxLayout()
        lay.addWidget(self.label_animation)
        self.setLayout(lay)
        self.label_animation.setMovie(self.movie)
        timer = QtCore.QTimer(self)
        self.start_animation()
        timer.singleShot(sure, self.finis_animation)
        self.show()

    def start_animation(self):
        self.movie.start()

    def finis_animation(self):
        self.movie.stop()
        self.close()



class Zil_app(QMainWindow):
    def __init__(self):
        super(Zil_app, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.resize(800,600)

        self.loading = LoadingScreen(2000)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.anasayfayi_guncelle)
        self.timer.start(1000)


        # Değişkenler
        self.version            = "Okul Zili v1.2"
        self.bekle_5_dk         = 10
        self.melodi_path = "melodies/melodi_1.mp3"
        self.buton_object_name = "btn_zil_ogrenci"
        self.player_calma_politikasi = 0
        self.left_menu_buttons = [self.ui.btn_page1, self.ui.btn_page2, self.ui.btn_page3, self.ui.btn_page4, self.ui.btn_page5]
        self.left_menu_labels  = [self.ui.label_btn1, self.ui.label_btn2, self.ui.label_btn3, self.ui.label_btn4, self.ui.label_btn5]
        self.gunler_checkBox   = [self.ui.checkBox_pazartesi, self.ui.checkBox_sali, self.ui.checkBox_carsamba, self.ui.checkBox_persembe, self.ui.checkBox_cuma, self.ui.checkBox_cumartesi, self.ui.checkBox_pazar]
        self.db_tables         = ("Pazartesi", "Sali", "Carsamba", "Persembe", "Cuma", "Cumartesi", "Pazar")
        self.ders_saat_items_dict = {0: {"giris": self.ui.timeEdit_sabah_toplanma, "cikis": self.ui.timeEdit_sabah_toplanma},
                                1: {"giris": self.ui.timeEdit_gun1_baslama1, "cikis": self.ui.timeEdit_gun1_bitis1},
                                2: {"giris": self.ui.timeEdit_gun1_baslama2, "cikis": self.ui.timeEdit_gun1_bitis2},
                                3: {"giris": self.ui.timeEdit_gun1_baslama3, "cikis": self.ui.timeEdit_gun1_bitis3},
                                4: {"giris": self.ui.timeEdit_gun1_baslama4, "cikis": self.ui.timeEdit_gun1_bitis4},
                                5: {"giris": self.ui.timeEdit_gun1_baslama5, "cikis": self.ui.timeEdit_gun1_bitis5},
                                6: {"giris": self.ui.timeEdit_gun1_baslama6, "cikis": self.ui.timeEdit_gun1_bitis6},
                                7: {"giris": self.ui.timeEdit_gun1_baslama7, "cikis": self.ui.timeEdit_gun1_bitis7},
                                8: {"giris": self.ui.timeEdit_gun1_baslama8, "cikis": self.ui.timeEdit_gun1_bitis8},
                                9: {"giris": self.ui.timeEdit_gun1_baslama9, "cikis": self.ui.timeEdit_gun1_bitis9},
                                10: {"giris": self.ui.timeEdit_gun1_baslama10, "cikis": self.ui.timeEdit_gun1_bitis10},
                                11: {"giris": self.ui.timeEdit_gun1_baslama11, "cikis": self.ui.timeEdit_gun1_bitis11},
                                12: {"giris": self.ui.timeEdit_gun1_baslama12, "cikis": self.ui.timeEdit_gun1_bitis12},
                                13: {"giris": self.ui.timeEdit_gun1_baslama13, "cikis": self.ui.timeEdit_gun1_bitis13},
                                14: {"giris": self.ui.timeEdit_gun1_baslama14, "cikis": self.ui.timeEdit_gun1_bitis14}}

        # Fonksiyonlar
        self.stackedWidget_sayfa_degistir()
        self.textbuttons_hide()
        self.zaman_tablosunu_vt_den_cek_doldur()
        self.melodileri_comboda_goster()
        self.melodi_ayarlari_programa_uygula()
        self.zaman_ayarlari_programa_uygula()
        self.baslangic_olarak_tum_gunlerin_zaman_tablolarini_olustur()
        self.mediaPlayer_olustur_ve_melodi_ata( path= self.calinacak_melodi_secimi(self.buton_object_name) )


        # signal slot
        self.ui.btn_sol_menu_gorunum.clicked[bool].connect(self.textbuttons_hide)
        self.ui.btn_sol_menu_gorunum.clicked[bool].connect(self.melodi_ayarlari_kaydet)
        self.ui.btn_page1.clicked[bool].connect(self.left_menu_clicked)
        self.ui.btn_page2.clicked[bool].connect(self.left_menu_clicked)
        self.ui.btn_page3.clicked[bool].connect(self.left_menu_clicked)
        self.ui.btn_page4.clicked[bool].connect(self.left_menu_clicked)
        self.ui.btn_page5.clicked[bool].connect(self.left_menu_clicked)

        self.ui.btn_zil_ogrenci.clicked.connect(self.play_butonu_tikla)
        self.ui.btn_zil_ogretmen.clicked.connect(self.play_butonu_tikla)
        self.ui.btn_zil_teneffus.clicked.connect(self.play_butonu_tikla)
        self.ui.btn_istiklal_marsi.clicked.connect(self.play_butonu_tikla)
        self.ui.btn_saygi_durusu.clicked.connect(self.play_butonu_tikla)
        self.ui.btn_saygi_ve_istiklal.clicked.connect(self.play_butonu_tikla)
        self.ui.btn_sari_ikaz.clicked.connect(self.play_butonu_tikla)
        self.ui.btn_kirmizi_ikaz.clicked.connect(self.play_butonu_tikla)
        self.ui.btn_siyah_ikaz.clicked.connect(self.play_butonu_tikla)
        self.ui.btn_play.clicked[bool].connect(self.melodi_oynat_durdur)
        self.ui.btn_mute.clicked[bool].connect(self.media_ses_mute)
        self.ui.dial_ses_seviyesi.valueChanged.connect(self.ses_seviyesi_ayarla)

        self.ui.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.ui.btn_mute.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))

        self.ui.btn_kaydet.clicked.connect(self.zaman_tablosu_kaydet)
        self.ui.btn_ayardan_saatleri_ata.clicked.connect(self.ayarlardan_saat_degerleri_ata)
        self.ui.btn_saatleri_sifirla.clicked.connect(self.zaman_tablosunu_temizle)

        self.ui.btn_gunun_programini_yukle.clicked.connect(self.zaman_tablosunu_vt_den_cek_doldur)
        self.ui.listWidget_gunler.itemClicked.connect(self.zaman_tablosunu_vt_den_cek_doldur)

        self.ui.spinBox_kac_dakika_once.valueChanged.connect(self.melodi_ayarlari_kaydet)
        self.ui.spinBox_zil_calma_suresi.valueChanged.connect(self.melodi_ayarlari_kaydet)
        self.ui.dial_ses_seviyesi.valueChanged.connect(self.melodi_ayarlari_kaydet)
        self.ui.comboBox_melodi_ogrenci.currentIndexChanged.connect(self.melodi_ayarlari_kaydet)
        self.ui.comboBox_melodi_ogretmen.currentIndexChanged.connect(self.melodi_ayarlari_kaydet)
        self.ui.comboBox_melodi_teneffus.currentIndexChanged.connect(self.melodi_ayarlari_kaydet)

        self.ui.comboBox_zamanlayici_gorevi.currentIndexChanged.connect(self.zamanlayici_gorevi_belirle)
        self.ui.spinBox_zamanlayici.valueChanged.connect(self.zamanlayici_gorev_secimini_aktif_et)

        self.ui.btn_ayardan_saatleri_ata.clicked.connect(self.Loading)

        self.ui.btn_ayardan_saatleri_ata.clicked.connect(self.zaman_ayarlari_kaydet)
        self.ui.btn_verileri_kaydet.clicked.connect(self.zaman_ayarlari_kaydet)
        self.ui.btn_verileri_kaydet.clicked.connect(self.Loading)

        self.ui.radioButton_normal_ogretim.clicked.connect(self.zaman_ayarlari_programa_uygula)
        self.ui.radioButton_ikili_ogretim.clicked.connect(self.zaman_ayarlari_programa_uygula)
        self.ui.btn_melodi_ekle.clicked.connect(self.melodi_ekle)

    def Loading(self):
        self.loading = LoadingScreen(500)

    def zamanlayici_gorev_secimini_aktif_et(self, value):
        self.ui.comboBox_zamanlayici_gorevi.setEnabled( bool(value) )
        if not value: self.ui.comboBox_zamanlayici_gorevi.setCurrentIndex(0)

    def zamanlayici_gorevi_belirle(self, state):
        try:
            self.timer1 = QtCore.QTimer()
            self.timer1.timeout.connect(self.zamanlayici_bitince_ses_ac)
            self.timer1.start(self.ui.spinBox_zamanlayici.value()* 60_000)      # 60_000 = 1 dk
            self.player_calma_politikasi = state
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk: zamanlayici_gorevi_belirle           Hata Kodu: {E}",10000)

    def zamanlayici_bitince_ses_ac(self):
        try:
            self.timer1.stop()
            self.ui.comboBox_zamanlayici_gorevi.setCurrentIndex(0)
            self.ui.spinBox_zamanlayici.setValue(0)
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk: zamanlayici_bitince_ses_ac        Hata Kodu:{E}   ",10000)

    def melodi_ekle(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Melodi Kopyala", "./", "mp3/wav dosyası (*.mp3 *.wav)")
            if file_name != "":
                shutil.copyfile(file_name, "./melodies/"+file_name.split("/")[-1])
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk: melodi_ekle           Hata Kodu: {E}")
        self.melodileri_comboda_goster()

    def melodi_ayarlari_topla(self):
        melodi_ogrenci  = self.ui.comboBox_melodi_ogrenci.currentIndex()
        melodi_ogretmen = self.ui.comboBox_melodi_ogretmen.currentIndex()
        melodi_teneffus = self.ui.comboBox_melodi_teneffus.currentIndex()
        ses_seviyesi    = self.ui.dial_ses_seviyesi.value()
        calma_suresi    = self.ui.spinBox_zil_calma_suresi.value()
        ogretim_tipi    = self.ui.radioButton_normal_ogretim.isChecked()
        menu_etkiket    = self.ui.btn_sol_menu_gorunum.isChecked()
        return [melodi_ogrenci, melodi_ogretmen, melodi_teneffus, ses_seviyesi, calma_suresi, ogretim_tipi, menu_etkiket]

    def zaman_ayarlari_topla(self):
        try:
            okul_adi = self.ui.lineEdit_okul_adi.text()
            sabah_ders  = self.ui.spinBox_sabah_ders_sayisi.value()
            ogle_ders   = self.ui.spinBox_ogle_ders_sayisi.value()
            ders_suresi = self.ui.spinBox_ders_suresi.value()
            tenef_suresi = self.ui.spinBox_tenefus_suresi.value()
            ogle_ara    = self.ui.spinBox_ogle_arasi_suresi.value()
            sabah_toplanma = self.ui.timeEdit_sabah_toplanma.time().toString("hh:mm:ss")
            ogrenci_zili = self.ui.spinBox_kac_dakika_once.value()
            toplanma_suresi = self.ui.spinBox_kac_dakika_sonra.value()
            if self.ui.radioButton_normal_ogretim.isChecked(): Id = 1
            else: Id = 2
            return [okul_adi, sabah_ders, ogle_ders, ders_suresi, tenef_suresi, ogle_ara, sabah_toplanma, ogrenci_zili, toplanma_suresi, Id]
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk: zaman_ayarlari_topla      Hata Kodu : {E}")

    def melodi_ayarlari_kaydet(self):
        try:
            cursor.execute(f"SELECT COUNT(*) FROM Melodi_ayarlari")
            kayit = cursor.fetchone()
            if not kayit[0]:
                sonuc = MyDatabase.melodi_ilk_ayarlar( self.melodi_ayarlari_topla() )
            else:
                sonuc = MyDatabase.melodi_ayarlari_guncelle( self.melodi_ayarlari_topla() )
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk : melodi_ayarlari_kaydet          Hata Kodu: {E}", 10000)

    def zaman_ayarlari_kaydet(self):
        try:
            cursor.execute(f"SELECT COUNT(*) FROM Zaman_ayarlari")
            kayit = cursor.fetchone()
            if not kayit[0]:
                sonuc = MyDatabase.zaman_ilk_ayarlar( self.zaman_ayarlari_topla() )
            else:
                sonuc = MyDatabase.zaman_ayarlari_guncelle( self.zaman_ayarlari_topla() )
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk : zaman_ayarlari_kaydet          Hata Kodu: {E}", 10000)

    def melodi_ayarlari_programa_uygula(self):
        try:
            ayar = MyDatabase.melodi_ayarlari_al()
            self.ui.comboBox_melodi_ogrenci.setCurrentIndex( ayar[0][0] )
            self.ui.comboBox_melodi_ogretmen.setCurrentIndex( ayar[0][1] )
            self.ui.comboBox_melodi_teneffus.setCurrentIndex( ayar[0][2] )
            self.ui.dial_ses_seviyesi.setValue( ayar[0][3] )
            self.ui.spinBox_zil_calma_suresi.setValue( ayar[0][4] )
            durum = ayar[0][5]
            self.ui.radioButton_normal_ogretim.click() if durum else self.ui.radioButton_ikili_ogretim.click()
            self.textbuttons_hide( state=bool(ayar[0][6]) )
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk : melodi_ayarlari_programa_uygula          Hata Kodu: {E}", 10000)

    def zaman_ayarlari_programa_uygula(self):
        try:
            if self.ui.radioButton_normal_ogretim.isChecked(): Id = 1
            else: Id = 2
            ayar = MyDatabase.zaman_ayarlari_al( Id=Id )
            self.ui.lineEdit_okul_adi.setText( ayar[0][1] )
            self.ui.spinBox_sabah_ders_sayisi.setValue( ayar[0][2] )
            self.ui.spinBox_ogle_ders_sayisi.setValue( ayar[0][3] )
            self.ui.spinBox_ders_suresi.setValue( ayar[0][4] )
            self.ui.spinBox_tenefus_suresi.setValue( ayar[0][5] )
            self.ui.spinBox_ogle_arasi_suresi.setValue( ayar[0][6] )
            h,m,s = ayar[0][7].split(":")
            self.ui.timeEdit_sabah_toplanma.setTime( QtCore.QTime( int(h), int(m), int(s) ) )
            self.ui.spinBox_kac_dakika_once.setValue( ayar[0][8] )
            self.ui.spinBox_kac_dakika_sonra.setValue( ayar[0][9] )
            okul_adi = "  -  "+ayar[0][1]
            self.setWindowTitle(self.version + okul_adi)
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk : zaman_ayarlari_programa_uygula          Hata Kodu: {E}", 10000)

    def baslangic_olarak_tum_gunlerin_zaman_tablolarini_olustur(self):
        try:
            for table in self.db_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                kayit=cursor.fetchone()
                if not kayit[0]:
                    sonuc = MyDatabase.veri_giris(table, self.zil_saatleri_topla_ver(veri_adedi=2))
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk : baslangic_olarak_tum_gunlerin_zaman_tablolarini_olustur   Hata Kodu: {E}", 10000)

    def zaman_tablosu_kaydet(self):
        try:
            kayit_var_mi = False
            for day in self.gunler_checkBox:
                if day.isChecked():
                    kayit_var_mi = True
            if not kayit_var_mi:
                QMessageBox.about(self, "Kayıt hatası", "Kayıt yapılacak en az bir gün seçmelisiniz")
            else:
                self.Loading = LoadingScreen()
                for i, gun in enumerate(self.gunler_checkBox):
                    if gun.isChecked():
                        db_tablo_adi = self.db_tables[i]
                        cursor.execute(f"SELECT COUNT(*) FROM {db_tablo_adi}")
                        kayit=cursor.fetchone()
                        if not kayit[0]:
                            sonuc = MyDatabase.veri_giris(db_tablo_adi, self.zil_saatleri_topla_ver(veri_adedi=2))
                        else:
                            sonuc = MyDatabase.veri_guncelle(db_tablo_adi, self.zil_saatleri_topla_ver(veri_adedi=3))
                        if sonuc:
                            self.ui.statusbar.showMessage("Yeni saatler kaydedildi", 10000)
                            self.ui.groupBox_zaman_tablosu.setTitle("Tablo kayıt edildi")
                        else:
                            self.ui.statusbar.showMessage("Kayıt başarısız..", 10000)
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk : zaman_tablosu_kaydet          Hata Kodu: {E}", 10000)

    def zil_saatleri_topla_ver(self, veri_adedi=3) -> list :
        timeline = []
        for i in self.ders_saat_items_dict.keys():
            giris = self.ders_saat_items_dict[i]["giris"].time().toString("hh:mm:ss")
            cikis = self.ders_saat_items_dict[i]["cikis"].time().toString("hh:mm:ss")
            veri = (giris, cikis, i+1)
            timeline.append(veri[:veri_adedi])
        return timeline

    def zaman_tablosunu_temizle(self):
        for key, value in self.ders_saat_items_dict.items():
            if key != 0 :
                value["giris"].setTime(QtCore.QTime(0,0,0))
                value["cikis"].setTime(QtCore.QTime(0,0,0))

    def zaman_tablosunu_vt_den_cek_doldur(self):
        try:
            bugun = datetime.datetime.today().strftime("%A")
            self.ui.groupBox_zaman_tablosu.setTitle("Bugün " + bugun)
            sender = self.sender()
            if sender != None:
                if sender.objectName() == "listWidget_gunler":
                    self.bekle_5_dk = 5
                    bugun = self.ui.listWidget_gunler.currentItem().text()
                    self.ui.groupBox_zaman_tablosu.setTitle("Seçilen Gün # " + bugun + " #")

            getirilicek_gun = bugun.replace("ı", "i").replace("ş", "s").replace("Ç", "C")
            self.aktif_zil_saatleri = MyDatabase.saat_verileri_al(getirilicek_gun)
            for key, value in self.ders_saat_items_dict.items():
                if key != 0 :
                    for i, veri in enumerate(self.aktif_zil_saatleri):
                        if key==i:
                            h, m, s = veri[1].split(":")
                            value["giris"].setTime(QtCore.QTime(int(h),int(m),int(s)))
                            h, m, s = veri[2].split(":")
                            value["cikis"].setTime(QtCore.QTime(int(h),int(m),int(s)))
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk : zaman_tablosunu_vt_den_cek_doldur             Hata Kodu : {E}", 5000)

    def ayarlardan_saat_degerleri_ata(self):
        try:
            self.ui.groupBox_zaman_tablosu.setTitle("Kayıt Edilmemiş Tablo")
            self.zaman_tablosunu_temizle()
            ders_saat_suresi = 60*self.ui.spinBox_ders_suresi.value()                           # 40
            teneffus_suresi  = 60*self.ui.spinBox_tenefus_suresi.value()                        # 45
            ogle_arasi       = 60*self.ui.spinBox_ogle_arasi_suresi.value()-teneffus_suresi     # 30
            sabah_ders_sayisi=    self.ui.spinBox_sabah_ders_sayisi.value()                     # 4
            ogle_ders_sayisi =    self.ui.spinBox_ogle_ders_sayisi.value()                      # 3
            toplanma_suresi  = 60*self.ui.spinBox_kac_dakika_sonra.value()                      # 10
            for key, value in self.ders_saat_items_dict.items():
                if key!=0 and key <= sabah_ders_sayisi+ogle_ders_sayisi:
                    if key <= sabah_ders_sayisi: ogle_arasi_suresi = 0
                    else: ogle_arasi_suresi = ogle_arasi

                    sure1 = (key-1)*ders_saat_suresi    +    (key-1)*teneffus_suresi    +     toplanma_suresi   + ogle_arasi_suresi
                    value["giris"].setTime(self.ui.timeEdit_sabah_toplanma.time().addSecs( sure1 ))

                    sure2 =  key*ders_saat_suresi     +      (key-1)*teneffus_suresi     +    toplanma_suresi   + ogle_arasi_suresi
                    value["cikis"].setTime(self.ui.timeEdit_sabah_toplanma.time().addSecs( sure2 ))
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk : ayarlardan_saat_degerleri_ata             Hata Kodu : {E}")

    def melodileri_comboda_goster(self):
        self.ui.comboBox_melodi_ogrenci.clear()
        self.ui.comboBox_melodi_ogretmen.clear()
        self.ui.comboBox_melodi_teneffus.clear()
        melodi = os.listdir("./melodies")
        mp3_list = list(filter(lambda name: bool((name[-3:]=="mp3" or name[-3:]=="wav") and (not name.startswith("ikaz") and not name.startswith("toren"))), melodi))
        self.ui.comboBox_melodi_ogrenci.addItems(mp3_list)
        self.ui.comboBox_melodi_ogretmen.addItems(mp3_list)
        self.ui.comboBox_melodi_teneffus.addItems(mp3_list)

    def melodi_degisince(self, sure):
        self.sure = sure
        self.ui.hSlider_music.setRange(0, sure)

    def zamanlayici_melodi_ses_calma_politikasi(self, position):
        if self.player_calma_politikasi == 1:
            self.player.stop()
        elif self.player_calma_politikasi == 2 and position > 3000 and self.buton_object_name in ["btn_zil_teneffus", "btn_zil_ogretmen", "btn_zil_ogrenci"]:         # 3 saniye cal
            self.player.stop()
        elif self.player_calma_politikasi == 3 and position > 5000 and self.buton_object_name in ["btn_zil_teneffus", "btn_zil_ogretmen", "btn_zil_ogrenci"]:         # 5 saniye cal
            self.player.stop()
        elif self.player_calma_politikasi == 4 and self.buton_object_name not in ["btn_zil_ogretmen"]:   # teneffüs ve öğrenci zili susturulur
            self.player.stop()
        elif self.player_calma_politikasi == 5 and self.buton_object_name not in ["btn_zil_teneffus"]:   # öğretmen ve öğrenci zili susturulur
            self.player.stop()
        elif self.player_calma_politikasi == 6 and self.buton_object_name in ["btn_zil_teneffus", "btn_zil_ogretmen", "btn_zil_ogrenci"]: # zil susar sadece tören ve siren sesleri çalar
            self.player.stop()

    def music_ilerleyince(self, position):
        self.ui.label_calma_suresi.setText(str(round(position/1000)))
        calma_suresi = self.ui.spinBox_zil_calma_suresi.value()*1000
        if position > calma_suresi and self.buton_object_name in ["btn_zil_teneffus", "btn_zil_ogrenci", "btn_zil_ogretmen"]:
            self.player.stop()
        if self.player_calma_politikasi:
            self.zamanlayici_melodi_ses_calma_politikasi(position=position)
        self.ui.hSlider_music.setSliderPosition(position)
        if not self.player.state():                             # melodi bitince yapılacaklar     state; çalınca 1, durunca 0 döndürür
            self.ui.hSlider_music.setSliderPosition(0)
            self.ui.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.ui.btn_play.setChecked(False)
            self.ui.label_calma_suresi.setText("")

    def media_ses_mute(self, state, btn_enable=True):
        try:
            self.player.setMuted( state )
            self.ui.btn_mute.setChecked( state )
            self.ui.btn_mute.setEnabled(btn_enable)
            if self.player.isMuted():
                self.ui.btn_mute.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
            else:
                self.ui.btn_mute.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk: media_ses_mute        Hata Kodu : {E}")

    def calinacak_melodi_secimi(self, sender):
        try:
            if sender == "btn_zil_ogrenci":
                self.melodi_path = "./melodies/"+self.ui.comboBox_melodi_ogrenci.currentText()
            elif sender == "btn_zil_ogretmen":
                self.melodi_path = "./melodies/"+self.ui.comboBox_melodi_ogretmen.currentText()
            elif sender == "btn_zil_teneffus":
                self.melodi_path = "./melodies/"+self.ui.comboBox_melodi_teneffus.currentText()
            elif sender == "btn_istiklal_marsi":
                self.melodi_path = "./melodies/toren_istiklal_marsi.mp3"
            elif sender == "btn_saygi_durusu":
                self.melodi_path = "./melodies/toren_saygi_durusu.mp3"
            elif sender == "btn_saygi_ve_istiklal":
                self.melodi_path = "./melodies/toren_saygi_ve_istiklal.mp3"
            elif sender == "btn_sari_ikaz":
                self.melodi_path = "./melodies/ikaz_sari.mp3"
            elif sender == "btn_kirmizi_ikaz":
                self.melodi_path = "./melodies/ikaz_kirmizi.mp3"
            elif sender == "btn_siyah_ikaz":
                self.melodi_path = "./melodies/ikaz_siyah.mp3"
            return self.melodi_path
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk: calinacak_melodi_secimi         Hata Kodu : {E}")

    def mediaPlayer_olustur_ve_melodi_ata(self, path):
        try:
            url = QtCore.QUrl.fromLocalFile(path)
            content = QMediaContent(url)
            self.player = QMediaPlayer()
            self.player.setMedia(content)
            self.player.positionChanged.connect(self.music_ilerleyince)
            self.player.durationChanged.connect(self.melodi_degisince)
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk: mediaPlayer_olustur_ve_melodi_ata            Hata Kodu : {E}")

    def play_butonu_tikla(self):
        self.buton_object_name = self.sender().objectName()
        if self.ui.btn_play.isChecked(): self.ui.btn_play.setChecked(False)
        self.ui.btn_play.click()

    def melodi_oynat_durdur(self, state):
        try:
            path = self.calinacak_melodi_secimi(self.buton_object_name)
            self.mediaPlayer_olustur_ve_melodi_ata(path)
            if state:
                self.player.setVolume(self.ui.dial_ses_seviyesi.value())
                self.player.play()
                self.player.setMuted(self.ui.btn_mute.isChecked())
                self.ui.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            else:
                self.player.stop()
                self.ui.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk: melodi_oynat_durdur            Hata Kodu : {E}")

    def ses_seviyesi_ayarla(self, deger):
        self.player.setVolume(deger)

    def anasayfayi_guncelle(self):
        try:
            kac_dk_once_zil_calsin = self.ui.spinBox_kac_dakika_once.value()*60
            currentTime = QtCore.QTime.currentTime()
            ogrenci_zili = QtCore.QTime.currentTime().addSecs(kac_dk_once_zil_calsin)     # 3 dakika sonraki zaman
            self.ui.lcdNumber.display(currentTime.toString("hh:mm:ss"))

            if currentTime.toString("ss") == "00" or ogrenci_zili.toString("ss") == "00":
                if currentTime.toString("hh:mm:ss") =="00:00:00":
                    self.ui.btn_gunun_programini_yukle.click()
                if self.bekle_5_dk < 6 : self.bekle_5_dk -= 1
                if self.bekle_5_dk == 0 :
                    self.zaman_tablosunu_vt_den_cek_doldur()
                    self.bekle_5_dk = 10
                currenDate = datetime.date.today().strftime("%d %B %Y\n%A")
                self.ui.label_bugun_tarihi.setText(currenDate)
                self.zilleri_cal(currentTime, ogrenci_zili)
                self.kalan_sure_goster()
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk: anasayfayi_guncelle            Hata Kodu : {E}")

    def kalan_sure_goster(self):
        try:
            ders_suresi     = self.ui.spinBox_ders_suresi.value()
            teneffus_suresi = self.ui.spinBox_tenefus_suresi.value()
            for index in self.ders_saat_items_dict.keys():
                if index:
                    giris_zili  = self.ders_saat_items_dict[ index ][ "giris" ].time()
                    cikis_zili  = self.ders_saat_items_dict[ index ][ "cikis" ].time()

                    simdi = datetime.datetime.now().time()
                    giris_ziline_kalan_sure = datetime.datetime(2021, 10, 25, giris_zili.hour(),giris_zili.minute(), giris_zili.second()) - datetime.datetime(2021, 10, 25, simdi.hour, simdi.minute, simdi.second)
                    cikis_ziline_kalan_sure = datetime.datetime(2021, 10, 25, cikis_zili.hour(),cikis_zili.minute(), cikis_zili.second()) - datetime.datetime(2021, 10, 25, simdi.hour, simdi.minute, simdi.second)

                    self.ui.label_zile_kalan_sure.setText("Ders dışı zaman")
                    if 0 < (giris_ziline_kalan_sure.total_seconds()/60) < (cikis_ziline_kalan_sure.total_seconds()/60):
                        sure = int(giris_ziline_kalan_sure.total_seconds()/60)
                        self.ui.progressBar_teneffuse_kalan_sure.setValue(0)
                        if sure > 60:
                            self.ui.label_zile_kalan_sure.setText(f"{index}. Dersin başlamasına\n60 dakikadan fazla zaman var")     # derslerin henüz başlamadığı zaman dilimi
                        else:
                            self.ui.label_zile_kalan_sure.setText(f"Teneffüsteyiz\n{index}. Dersin Başlamasına {sure} dk kaldı")    # teneffüs ve öğle arası zamanı
                        break
                    elif (giris_ziline_kalan_sure.total_seconds()/60) <= 0 < (cikis_ziline_kalan_sure.total_seconds()/60) :
                        sure = int(cikis_ziline_kalan_sure.total_seconds() / 60)
                        self.ui.label_zile_kalan_sure.setText(f"Şu an {index}. dersteyiz\nTeneffüse {sure} dk kaldı")               # ders zamanı
                        self.ui.progressBar_teneffuse_kalan_sure.setRange(0,ders_suresi)
                        self.ui.progressBar_teneffuse_kalan_sure.setValue(ders_suresi-sure)
                        break
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk: kalan_sure_goster            Hata Kodu : {E}")

    def zilleri_cal(self, currentTime, ogrenci_zili):
        try:
            for index in self.ders_saat_items_dict.keys():
                giris_zili  = self.ders_saat_items_dict[ index ][ "giris" ].time().toString("hh:mm:ss")
                cikis_zili  = self.ders_saat_items_dict[ index ][ "cikis" ].time().toString("hh:mm:ss")

                if giris_zili == "00:00:00":
                    break
                elif currentTime.toString("hh:mm:ss") == giris_zili  and giris_zili==cikis_zili:
                    self.ui.btn_zil_ogrenci.click()
                    break
                elif ogrenci_zili.toString("hh:mm:ss") == giris_zili and giris_zili!=cikis_zili and index!=1:
                    self.ui.btn_zil_ogrenci.click()
                    break
                elif currentTime.toString("hh:mm:ss") == giris_zili :
                    self.ui.btn_zil_ogretmen.click()
                    break
                elif currentTime.toString("hh:mm:ss") == cikis_zili :
                    self.ui.btn_zil_teneffus.click()
                    break
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk: zilleri_cal            Hata Kodu : {E}")

    def textbuttons_hide(self, state=False):
        self.ui.btn_sol_menu_gorunum.setChecked(state)
        if state:
            self.ui.btn_sol_menu_gorunum.setIcon(QtGui.QIcon("./icons/sol_menu_3.png"))
            for label in self.left_menu_labels:
                label.show()
        else:
            self.ui.btn_sol_menu_gorunum.setIcon(QtGui.QIcon("./icons/sol_menu_2.png"))
            for label in self.left_menu_labels:
                label.hide()

    def left_menu_clicked(self, state):
        try:
            sender = self.sender().objectName()
            for button in self.left_menu_buttons:
                button.setChecked(True) if sender in button.objectName() else button.setChecked(False)
            self.stackedWidget_sayfa_degistir()
        except Exception as E:
            self.ui.statusbar.showMessage(f"Fonk: left_menu_clicked            Hata Kodu : {E}")

    def stackedWidget_sayfa_degistir(self):
        if self.ui.btn_page1.isChecked():
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_1)
        elif self.ui.btn_page2.isChecked():
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_2)
        elif self.ui.btn_page3.isChecked():
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_3)
        elif self.ui.btn_page4.isChecked():
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_4)
        elif self.ui.btn_page5.isChecked():
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_5)





app = QApplication(sys.argv)
app.setStyle("Fusion")
win = Zil_app()
win.show()
sys.exit(app.exec_())


#                        pyinstaller --noconsole --onefile --windowed -i "zil.ico" Okul_zili.py
#                        pyinstaller --noconsole --windowed -i "zil.ico" Okul_zili.py





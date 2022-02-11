import sqlite3
conn    = sqlite3.connect("okul_zili.db")
cursor  = conn.cursor()



class MyDatabase:
    def __init__(self):
        gunler = ["Pazartesi", "Sali", "Carsamba", "Persembe", "Cuma", "Cumartesi", "Pazar"]
        for gun in gunler:
            self.gunluk_zaman_cizelgesi_olustur(gun)
        self.melodi_ayarlari_tablosu_olustur()
        self.zaman_ayarlari_tablosu_olustur()
        conn.commit()


    def gunluk_zaman_cizelgesi_olustur(self, gun_tablosu):
        table = f"""CREATE TABLE IF NOT EXISTS {gun_tablosu} (
        Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, Giris TEXT, Cikis TEXT) """
        cursor.execute(table)

    @classmethod
    def melodi_ayarlari_tablosu_olustur(cls):
        table = f"""CREATE TABLE IF NOT EXISTS Melodi_ayarlari (
                Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, melodi_ogrenci INTEGER, melodi_ogretmen INTEGER, 
                melodi_teneffus INTEGER, ses_seviyesi INTEGER, calma_suresi INTEGER, ogretim_tipi INTEGER, menu_etiket_goster INTEGER) """
        cursor.execute(table)

    @classmethod
    def zaman_ayarlari_tablosu_olustur(cls):
        table = f"""CREATE TABLE IF NOT EXISTS Zaman_ayarlari (Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, okul_adi TEXT,
                sabah_ders_sayisi INTEGER, ogle_ders_sayisi INTEGER, ders_suresi INTEGER, teneffus_suresi INTEGER, 
                ogle_arasi_suresi INTEGER, sabah_toplanma_saati TEXT, ogrenci_zili_kac_dk_once INTEGER, toplanma_suresi INTEGER) """
        cursor.execute(table)

    @classmethod
    def veri_giris(cls, gun, veri=[]):
        sql = f"INSERT INTO {gun} (Giris, Cikis) VALUES (?,?)"
        cursor.executemany(sql, veri)
        conn.commit()
        return bool(cursor.rowcount)

    @classmethod
    def veri_guncelle(cls, gun, veri=[]):
        sql = f"UPDATE {gun} SET Giris=?, Cikis=? WHERE Id=?"
        cursor.executemany(sql, veri)
        conn.commit()
        return bool(cursor.rowcount)

    @classmethod
    def saat_verileri_al(cls, gun):
        cursor.execute(F"SELECT * FROM {gun}")
        veriler = cursor.fetchall()
        return veriler

    @classmethod
    def melodi_ilk_ayarlar(cls, veri=[]):
        try:
            sql = "INSERT INTO Melodi_ayarlari (melodi_ogrenci, melodi_ogretmen, melodi_teneffus, ses_seviyesi, calma_suresi, ogretim_tipi, menu_etiket_goster) VALUES (?,?,?,?,?,?,?)"
            cursor.execute(sql, veri)
            conn.commit()
            return bool(cursor.rowcount)
        except Exception as E:
            print(f"fonk: ilk ayarlar        {E}")

    @classmethod
    def melodi_ayarlari_guncelle(cls, veri=[]):
        sql = "UPDATE Melodi_ayarlari SET melodi_ogrenci=?, melodi_ogretmen=?, melodi_teneffus=?, ses_seviyesi=?, calma_suresi=?, ogretim_tipi=?, menu_etiket_goster=? WHERE Id=1"
        cursor.execute(sql, veri)
        conn.commit()
        return bool(cursor.rowcount)

    @classmethod
    def melodi_ayarlari_al(cls):
        try:
            cursor.execute("SELECT melodi_ogrenci, melodi_ogretmen, melodi_teneffus, ses_seviyesi, calma_suresi, ogretim_tipi, menu_etiket_goster FROM Melodi_ayarlari")
            veriler = cursor.fetchall()
            if veriler==[]:
                veriler = [1, 1, 1, 50, 20, 1, 1]
                cls.melodi_ilk_ayarlar( veriler )
            return veriler
        except Exception as E:
            print("Fonk: ayarlari al "+ E)

    @classmethod
    def zaman_ilk_ayarlar(cls, veri=[]):
        try:
            sql = """INSERT INTO Zaman_ayarlari (okul_adi, sabah_ders_sayisi, ogle_ders_sayisi, ders_suresi, teneffus_suresi, 
                ogle_arasi_suresi, sabah_toplanma_saati, ogrenci_zili_kac_dk_once, toplanma_suresi) VALUES (?,?,?,?,?,?,?,?,?)"""
            cursor.executemany(sql, veri)
            conn.commit()
            return bool(cursor.rowcount)
        except Exception as E:
            print(f"fonk: zaman ilk ayarlar        {E}")

    @classmethod
    def zaman_ayarlari_guncelle(cls, veri=[]):
        sql = """UPDATE Zaman_ayarlari SET okul_adi=?, sabah_ders_sayisi=?, ogle_ders_sayisi=?, ders_suresi=?, teneffus_suresi=?, 
                ogle_arasi_suresi=?, sabah_toplanma_saati=?, ogrenci_zili_kac_dk_once=?, toplanma_suresi=? WHERE Id=?"""
        cursor.execute(sql, veri)
        conn.commit()
        return bool(cursor.rowcount)

    @classmethod
    def zaman_ayarlari_al(cls, Id=1):
        try:
            cursor.execute(f"SELECT * FROM Zaman_ayarlari WHERE Id={Id}")
            veriler = cursor.fetchall()
            if veriler==[]:
                veriler = [("Batman Necip Fazıl Ortaokulu", 4, 3, 40, 15, 45, "08:20:00", 3, 10),("Batman Fatih Ortaokulu", 7, 7, 40, 10, 10, "06:50:00", 2, 10)]
                cls.zaman_ilk_ayarlar( veriler )
            return veriler
        except Exception as E:
            print("Fonk: ayarlari al "+ E)





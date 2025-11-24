# Multi-Modbus Server Simülasyonu

Bu proje, Python ve PyQt6 kullanılarak geliştirilmiş, aynı anda birden fazla Modbus TCP sunucusunu (Slave cihaz) simüle etmenizi sağlayan bir araçtır. Endüstriyel otomasyon testleri, SCADA sistemleri ve PLC haberleşme denemeleri için tasarlanmıştır.
<img width="988" height="730" alt="image" src="https://github.com/user-attachments/assets/41c14266-d010-476f-9503-980a19557d91" />


## Özellikler

*   **Çoklu Sanal Cihaz:** İstenilen sayıda sanal Modbus sunucusu oluşturabilirsiniz.
*   **Ağ Tarayıcı ve Otomatik IP Tanımlama (YENİ):** Ağdaki (örneğin Wi-Fi Hotspot) boş IP adreslerini tarar ve bunları bilgisayarınıza otomatik olarak ekler.
*   **Özelleştirilebilir Ağ Ayarları:** Her sunucu için ayrı IP adresi ve Port numarası belirleyebilirsiniz.
*   **Otomatik Veri Simülasyonu:** Oluşturulan her cihaz, **Holding Register 1** (Adres 1) değerini her 5 saniyede bir otomatik olarak `0` ve `1` arasında değiştirir. Bu sayede canlı veri akışını test edebilirsiniz.
*   **Kullanıcı Dostu Arayüz:** Sunucuları eklemek, silmek, başlatmak ve durdurmak için modern bir grafik arayüz sunar.

## Kurulum

Projenin çalışması için Python kurulu olmalıdır.

1.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install -r requirements.txt
    ```

2.  **ÖNEMLİ:** Ağ özelliklerini (IP tarama ve ekleme) kullanabilmek için uygulamayı **Yönetici Olarak (Run as Administrator)** çalıştırmanız gerekir.
    ```bash
    # Terminali Yönetici olarak açın ve:
    python main.py
    ```

## Çalıştırılabilir Dosya (.exe) Oluşturma

Bu projeyi tek bir `.exe` dosyası haline getirmek için `PyInstaller` kullanabilirsiniz.

1.  **PyInstaller Yükleyin:**
    ```bash
    pip install pyinstaller
    ```

2.  **Exe Oluşturun:**
    ```bash
    pyinstaller --noconfirm --onefile --windowed --name "MultiModbusServer" main.py
    ```

3.  **Dosyayı Bulun:**
    Oluşturulan `MultiModbusServer.exe` dosyası `dist` klasörü içinde yer alacaktır. Bu dosyayı istediğiniz yere taşıyıp çalıştırabilirsiniz.

    *Not: Yönetici hakları gerektiren özellikler için .exe dosyasına sağ tıklayıp "Yönetici olarak çalıştır" demeniz gerekebilir.*

## Kullanım

### Yöntem 1: Otomatik Ağ Kurulumu (Önerilen)
Bu yöntem, ağdaki boş IP'leri bulur ve sizin için ayarlar.

1.  Uygulamayı **Yönetici** olarak başlatın.
2.  **Network Auto-Setup** bölümüne gelin.
3.  **Interface** listesinden ağ kartınızı seçin (Örn: `Wi-Fi`).
4.  **Start IP** kısmına taramanın başlayacağı IP adresini yazın (Örn: `192.168.43.50`).
5.  **Port** kısmına sunucuların çalışacağı portu girin (Örn: `5020`).
6.  **Count** kısmına kaç adet sunucu istediğinizi yazın (Örn: `5`).
7.  **Scan & Claim IPs** butonuna tıklayın.
    *   Program belirtilen aralıktaki boş IP'leri bulacak.
    *   Bu IP'leri bilgisayarınıza "Sanal IP" olarak ekleyecek.
    *   Sunucuları otomatik olarak listeye ekleyecektir.
    *   *İpucu: Bu işlemi farklı IP aralıkları veya portlar için tekrar tekrar yapabilirsiniz.*
8.  **Start All** butonuna basarak tüm sunucuları başlatın.

### Yöntem 2: Manuel Ekleme
Eğer IP adreslerini kendiniz belirlemek istiyorsanız:

1.  **Manual Add** bölümüne gelin.
2.  **IP Adresi** ve **Port** girin.
3.  **Add Server** butonuna tıklayın.
4.  **Start All** ile başlatın.

## ⚠️ PLC ve Ağ Bağlantısı Hakkında

Ağdaki gerçek bir PLC'nin bu simülasyona bağlanabilmesi için:

1.  **Doğru IP Kullanımı:** Sunucuları `127.0.0.1` yerine, ağdaki gerçek IP bloklarından (Örn: `192.168.x.x`) oluşturmalısınız. Otomatik kurulum bunu sizin için yapar.
2.  **Erişim:** PLC ve Bilgisayar aynı ağda (örneğin aynı Wi-Fi veya Switch üzerinde) olmalıdır.
3.  **Port:** Varsayılan port `5020`'dir. PLC ayarlarında bu portu kullanmayı unutmayın. Standart `502` portunu kullanmak isterseniz, port ayarını değiştirebilirsiniz.
